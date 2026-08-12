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
from app.core.exceptions import NotFoundException, ValidationException
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
                self.option_repo.create(db, obj_in=opt_data)
                
        return created_questions

    def start_assessment(self, db: Session, session_id: str) -> AssessmentSession:
        """
        Start an assessment by setting its status and started_at timestamp.

        Args:
            db (Session): Database session.
            session_id (str): ID of the assessment session.

        Returns:
            AssessmentSession: The updated session.
        """
        session = self.session_repo.get_by_id(db, session_id)
        if not session:
            raise NotFoundException(f"AssessmentSession '{session_id}' not found.")
            
        update_data = {
            "status": AssessmentStatus.IN_PROGRESS,
            "started_at": datetime.now(timezone.utc)
        }
        return self.session_repo.update(db, db_obj=session, obj_in=update_data)

    def submit_assessment(self, db: Session, session_id: str, student_id: str, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Submit and evaluate an assessment.

        Args:
            db (Session): Database session.
            session_id (str): ID of the assessment session.
            student_id (str): ID of the student.
            responses (List[Dict[str, Any]]): List of responses containing question_id, option_id, etc.

        Returns:
            Dict[str, Any]: Evaluation result containing total, correct, scored_marks, percentage.
        """
        session = self.session_repo.get_by_id(db, session_id)
        if not session:
            raise NotFoundException(f"AssessmentSession '{session_id}' not found.")
            
        if session.status != AssessmentStatus.IN_PROGRESS:
            raise ValidationException("Can only submit an assessment that is 'in_progress'.")

        total_marks = 0
        scored_marks = 0
        correct_count = 0
        
        # We need all questions for the session to score
        questions = self.question_repo.get_multi_by_session(db, session_id=session_id)
        question_map = {str(q.id): q for q in questions}

        for response_data in responses:
            question_id = response_data.get("question_id")
            selected_option_id = response_data.get("selected_option_id") or response_data.get("option_id")
            
            question = question_map.get(str(question_id))
            if not question:
                continue

            # Evaluate correctness
            is_correct = False
            if selected_option_id:
                option = self.option_repo.get_by_id(db, selected_option_id)
                if option and option.is_correct:
                    is_correct = True
            
            total_marks += question.marks
            if is_correct:
                scored_marks += question.marks
                correct_count += 1
                
            # Create StudentResponse
            resp_obj_in = {
                "assessment_session_id": session_id,
                "student_id": student_id,
                "question_id": question_id,
                "selected_option_id": selected_option_id,
                "is_correct": is_correct,
                "time_taken_seconds": response_data.get("time_taken_seconds", 0)
            }
            self.response_repo.create(db, obj_in=resp_obj_in)
            
            # Update StudentSkill if a skill_id is associated with the question
            # (Assuming questions are linked to skills for granular tracking)
            skill_id = getattr(question, 'skill_id', None)
            if skill_id:
                self.student_skill_repo.update_proficiency(db, student_id=student_id, skill_id=skill_id, is_correct=is_correct)

        percentage = (scored_marks / total_marks * 100) if total_marks > 0 else 0.0
        
        # Complete session
        update_data = {
            "status": AssessmentStatus.COMPLETED,
            "completed_at": datetime.now(timezone.utc),
            "score": scored_marks
        }
        self.session_repo.update(db, db_obj=session, obj_in=update_data)
        
        return {
            "total_questions": len(questions),
            "correct_answers": correct_count,
            "total_marks": total_marks,
            "scored_marks": scored_marks,
            "percentage": percentage
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

    def get_assessment_detail(self, db: Session, session_id: str) -> AssessmentSession:
        """
        Retrieve a full assessment session including its questions and options.

        Args:
            db (Session): Database session.
            session_id (str): ID of the assessment session.

        Returns:
            AssessmentSession: The assessment session with loaded relationships.
        """
        session = self.session_repo.get_with_questions(db, id=session_id)
        if not session:
            raise NotFoundException(f"AssessmentSession '{session_id}' not found.")
        return session

    def abandon_assessment(self, db: Session, session_id: str) -> AssessmentSession:
        """
        Abandon an in-progress assessment.

        Args:
            db (Session): Database session.
            session_id (str): ID of the assessment session.

        Returns:
            AssessmentSession: The updated session.
        """
        session = self.session_repo.get_by_id(db, session_id)
        if not session:
            raise NotFoundException(f"AssessmentSession '{session_id}' not found.")
            
        return self.session_repo.update(
            db, 
            db_obj=session, 
            obj_in={"status": AssessmentStatus.ABANDONED, "completed_at": datetime.now(timezone.utc)}
        )
