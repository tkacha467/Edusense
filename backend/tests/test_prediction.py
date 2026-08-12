"""Unit and API integration tests for ML Prediction Engine."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User, Skill, KnowledgeProfile
from app.services.knowledge import PredictionEngineService, KnowledgeDecayService
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill
from tests.fixtures.knowledge import sample_knowledge_profile


def test_prediction_engine_inference_bounds():
    """Verify PredictionEngineService outputs probabilities within [0, 1] and sum to ~1."""
    pred_service = PredictionEngineService()

    forget_prob, retention_score, confidence = pred_service.predict_forgetting_probability(
        interaction_order=2,
        past_attempts=5,
        past_correct=4,
        past_accuracy=0.8,
        rolling_accuracy=0.8,
        mastered=True
    )

    assert 0.0 <= forget_prob <= 1.0
    assert 0.0 <= retention_score <= 1.0
    assert abs((forget_prob + retention_score) - 1.0) < 0.001
    assert confidence > 0.0


def test_full_knowledge_decay_pipeline(db_session: Session, onboarded_student_user: User, sample_skill: Skill):
    """Verify KnowledgeDecayService orchestrates feature calculation, ML inference, and history snapshotting."""
    service = KnowledgeDecayService()
    student_profile = onboarded_student_user.student_profile

    updated_profile, snapshot = service.run_prediction_pipeline(
        db_session,
        student_id=student_profile.id,
        skill_id=str(sample_skill.id)
    )

    assert updated_profile.forget_probability is not None
    assert updated_profile.retention_score is not None
    assert snapshot.knowledge_profile_id == updated_profile.id
    assert snapshot.forget_probability == updated_profile.forget_probability


def test_prediction_trend_api(client: TestClient, onboarded_student_user: User, sample_knowledge_profile: KnowledgeProfile):
    """Verify /knowledge/skills/{id}/trend returns ordered prediction history snapshots."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    res = client.get(f"/api/v1/knowledge/skills/{sample_knowledge_profile.skill_id}/trend", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
