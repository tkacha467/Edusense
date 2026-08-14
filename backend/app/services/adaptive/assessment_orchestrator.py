import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc

from app.core.enums import AssessmentStatus, AssessmentDifficulty, QuestionDifficulty
from app.core.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.models import AssessmentSession, Question, QuestionOption, StudentResponse, StudentProfile
from app.models.learning import Skill, TopicSkill, Topic, Subject
from app.repositories import (
    AssessmentSessionRepository,
    QuestionRepository,
    QuestionOptionRepository,
    StudentSkillRepository,
    KnowledgeProfileRepository
)
from app.ai.question_generation.generator import AIQuestionGenerator
from app.services.knowledge import KnowledgeDecayService
from app.services.adaptive.planner import RevisionPlanner
from app.services.adaptive.timeline import LearningTimelineService

logger = logging.getLogger(__name__)


class SkillSelectionService:
    """Ranks skills for adaptive assessment based on mastery, forget probability, and history."""

    def __init__(self) -> None:
        self.kp_repo = KnowledgeProfileRepository()
        self.skill_repo = StudentSkillRepository()

    def get_ranked_skills(self, db: Session, student_id: str, subject_id: str) -> List[str]:
        # Query existing knowledge profiles
        profiles = self.kp_repo.get_by_student(db, student_id=student_id)
        
        # Rank by forget probability descending (higher risk first)
        profiles.sort(key=lambda p: -(p.forget_probability or 0.0))
        
        ranked_ids = [p.skill_id for p in profiles]
        
        # If no profiles, fetch default skills for the subject
        if not ranked_ids:
            skills = db.query(Skill).all()
            ranked_ids = [str(s.id) for s in skills]
            
        return ranked_ids


class DifficultyEngine:
    """Calculates active target difficulty based on student session responses accuracy."""

    def calculate_next_difficulty(self, db: Session, session_id: str) -> str:
        # Fetch responses in this session
        stmt = select(StudentResponse).where(StudentResponse.assessment_session_id == session_id).order_by(desc(StudentResponse.created_at))
        responses = list(db.execute(stmt).scalars().all())

        if not responses:
            return "MEDIUM"  # Default starting difficulty

        # Check the correctness of the last response
        last_response = responses[0]
        if last_response.is_correct:
            # Scale up difficulty
            return "HARD"
        else:
            # Scale down difficulty
            return "EASY"


class AssessmentOrchestrator:
    """ ब्रेन: Coordinates the dynamic assessment execution flow, difficulty adjustment, and grading. """

    def __init__(self) -> None:
        self.session_repo = AssessmentSessionRepository()
        self.question_repo = QuestionRepository()
        self.option_repo = QuestionOptionRepository()
        self.skill_selector = SkillSelectionService()
        self.diff_engine = DifficultyEngine()
        self.kd_service = KnowledgeDecayService()
        self.planner = RevisionPlanner()
        self.timeline_service = LearningTimelineService()

    def start_adaptive_session(
        self,
        db: Session,
        student_id: str,
        subject_id: str,
        title: str,
        total_questions: int = 5,
        time_limit: int = 900
    ) -> AssessmentSession:
        """Initializes a new adaptive assessment session."""
        session_data = {
            "student_id": student_id,
            "subject_id": subject_id,
            "title": title,
            "difficulty_level": AssessmentDifficulty.ADAPTIVE,
            "total_questions": total_questions,
            "time_limit_seconds": time_limit,
            "status": AssessmentStatus.IN_PROGRESS,
            "started_at": datetime.now(timezone.utc),
            "generation_method": "ai"
        }
        session = self.session_repo.create(db, obj_in=session_data)
        logger.info(f"Initialized adaptive session {session.id} for student {student_id}")
        return session

    async def get_or_generate_next_question(
        self,
        db: Session,
        session_id: str,
        student_id: str
    ) -> Optional[Tuple[Question, int]]:
        """Determines the next skill & difficulty, and retrieves/generates a question."""
        session = self.session_repo.get_by_id(db, session_id)
        if not session:
            raise NotFoundException("AssessmentSession not found.")
            
        if session.status != AssessmentStatus.IN_PROGRESS:
            return None

        # Check total questions answered
        stmt_count = select(StudentResponse).where(StudentResponse.assessment_session_id == session_id)
        answered_count = len(list(db.execute(stmt_count).scalars().all()))

        if answered_count >= session.total_questions:
            return None # Finished

        # Find skill to test (rank first candidate)
        skills = self.skill_selector.get_ranked_skills(db, student_id, session.subject_id)
        target_skill_id = skills[0] if skills else "adca46c6-d4c4-4467-9904-a4b69919459d"

        # Determine target difficulty
        target_diff = self.diff_engine.calculate_next_difficulty(db, session_id)

        # Check if we already have an un-answered generated question in this session
        stmt_unanswered = select(Question).where(
            Question.assessment_session_id == session_id
        ).order_by(asc(Question.order_index))
        all_session_qs = list(db.execute(stmt_unanswered).scalars().all())
        
        if len(all_session_qs) > answered_count:
            # We already have an unanswered question queued, return it
            return all_session_qs[answered_count], answered_count + 1

        # Otherwise, dynamically generate a new question for this skill and difficulty!
        skill_obj = db.query(Skill).filter(Skill.id == target_skill_id).first()
        skill_name = skill_obj.name if skill_obj else "General Knowledge"
        subject_obj = db.query(Subject).filter(Subject.id == session.subject_id).first()
        subject_name = subject_obj.name if subject_obj else "Computer Science"

        ai_generator = AIQuestionGenerator()
        logger.info(f"Generating adaptive question for skill {skill_name} and difficulty {target_diff}")
        generated_dtos = await ai_generator.generate_questions(
            subject_name=subject_name,
            topic_name=skill_name,
            difficulty=target_diff.lower(),
            count=1
        )

        dto = generated_dtos[0]
        question_data = {
            "assessment_session_id": session_id,
            "skill_id": target_skill_id,
            "question_text": dto.get("question_text"),
            "question_type": dto.get("question_type", "MCQ").upper(),
            "difficulty_level": target_diff,
            "marks": dto.get("marks", 1.0),
            "correct_answer": dto.get("correct_answer"),
            "explanation": dto.get("explanation"),
            "hint": dto.get("hint"),
            "order_index": answered_count
        }

        # Save question and options
        question = self.question_repo.create(db, obj_in=question_data)
        for opt in dto.get("options", []):
            self.option_repo.create(db, obj_in={
                "question_id": question.id,
                "option_label": opt.get("option_label"),
                "option_text": opt.get("option_text"),
                "is_correct": opt.get("option_label") == dto.get("correct_answer"),
                "order_index": opt.get("order_index", 0)
            })

        db.flush()
        return question, answered_count + 1

    def submit_single_answer(
        self,
        db: Session,
        session_id: str,
        student_id: str,
        question_id: str,
        selected_option_id: str,
        time_taken_seconds: int = 15
    ) -> Dict[str, Any]:
        """Evaluates one answer in real-time, updates database, and returns correctness."""
        session = self.session_repo.get_by_id(db, session_id)
        if not session or session.status != AssessmentStatus.IN_PROGRESS:
            raise ValidationException("Session is not in progress.")

        # Verify question ownership
        question = self.question_repo.get_by_id(db, question_id)
        if not question or str(question.assessment_session_id) != session_id:
            raise NotFoundException("Question not found in this session.")

        # Prevent double submit on same question
        stmt_exists = select(StudentResponse).where(
            StudentResponse.assessment_session_id == session_id,
            StudentResponse.question_id == question_id
        )
        if db.execute(stmt_exists).scalar_one_or_none():
            raise ValidationException("Question already answered.")

        # Evaluate correctness
        option = self.option_repo.get_by_id(db, selected_option_id)
        is_correct = bool(option and option.is_correct)

        # Store response row
        response = StudentResponse(
            assessment_session_id=session_id,
            student_id=student_id,
            question_id=question_id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds
        )
        db.add(response)
        db.flush()

        # Incremental StudentSkill updates
        skill_id = question.skill_id
        if skill_id:
            from app.models import StudentSkill
            student_skill = db.query(StudentSkill).filter_by(student_id=student_id, skill_id=skill_id).first()
            if not student_skill:
                student_skill = StudentSkill(
                    student_id=student_id,
                    skill_id=skill_id,
                    total_attempts=0,
                    correct_attempts=0,
                    proficiency_level=0.0
                )
                db.add(student_skill)
                db.flush()

            student_skill.total_attempts += 1
            if is_correct:
                student_skill.correct_attempts += 1
            student_skill.proficiency_level = student_skill.correct_attempts / student_skill.total_attempts
            student_skill.last_practiced_at = datetime.now(timezone.utc)
            db.flush()

            # Run prediction pipeline synchronously
            self.kd_service.run_prediction_pipeline(db=db, student_id=student_id, skill_id=str(skill_id))

        return {
            "is_correct": is_correct,
            "correct_option_id": db.query(QuestionOption).filter_by(question_id=question_id, is_correct=True).first().id
        }

    def finish_session(self, db: Session, session_id: str, student_id: str) -> Dict[str, Any]:
        """Concludes the assessment session and scores the results."""
        session = self.session_repo.get_by_id(db, session_id)
        if not session or session.status != AssessmentStatus.IN_PROGRESS:
            raise ValidationException("Session is not in progress.")

        # Sum results
        stmt_res = select(StudentResponse).where(StudentResponse.assessment_session_id == session_id)
        responses = list(db.execute(stmt_res).scalars().all())

        total_questions = len(responses)
        correct_count = sum(1 for r in responses if r.is_correct)
        total_marks = sum(1.0 for r in responses)
        scored_marks = sum(1.0 for r in responses if r.is_correct)
        percentage = (scored_marks / total_marks * 100) if total_marks > 0 else 0.0

        session.status = AssessmentStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        session.scored_marks = scored_marks
        session.total_marks = total_marks
        session.percentage = percentage
        db.flush()

        # Update revision plan
        student_profile = db.query(StudentProfile).filter_by(id=student_id).first()
        if student_profile:
            self.planner.generate_adaptive_study_plan(db=db, student_profile=student_profile)
            self.timeline_service.record_event(
                db=db,
                user_id=student_profile.user_id,
                event_name="Adaptive Assessment Completed",
                entity_type="AssessmentSession",
                entity_id=session_id,
                details=f"Concluded adaptive test with accuracy {int(percentage)}%."
            )

        return {
            "assessment_session_id": session_id,
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "scored_marks": scored_marks,
            "total_marks": total_marks,
            "percentage": percentage,
            "time_taken_seconds": sum(r.time_taken_seconds for r in responses)
        }
