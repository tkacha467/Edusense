"""Tests for Revision Planner service and Study Plan APIs."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import StudyPlanStatus
from app.models import User, Skill, KnowledgeProfile
from app.services.adaptive.planner import RevisionPlanner
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill
from tests.fixtures.knowledge import sample_knowledge_profile


def test_revision_planner_generates_study_plan(db_session: Session, onboarded_student_user: User, sample_knowledge_profile: KnowledgeProfile):
    """Verify RevisionPlanner creates an active StudyPlan with prioritized tasks."""
    planner = RevisionPlanner()
    student_profile = onboarded_student_user.student_profile

    plan = planner.generate_adaptive_study_plan(db_session, student_profile)

    assert plan.student_id == student_profile.id
    assert plan.status == StudyPlanStatus.ACTIVE
    assert len(plan.tasks) >= 1


def test_generate_recommendations_api(client: TestClient, onboarded_student_user: User, sample_knowledge_profile: KnowledgeProfile):
    """Verify POST /api/v1/recommendations/generate endpoint."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    res = client.post("/api/v1/recommendations/generate", headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "active"
