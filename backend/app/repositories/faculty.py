"""Faculty repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models import FacultyProfile

class FacultyProfileRepository(BaseRepository[FacultyProfile]):
    """Repository for FacultyProfile model."""
    
    def __init__(self) -> None:
        """Initialize with FacultyProfile model."""
        super().__init__(FacultyProfile)

    def get_by_user_id(self, db: Session, user_id: str) -> FacultyProfile | None:
        """Get faculty profile by user ID."""
        stmt = select(FacultyProfile).where(FacultyProfile.user_id == user_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_department(self, db: Session, department: str, skip: int = 0, limit: int = 100) -> list[FacultyProfile]:
        """Get faculty profiles by department."""
        stmt = select(FacultyProfile).where(FacultyProfile.department == department).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_specialization(self, db: Session, specialization: str, skip: int = 0, limit: int = 100) -> list[FacultyProfile]:
        """Get faculty profiles by specialization."""
        stmt = select(FacultyProfile).where(FacultyProfile.specialization == specialization).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())
