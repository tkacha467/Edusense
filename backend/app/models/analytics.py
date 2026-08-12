"""Analytics models."""
from datetime import date
from typing import Optional

from sqlalchemy import String, Integer, Text, Date, ForeignKey, Index, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, GUID
from app.core.enums import ActivityType

class StudentActivity(BaseModel):
    """Student activity model."""
    __tablename__ = 'student_activities'

    student_id: Mapped[str] = mapped_column(GUID(), ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    activity_type: Mapped[ActivityType] = mapped_column(SAEnum(ActivityType), nullable=False, index=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    entity_id: Mapped[Optional[str]] = mapped_column(GUID(), nullable=True)
    subject_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    activity_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    __table_args__ = (
        Index('ix_student_activity_date', 'student_id', 'activity_date'),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="activities")
    subject: Mapped[Optional["Subject"]] = relationship("Subject", back_populates="activities")

    def __repr__(self) -> str:
        """String representation."""
        return f"<StudentActivity(id={self.id}, student_id={self.student_id}, type='{self.activity_type}')>"
