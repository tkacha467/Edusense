"""Assessment service module."""
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.repositories import (
    AssessmentSessionRepository,
    QuestionRepository,
    QuestionOptionRepository,
    StudentResponseRepository,
    StudentSkillRepository,
    StudentSubjectRepository,
)
from app.models import AssessmentSession, Question, QuestionOption, StudentResponse, StudentSkill
from app.core.exceptions import NotFoundException, ValidationException, ForbiddenException
from app.core.enums import AssessmentStatus


class AssessmentService:
    """Service for managing assessments, question generation, and result evaluation."""

    def __init__(self) -> None:
        """Initialize AssessmentService with necessary repositories."""
        self.session_repo = AssessmentSessionRepository()
        self.question_repo = QuestionRepository()
        self.option_repo = QuestionOptionRepository()
        self.response_repo = StudentResponseRepository()
        self.student_skill_repo = StudentSkillRepository()
        self.student_subject_repo = StudentSubjectRepository()

    def create_assessment_session(
        self,
        db: Session,
        student_id: str,
        subject_id: str,
        topic_id: str,
        title: str,
        difficulty: str,
        total_questions: int,
        time_limit: int,
        generation_method: str
    ) -> AssessmentSession:
        """
        Create a new assessment session for a student.

        Args:
            db (Session): Database session.
            student_id (str): ID of the student.
            subject_id (str): ID of the subject.
            topic_id (str): ID of the topic.
            title (str): Title of the assessment.
            difficulty (str): Assessment difficulty.
            total_questions (int): Number of questions.
            time_limit (int): Time limit in minutes.
            generation_method (str): Method used for generating questions (e.g., 'ai_generated', 'manual').

        Returns:
            AssessmentSession: The newly created session.

        Raises:
            ValidationException: If the student is not enrolled in the subject.
        """
        # Business rule: verify student is enrolled in subject
        enrollment = self.student_subject_repo.get_by_student_and_subject(
            db, student_id=student_id, subject_id=subject_id
        )
        if not enrollment:
            raise ValidationException("Student is not enrolled in this subject.")

        session_data = {
            "student_id": student_id,
            "subject_id": subject_id,
            "topic_id": topic_id,
            "title": title,
            "difficulty_level": difficulty,
            "total_questions": total_questions,
            "total_marks": float(total_questions),
            "time_limit_seconds": time_limit,
            "generation_method": generation_method,
            "status": AssessmentStatus.PENDING,
        }
        return self.session_repo.create(db, obj_in=session_data)

    def add_questions_to_session(self, db: Session, session_id: str, questions_data: List[Dict[str, Any]]) -> List[Question]:
        """
        Add generated questions and their options to a session.

        Args:
            db (Session): Database session.
            session_id (str): ID of the assessment session.
            questions_data (List[Dict[str, Any]]): List of question dictionaries.

        Returns:
            List[Question]: The list of created questions.

        Raises:
            ValidationException: If session is not pending or doesn't exist.
        """
        session = self.session_repo.get_by_id(db, session_id)
        if not session:
            raise NotFoundException(f"AssessmentSession '{session_id}' not found.")
        
        # Business rule: verify session exists and is 'pending'
        if session.status != AssessmentStatus.PENDING:
            raise ValidationException("Questions can only be added to a 'pending' assessment session.")

        created_questions = []
        for q_data in questions_data:
            options_data = q_data.pop("options", [])
            q_data["assessment_session_id"] = session_id
            
            question = self.question_repo.create(db, obj_in=q_data)
            created_questions.append(question)
            
            for opt_data in options_data:
                opt_data["question_id"] = question.id
                if "is_correct" not in opt_data or opt_data["is_correct"] is None:
                    opt_data["is_correct"] = bool(opt_data.get("option_label") == question.correct_answer)
                self.option_repo.create(db, obj_in=opt_data)
                
        return created_questions

    def start_assessment(self, db: Session, session_id: str, student_id: str) -> AssessmentSession:
        """
        Start an assessment by setting its status and started_at timestamp.

        Args:
            db (Session): Database session.
            session_id (str): ID of the assessment session.
            student_id (str): ID of the requesting student.

        Returns:
            AssessmentSession: The updated session.
        """
        session = self.session_repo.get_by_id(db, session_id)
        if not session:
            raise NotFoundException(f"AssessmentSession '{session_id}' not found.")
        if session.student_id != student_id:
            raise ForbiddenException("Assessment session does not belong to this student.")
            
        update_data = {
            "status": AssessmentStatus.IN_PROGRESS,
            "started_at": datetime.now(timezone.utc)
        }
        return self.session_repo.update(db, db_obj=session, obj_in=update_data)

    def submit_assessment(self, db: Session, session_id: str, student_id: str, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Submit and evaluate an assessment.
        Runs entirely within one transaction boundary via the injected Session.
        Fixes N+1 query issues by bulk fetching QuestionOptions and bulk processing updates.
        """
        from app.core.events import EventDispatcher

        session = self.session_repo.get_by_id(db, session_id)
        if not session:
            raise NotFoundException(f"AssessmentSession '{session_id}' not found.")
            
        if session.student_id != student_id:
            raise ForbiddenException("Assessment session does not belong to this student.")
            
        if session.status != AssessmentStatus.IN_PROGRESS:
            raise ValidationException("Can only submit an assessment that is 'in_progress'.")

        total_marks = 0
        scored_marks = 0
        correct_count = 0
        
        # 1. Bulk fetch all questions for the session
        questions = self.question_repo.get_multi_by_session(db, session_id=session_id)
        question_map = {str(q.id): q for q in questions}

        # 2. Bulk fetch all submitted options
        option_ids = []
        for r in responses:
            opt_id = r.get("selected_option_id") or r.get("option_id")
            if opt_id:
                option_ids.append(str(opt_id))
                
        # Bulk query QuestionOptions
        options = self.option_repo.get_by_ids(db, option_ids)
        option_map = {str(opt.id): opt for opt in options}
        
        # 3. Evaluate correctness and prepare bulk inserts/updates
        responses_to_insert = []
        skill_updates = {} # map skill_id -> (total_attempts_increment, correct_attempts_increment)

        for response_data in responses:
            question_id = response_data.get("question_id")
            selected_option_id = response_data.get("selected_option_id") or response_data.get("option_id")
            
            question = question_map.get(str(question_id))
            if not question:
                continue

            # Evaluate correctness using the pre-loaded option_map
            is_correct = False
            if selected_option_id:
                option = option_map.get(str(selected_option_id))
                if option and option.is_correct:
                    is_correct = True
            
            total_marks += question.marks
            if is_correct:
                scored_marks += question.marks
                correct_count += 1
                
            # Prepare StudentResponse data
            responses_to_insert.append(StudentResponse(
                assessment_session_id=session_id,
                student_id=student_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                is_correct=is_correct,
                time_taken_seconds=response_data.get("time_taken_seconds", 0)
            ))
            
            # Prepare StudentSkill update aggregation
            skill_id = getattr(question, 'skill_id', None)
            if skill_id:
                skill_id_str = str(skill_id)
                current_val = skill_updates.get(skill_id_str, (0, 0))
                skill_updates[skill_id_str] = (
                    current_val[0] + 1, 
                    current_val[1] + (1 if is_correct else 0)
                )

        # 4. Bulk insert responses
        if responses_to_insert:
            db.add_all(responses_to_insert)
            
        # 5. Process StudentSkill updates (we iterate through aggregated skills instead of per-question)
        for skill_id_str, (total_inc, correct_inc) in skill_updates.items():
            # get or create the skill (since there may not be many unique skills per test, this is much faster)
            student_skill = self.student_skill_repo.get_student_skill(db, student_id=student_id, skill_id=skill_id_str)
            if not student_skill:
                student_skill = StudentSkill(
                    student_id=student_id, 
                    skill_id=skill_id_str, 
                    total_attempts=0, 
                    correct_attempts=0, 
                    proficiency_level=0.0
                )
                db.add(student_skill)
                db.flush() # Need flush to ensure it has an ID/state for the update below
                
            student_skill.total_attempts += total_inc
            student_skill.correct_attempts += correct_inc
            student_skill.proficiency_level = student_skill.correct_attempts / student_skill.total_attempts
            student_skill.last_practiced_at = datetime.now(timezone.utc)

        percentage = (scored_marks / total_marks * 100) if total_marks > 0 else 0.0
        
        # 6. Complete session
        session.status = AssessmentStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        session.score = scored_marks
        
        # Note: the db session will be committed by the router dependency.
        db.flush() 

        return {
            "total_questions": len(questions),
            "correct_answers": correct_count,
            "total_marks": total_marks,
            "scored_marks": scored_marks,
            "percentage": percentage,
            "skill_updates": list(skill_updates.keys())
        }

    def get_assessment_history(self, db: Session, student_id: str, page: int = 1, page_size: int = 20) -> Tuple[List[AssessmentSession], int]:
        """
        Retrieve a student's assessment history.

        Args:
            db (Session): Database session.
            student_id (str): ID of the student.
            page (int): Page number.
            page_size (int): Items per page.

        Returns:
            Tuple[List[AssessmentSession], int]: History and total count.
        """
        skip = (page - 1) * page_size
        return self.session_repo.get_history_by_student(db, student_id=student_id, skip=skip, limit=page_size)

    def get_assessment_detail(self, db: Session, session_id: str, student_id: str = None) -> AssessmentSession:
        """
        Retrieve a full assessment session including its questions and options.

        Args:
            db (Session): Database session.
            session_id (str): ID of the assessment session.
            student_id (str, optional): ID of the requesting student for ownership validation.

        Returns:
            AssessmentSession: The assessment session with loaded relationships.
        """
        session = self.session_repo.get_with_questions(db, id=session_id)
        if not session:
            raise NotFoundException(f"AssessmentSession '{session_id}' not found.")
        if student_id and session.student_id != student_id:
            raise ForbiddenException("Assessment session does not belong to this student.")
        return session

    def abandon_assessment(self, db: Session, session_id: str, student_id: str) -> AssessmentSession:
        """
        Abandon an in-progress assessment.

        Args:
            db (Session): Database session.
            session_id (str): ID of the assessment session.
            student_id (str): ID of the requesting student.

        Returns:
            AssessmentSession: The updated session.
        """
        session = self.session_repo.get_by_id(db, session_id)
        if not session:
            raise NotFoundException(f"AssessmentSession '{session_id}' not found.")
            
        if session.student_id != student_id:
            raise ForbiddenException("Assessment session does not belong to this student.")
            
        return self.session_repo.update(
            db, 
            db_obj=session, 
            obj_in={"status": AssessmentStatus.ABANDONED, "completed_at": datetime.now(timezone.utc)}
        )
