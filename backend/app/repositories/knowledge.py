"""Knowledge profile repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.repositories.base import BaseRepository
from app.models import KnowledgeProfile, PredictionHistory
from typing import Any

class KnowledgeProfileRepository(BaseRepository[KnowledgeProfile]):
    """Repository for KnowledgeProfile model."""
    
    def __init__(self) -> None:
        """Initialize with KnowledgeProfile model."""
        super().__init__(KnowledgeProfile)

    def get_by_student(self, db: Session, student_id: str) -> list[KnowledgeProfile]:
        """Get all knowledge profiles for a student."""
        stmt = select(KnowledgeProfile).where(KnowledgeProfile.student_id == student_id)
        return list(db.execute(stmt).scalars().all())

    def get_by_student_and_skill(self, db: Session, student_id: str, skill_id: str) -> KnowledgeProfile | None:
        """Get specific knowledge profile."""
        stmt = select(KnowledgeProfile).where(
            KnowledgeProfile.student_id == student_id,
            KnowledgeProfile.skill_id == skill_id
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_or_create(self, db: Session, student_id: str, skill_id: str) -> KnowledgeProfile:
        """Get existing or create new knowledge profile."""
        profile = self.get_by_student_and_skill(db, student_id, skill_id)
        if not profile:
            profile = self.model(student_id=student_id, skill_id=skill_id)
            db.add(profile)
            db.flush()
        return profile

    def get_at_risk_skills(self, db: Session, student_id: str, threshold: float = 0.5) -> list[KnowledgeProfile]:
        """Get skills at risk of forgetting."""
        stmt = select(KnowledgeProfile).where(
            KnowledgeProfile.student_id == student_id,
            KnowledgeProfile.forget_probability > threshold
        )
        return list(db.execute(stmt).scalars().all())

    get_at_risk_profiles = get_at_risk_skills

    def get_mastered_skills(self, db: Session, student_id: str) -> list[KnowledgeProfile]:
        """Get mastered skills."""
        stmt = select(KnowledgeProfile).where(
            KnowledgeProfile.student_id == student_id,
            KnowledgeProfile.mastered == True
        )
        return list(db.execute(stmt).scalars().all())

    def update_features(self, db: Session, profile_id: str, features: dict[str, Any]) -> KnowledgeProfile | None:
        """Update model features in profile."""
        profile = self.get_by_id(db, profile_id)
        if profile:
            for k, v in features.items():
                if hasattr(profile, k):
                    setattr(profile, k, v)
            db.flush()
        return profile

    def update_prediction(self, db: Session, profile_id: str, forget_prob: float, retention: float, confidence: float | None) -> KnowledgeProfile | None:
        """Update prediction scores."""
        profile = self.get_by_id(db, profile_id)
        if profile:
            profile.forget_probability = forget_prob
            profile.retention_score = retention
            if confidence is not None:
                profile.confidence_score = confidence
            db.flush()
        return profile


class PredictionHistoryRepository(BaseRepository[PredictionHistory]):
    """Repository for PredictionHistory model."""
    
    def __init__(self) -> None:
        """Initialize with PredictionHistory model."""
        super().__init__(PredictionHistory)

    def get_by_student(self, db: Session, student_id: str, skip: int = 0, limit: int = 100) -> list[PredictionHistory]:
        """Get prediction history by student."""
        stmt = select(PredictionHistory).where(PredictionHistory.student_id == student_id).order_by(desc(PredictionHistory.predicted_at)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_knowledge_profile(self, db: Session, profile_id: str, skip: int = 0, limit: int = 100) -> list[PredictionHistory]:
        """Get prediction history by profile."""
        stmt = select(PredictionHistory).where(PredictionHistory.knowledge_profile_id == profile_id).order_by(desc(PredictionHistory.predicted_at)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_student_and_skill(self, db: Session, student_id: str, skill_id: str, skip: int = 0, limit: int = 100) -> list[PredictionHistory]:
        """Get prediction history by student and skill."""
        stmt = select(PredictionHistory).where(
            PredictionHistory.student_id == student_id,
            PredictionHistory.skill_id == skill_id
        ).order_by(desc(PredictionHistory.predicted_at)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_latest_prediction(self, db: Session, student_id: str, skill_id: str) -> PredictionHistory | None:
        """Get latest prediction for student skill."""
        stmt = select(PredictionHistory).where(
            PredictionHistory.student_id == student_id,
            PredictionHistory.skill_id == skill_id
        ).order_by(desc(PredictionHistory.predicted_at)).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    def get_prediction_trend(self, db: Session, student_id: str, skill_id: str, limit: int = 10) -> list[PredictionHistory]:
        """Get trend for a specific skill prediction."""
        stmt = select(PredictionHistory).where(
            PredictionHistory.student_id == student_id,
            PredictionHistory.skill_id == skill_id
        ).order_by(desc(PredictionHistory.predicted_at)).limit(limit)
        return list(db.execute(stmt).scalars().all())
