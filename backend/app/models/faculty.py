"""Faculty models."""
from typing import Optional, List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, GUID

class FacultyProfile(BaseModel):
    """Faculty profile model."""
    __tablename__ = 'faculty_profiles'

    user_id: Mapped[str] = mapped_column(GUID(), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    institution: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="faculty_profile")
    subjects: Mapped[List["FacultySubject"]] = relationship("FacultySubject", back_populates="faculty")

    def __repr__(self) -> str:
        """String representation."""
        return f"<FacultyProfile(id={self.id}, user_id={self.user_id})>"
