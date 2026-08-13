"""Assessment repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc
from datetime import datetime, timezone
from app.repositories.base import BaseRepository
from app.models import AssessmentSession, Question, QuestionOption, StudentResponse
from app.core.enums import AssessmentStatus
from typing import Any

class AssessmentSessionRepository(BaseRepository[AssessmentSession]):
    """Repository for AssessmentSession model."""
    
    def __init__(self) -> None:
        """Initialize with AssessmentSession model."""
        super().__init__(AssessmentSession)

    def get_by_student(self, db: Session, student_id: str, skip: int = 0, limit: int = 100) -> list[AssessmentSession]:
        """Get assessment sessions by student."""
        stmt = select(AssessmentSession).where(AssessmentSession.student_id == student_id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_student_and_subject(self, db: Session, student_id: str, subject_id: str, skip: int = 0, limit: int = 100) -> list[AssessmentSession]:
        """Get assessment sessions by student and subject."""
        stmt = select(AssessmentSession).where(
            AssessmentSession.student_id == student_id,
            AssessmentSession.subject_id == subject_id
        ).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_status(self, db: Session, status: AssessmentStatus, skip: int = 0, limit: int = 100) -> list[AssessmentSession]:
        """Get assessment sessions by status."""
        stmt = select(AssessmentSession).where(AssessmentSession.status == status).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_recent_by_student(self, db: Session, student_id: str, limit: int = 5) -> list[AssessmentSession]:
        """Get recent assessment sessions by student."""
        stmt = select(AssessmentSession).where(AssessmentSession.student_id == student_id).order_by(desc(AssessmentSession.created_at)).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def complete_session(self, db: Session, session_id: str, scored_marks: float, total_marks: float, time_taken: int) -> AssessmentSession | None:
        """Complete an assessment session."""
        session = self.get_by_id(db, session_id)
        if session:
            session.scored_marks = scored_marks
            session.total_marks = total_marks
            session.percentage = (scored_marks / total_marks * 100) if total_marks > 0 else 0.0
            session.time_taken = time_taken
            session.status = AssessmentStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)
            db.flush()
        return session


    def get_history_by_student(self, db: Session, student_id: str, skip: int = 0, limit: int = 20) -> tuple[list[AssessmentSession], int]:
        """Get paginated assessment session history for a student."""
        total_stmt = select(AssessmentSession).where(AssessmentSession.student_id == student_id)
        total = len(list(db.execute(total_stmt).scalars().all()))
        stmt = total_stmt.order_by(desc(AssessmentSession.created_at)).offset(skip).limit(limit)
        items = list(db.execute(stmt).scalars().all())
        return items, total

    def get_with_questions(self, db: Session, id: str) -> AssessmentSession | None:
        """Get assessment session by ID."""
        return self.get_by_id(db, id)


class QuestionRepository(BaseRepository[Question]):
    """Repository for Question model."""
    
    def __init__(self) -> None:
        """Initialize with Question model."""
        super().__init__(Question)

    def get_by_assessment(self, db: Session, session_id: str) -> list[Question]:
        """Get questions by assessment session ordered by index."""
        stmt = select(Question).where(Question.assessment_session_id == session_id).order_by(asc(Question.order_index))
        return list(db.execute(stmt).scalars().all())

    get_multi_by_session = get_by_assessment
    get_by_session = get_by_assessment

    def get_by_topic(self, db: Session, topic_id: str, skip: int = 0, limit: int = 100) -> list[Question]:
        """Get questions by topic."""
        stmt = select(Question).where(Question.topic_id == topic_id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_skill(self, db: Session, skill_id: str, skip: int = 0, limit: int = 100) -> list[Question]:
        """Get questions by skill."""
        stmt = select(Question).where(Question.skill_id == skill_id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def bulk_create_with_options(self, db: Session, questions_data: list[dict[str, Any]]) -> list[Question]:
        """Create questions and their options in one transaction."""
        created_questions = []
        for q_data in questions_data:
            options_data = q_data.pop('options', [])
            question = self.model(**q_data)
            db.add(question)
            db.flush()
            for opt_data in options_data:
                option = QuestionOption(question_id=question.id, **opt_data)
                db.add(option)
            created_questions.append(question)
        db.flush()
        return created_questions


class QuestionOptionRepository(BaseRepository[QuestionOption]):
    """Repository for QuestionOption model."""
    
    def __init__(self) -> None:
        """Initialize with QuestionOption model."""
        super().__init__(QuestionOption)

    def get_by_question(self, db: Session, question_id: str) -> list[QuestionOption]:
        """Get options by question ID ordered by index."""
        stmt = select(QuestionOption).where(QuestionOption.question_id == question_id).order_by(asc(QuestionOption.order_index))
        return list(db.execute(stmt).scalars().all())

    def get_by_ids(self, db: Session, option_ids: list[str]) -> list[QuestionOption]:
        """Get options by a list of IDs."""
        if not option_ids:
            return []
        stmt = select(QuestionOption).where(QuestionOption.id.in_(option_ids))
        return list(db.execute(stmt).scalars().all())

    def get_correct_option(self, db: Session, question_id: str) -> QuestionOption | None:
        """Get correct option for a question."""
        stmt = select(QuestionOption).where(QuestionOption.question_id == question_id, QuestionOption.is_correct == True)
        return db.execute(stmt).scalar_one_or_none()


class StudentResponseRepository(BaseRepository[StudentResponse]):
    """Repository for StudentResponse model."""
    
    def __init__(self) -> None:
        """Initialize with StudentResponse model."""
        super().__init__(StudentResponse)

    def get_by_session(self, db: Session, session_id: str) -> list[StudentResponse]:
        """Get responses for a session."""
        stmt = select(StudentResponse).where(StudentResponse.assessment_session_id == session_id)
        return list(db.execute(stmt).scalars().all())

    def get_by_student(self, db: Session, student_id: str, skip: int = 0, limit: int = 100) -> list[StudentResponse]:
        """Get responses by student."""
        stmt = select(StudentResponse).where(StudentResponse.student_id == student_id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_question(self, db: Session, question_id: str) -> list[StudentResponse]:
        """Get responses for a question."""
        stmt = select(StudentResponse).where(StudentResponse.question_id == question_id)
        return list(db.execute(stmt).scalars().all())

    def get_session_results(self, db: Session, session_id: str) -> dict[str, Any]:
        """Get aggregated results for an assessment session."""
        responses = self.get_by_session(db, session_id)
        total = len(responses)
        correct = sum(1 for r in responses if r.is_correct)
        incorrect = total - correct
        percentage = (correct / total * 100) if total > 0 else 0.0
        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "percentage": percentage
        }
