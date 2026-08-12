"""Knowledge models."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Integer, Float, Boolean, DateTime, ForeignKey, Index, UniqueConstraint, CheckConstraint, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import BaseModel, GUID
from app.core.enums import PredictionTrigger

class KnowledgeProfile(BaseModel):
    """Knowledge profile model."""
    __tablename__ = 'knowledge_profiles'

    student_id: Mapped[str] = mapped_column(GUID(), ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    skill_id: Mapped[str] = mapped_column(GUID(), ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    interaction_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    past_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    past_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    past_accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rolling_accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    mastered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    forget_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    retention_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_predicted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_interaction_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('student_id', 'skill_id', name='uq_student_skill_knowledge'),
        CheckConstraint('forget_probability >= 0.0 AND forget_probability <= 1.0', name='check_forget_prob'),
        CheckConstraint('retention_score >= 0.0 AND retention_score <= 1.0', name='check_retention_score'),
        CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='check_confidence_score'),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="knowledge_profiles")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="knowledge_profiles")
    prediction_histories: Mapped[List["PredictionHistory"]] = relationship("PredictionHistory", back_populates="knowledge_profile", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<KnowledgeProfile(id={self.id}, student_id={self.student_id}, skill_id={self.skill_id})>"

class PredictionHistory(BaseModel):
    """Prediction history model."""
    __tablename__ = 'prediction_history'

    knowledge_profile_id: Mapped[str] = mapped_column(GUID(), ForeignKey('knowledge_profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(GUID(), ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_id: Mapped[str] = mapped_column(GUID(), ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    interaction_order: Mapped[int] = mapped_column(Integer, nullable=False)
    past_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    past_correct: Mapped[int] = mapped_column(Integer, nullable=False)
    past_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    rolling_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    mastered: Mapped[bool] = mapped_column(Boolean, nullable=False)
    forget_probability: Mapped[float] = mapped_column(Float, nullable=False)
    retention_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    triggered_by: Mapped[PredictionTrigger] = mapped_column(SAEnum(PredictionTrigger), nullable=False)
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        CheckConstraint('forget_probability >= 0.0 AND forget_probability <= 1.0', name='check_hist_forget_prob'),
        CheckConstraint('retention_score >= 0.0 AND retention_score <= 1.0', name='check_hist_retention_score'),
        Index('ix_pred_hist_student_skill', 'student_id', 'skill_id'),
    )

    knowledge_profile: Mapped["KnowledgeProfile"] = relationship("KnowledgeProfile", back_populates="prediction_histories")
    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="prediction_histories")
    skill: Mapped["Skill"] = relationship("Skill")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PredictionHistory(id={self.id}, knowledge_profile_id={self.knowledge_profile_id})>"
