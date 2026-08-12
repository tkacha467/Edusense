"""Analytics repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import date, timedelta
from app.repositories.base import BaseRepository
from app.models import StudentActivity
from app.core.enums import ActivityType

class StudentActivityRepository(BaseRepository[StudentActivity]):
    """Repository for StudentActivity model."""
    
    def __init__(self) -> None:
        """Initialize with StudentActivity model."""
        super().__init__(StudentActivity)

    def get_by_student(self, db: Session, student_id: str, skip: int = 0, limit: int = 100) -> list[StudentActivity]:
        """Get activities by student."""
        stmt = select(StudentActivity).where(StudentActivity.student_id == student_id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_date_range(self, db: Session, student_id: str, start_date: date, end_date: date) -> list[StudentActivity]:
        """Get activities in a date range."""
        stmt = select(StudentActivity).where(
            StudentActivity.student_id == student_id,
            StudentActivity.activity_date >= start_date,
            StudentActivity.activity_date <= end_date
        )
        return list(db.execute(stmt).scalars().all())

    def get_by_type(self, db: Session, student_id: str, activity_type: ActivityType) -> list[StudentActivity]:
        """Get activities by type."""
        stmt = select(StudentActivity).where(
            StudentActivity.student_id == student_id,
            StudentActivity.activity_type == activity_type
        )
        return list(db.execute(stmt).scalars().all())

    def get_weekly_summary(self, db: Session, student_id: str) -> dict[str, int]:
        """Get summary of activities for the last 7 days grouped by type."""
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        stmt = select(StudentActivity.activity_type, func.count()).where(
            StudentActivity.student_id == student_id,
            StudentActivity.activity_date >= start_date,
            StudentActivity.activity_date <= end_date
        ).group_by(StudentActivity.activity_type)
        
        results = db.execute(stmt).all()
        return {str(k): v for k, v in results}

    def get_daily_count(self, db: Session, student_id: str, target_date: date) -> int:
        """Get count of activities on a specific day."""
        stmt = select(func.count()).select_from(StudentActivity).where(
            StudentActivity.student_id == student_id,
            StudentActivity.activity_date == target_date
        )
        return db.execute(stmt).scalar_one()

    def log_activity(
        self,
        db: Session,
        student_id: str,
        activity_type: ActivityType,
        entity_type: str | None = None,
        entity_id: str | None = None,
        subject_id: str | None = None,
        metadata_str: str | None = None,
        duration_seconds: int | None = None
    ) -> StudentActivity:
        """Log a new student activity."""
        activity = self.model(
            student_id=student_id,
            activity_type=activity_type,
            activity_date=date.today(),
            entity_type=entity_type,
            entity_id=entity_id,
            subject_id=subject_id,
            metadata_=metadata_str,
            duration_seconds=duration_seconds
        )
        db.add(activity)
        db.flush()
        return activity
