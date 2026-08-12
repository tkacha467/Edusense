"""Knowledge profile and prediction history test fixtures."""
import pytest
from sqlalchemy.orm import Session
from app.models import KnowledgeProfile, PredictionHistory, User, Skill
from app.repositories import KnowledgeProfileRepository, PredictionHistoryRepository

kp_repo = KnowledgeProfileRepository()
ph_repo = PredictionHistoryRepository()


@pytest.fixture
def sample_knowledge_profile(db_session: Session, onboarded_student_user: User, sample_skill: Skill) -> KnowledgeProfile:
    """Fixture providing a sample KnowledgeProfile entity."""
    student_profile = onboarded_student_user.student_profile
    profile = kp_repo.create(
        db_session,
        student_id=student_profile.id,
        skill_id=sample_skill.id,
        interaction_order=1,
        past_attempts=1,
        past_correct=1,
        past_accuracy=1.0,
        rolling_accuracy=1.0,
        mastered=False,
        forget_probability=0.25,
        retention_score=0.75,
        confidence_score=0.90
    )
    db_session.commit()
    return profile


@pytest.fixture
def sample_prediction_history(db_session: Session, sample_knowledge_profile: KnowledgeProfile) -> PredictionHistory:
    """Fixture providing a sample PredictionHistory snapshot record."""
    history = ph_repo.create(
        db_session,
        knowledge_profile_id=sample_knowledge_profile.id,
        student_id=sample_knowledge_profile.student_id,
        skill_id=sample_knowledge_profile.skill_id,
        interaction_order=sample_knowledge_profile.interaction_order,
        past_attempts=sample_knowledge_profile.past_attempts,
        past_correct=sample_knowledge_profile.past_correct,
        past_accuracy=sample_knowledge_profile.past_accuracy,
        rolling_accuracy=sample_knowledge_profile.rolling_accuracy,
        mastered=sample_knowledge_profile.mastered,
        forget_probability=sample_knowledge_profile.forget_probability,
        retention_score=sample_knowledge_profile.retention_score,
        confidence_score=sample_knowledge_profile.confidence_score,
        model_version="logistic_regression_v1.0",
        triggered_by="ASSESSMENT_COMPLETE"
    )
    db_session.commit()
    return history
