"""Recommendation models."""
from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Text, Date, DateTime, ForeignKey, CheckConstraint, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, GUID
from app.core.enums import StudyPlanType, StudyPlanStatus, TaskType, TaskPriority, TaskStatus

class StudyPlan(BaseModel):
    """Study plan model."""
    __tablename__ = 'study_plans'

    student_id: Mapped[str] = mapped_column(GUID(), ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    subject_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan_type: Mapped[StudyPlanType] = mapped_column(SAEnum(StudyPlanType), nullable=False)
    status: Mapped[StudyPlanStatus] = mapped_column(SAEnum(StudyPlanStatus), nullable=False, default=StudyPlanStatus.ACTIVE)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="study_plans")
    subject: Mapped[Optional["Subject"]] = relationship("Subject", back_populates="study_plans")
    tasks: Mapped[List["StudyTask"]] = relationship("StudyTask", back_populates="study_plan", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<StudyPlan(id={self.id}, student_id={self.student_id}, title='{self.title}')>"

class StudyTask(BaseModel):
    """Study task model."""
    __tablename__ = 'study_tasks'

    study_plan_id: Mapped[str] = mapped_column(GUID(), ForeignKey('study_plans.id', ondelete='CASCADE'), nullable=False)
    topic_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('topics.id', ondelete='SET NULL'), nullable=True)
    skill_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('skills.id', ondelete='SET NULL'), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    task_type: Mapped[TaskType] = mapped_column(SAEnum(TaskType), nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(SAEnum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint('estimated_minutes > 0', name='check_est_mins'),
    )

    study_plan: Mapped["StudyPlan"] = relationship("StudyPlan", back_populates="tasks")
    topic: Mapped[Optional["Topic"]] = relationship("Topic", back_populates="study_tasks")
    skill: Mapped[Optional["Skill"]] = relationship("Skill", back_populates="study_tasks")

    def __repr__(self) -> str:
        """String representation."""
        return f"<StudyTask(id={self.id}, study_plan_id={self.study_plan_id}, title='{self.title}')>"
