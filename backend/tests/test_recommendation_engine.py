"""Tests for Recommendation Decision Engine and Priority Calculator."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import TaskPriority
from app.models import User, Skill, KnowledgeProfile
from app.services.adaptive.decision_engine import PriorityCalculator, RecommendationDecisionEngine
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill
from tests.fixtures.knowledge import sample_knowledge_profile


def test_priority_calculator_thresholds():
    """Verify priority rules mapping from forget_probability."""
    assert PriorityCalculator.calculate_priority(0.85) == TaskPriority.HIGH
    assert PriorityCalculator.calculate_priority(0.65) == TaskPriority.HIGH
    assert PriorityCalculator.calculate_priority(0.45) == TaskPriority.MEDIUM
    assert PriorityCalculator.calculate_priority(0.20) == TaskPriority.LOW


def test_decision_engine_evaluation(db_session: Session, onboarded_student_user: User, sample_knowledge_profile: KnowledgeProfile):
    """Verify RecommendationDecisionEngine generates valid deterministic decisions."""
    engine = RecommendationDecisionEngine()
    student_profile = onboarded_student_user.student_profile

    decision = engine.evaluate_skill_decision(db_session, student_profile, sample_knowledge_profile)

    assert decision.student_id == student_profile.id
    assert decision.skill_id == sample_knowledge_profile.skill_id
    assert decision.forget_probability == sample_knowledge_profile.forget_probability
    assert isinstance(decision.priority, TaskPriority)


def test_get_recommendations_api(client: TestClient, onboarded_student_user: User, sample_knowledge_profile: KnowledgeProfile):
    """Verify GET /api/v1/recommendations endpoint."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    res = client.get("/api/v1/recommendations", headers=headers)
    assert res.status_code == 200
    decisions = res.json()
    assert isinstance(decisions, list)
