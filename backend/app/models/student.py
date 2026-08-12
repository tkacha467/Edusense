"""Student models."""
from typing import Optional, List

from sqlalchemy import String, Integer, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, GUID

class StudentProfile(BaseModel):
    """Student profile model."""
    __tablename__ = 'student_profiles'

    user_id: Mapped[str] = mapped_column(GUID(), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    institution: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    semester: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    enrollment_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    learning_goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), nullable=False, default='en')
    onboarding_completed: Mapped[bool] = mapped_column(nullable=False, default=False)

    __table_args__ = (
        CheckConstraint('semester BETWEEN 1 AND 12', name='check_semester_range'),
    )

    user: Mapped["User"] = relationship("User", back_populates="student_profile")
    subjects: Mapped[List["StudentSubject"]] = relationship("StudentSubject", back_populates="student")
    skills: Mapped[List["StudentSkill"]] = relationship("StudentSkill", back_populates="student")
    learning_preference: Mapped[Optional["LearningPreference"]] = relationship(
        "LearningPreference", uselist=False, back_populates="student", cascade="all, delete-orphan"
    )
    assessment_sessions: Mapped[List["AssessmentSession"]] = relationship(
        "AssessmentSession", back_populates="student", cascade="all, delete-orphan"
    )
    responses: Mapped[List["StudentResponse"]] = relationship("StudentResponse", back_populates="student")
    knowledge_profiles: Mapped[List["KnowledgeProfile"]] = relationship(
        "KnowledgeProfile", back_populates="student", cascade="all, delete-orphan"
    )
    prediction_histories: Mapped[List["PredictionHistory"]] = relationship("PredictionHistory", back_populates="student")
    study_plans: Mapped[List["StudyPlan"]] = relationship(
        "StudyPlan", back_populates="student", cascade="all, delete-orphan"
    )
    activities: Mapped[List["StudentActivity"]] = relationship("StudentActivity", back_populates="student")

    def __repr__(self) -> str:
        """String representation."""
        return f"<StudentProfile(id={self.id}, user_id={self.user_id})>"
