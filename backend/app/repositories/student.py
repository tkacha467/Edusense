"""Student repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models import StudentProfile

class StudentProfileRepository(BaseRepository[StudentProfile]):
    """Repository for StudentProfile model."""
    
    def __init__(self) -> None:
        """Initialize with StudentProfile model."""
        super().__init__(StudentProfile)

    def get_by_user_id(self, db: Session, user_id: str) -> StudentProfile | None:
        """Get student profile by user ID."""
        stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_institution(self, db: Session, institution: str, skip: int = 0, limit: int = 100) -> list[StudentProfile]:
        """Get student profiles by institution."""
        stmt = select(StudentProfile).where(StudentProfile.institution == institution).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_incomplete_onboarding(self, db: Session, skip: int = 0, limit: int = 100) -> list[StudentProfile]:
        """Get student profiles with incomplete onboarding."""
        stmt = select(StudentProfile).where(StudentProfile.onboarding_completed.is_(False)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def complete_onboarding(self, db: Session, student_id: str) -> StudentProfile | None:
        """Mark onboarding as complete for a student."""
        profile = self.get_by_id(db, student_id)
        if profile:
            profile.onboarding_completed = True
            db.flush()
        return profile

    def search(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> list[StudentProfile]:
        """Search student profiles by institution or department."""
        stmt = select(StudentProfile).where(
            (StudentProfile.institution.ilike(f"%{query}%")) |
            (StudentProfile.department.ilike(f"%{query}%"))
        ).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[StudentProfile]:
        """Get all student profiles."""
        return super().get_all(db, skip=skip, limit=limit)
