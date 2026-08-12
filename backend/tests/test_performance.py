"""Performance & Execution SLA latency benchmark test suite."""
import time
import pytest
from fastapi.testclient import TestClient
from app.models import User, Skill, KnowledgeProfile
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill
from tests.fixtures.knowledge import sample_knowledge_profile


def test_prediction_api_latency_under_2_seconds(client: TestClient, onboarded_student_user: User, sample_skill: Skill):
    """Verify ML prediction endpoint responds in under 2 seconds."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    payload = {"skill_id": str(sample_skill.id)}

    start_time = time.time()
    res = client.post("/api/v1/knowledge/predict", json=payload, headers=headers)
    elapsed = time.time() - start_time

    assert res.status_code == 200
    assert elapsed < 2.0, f"Prediction SLA violated: took {elapsed:.2f}s (expected < 2.0s)"


def test_knowledge_profiles_latency_under_1_second(client: TestClient, onboarded_student_user: User, sample_knowledge_profile: KnowledgeProfile):
    """Verify knowledge profile query responds in under 1 second."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}

    start_time = time.time()
    res = client.get("/api/v1/knowledge/profiles", headers=headers)
    elapsed = time.time() - start_time

    assert res.status_code == 200
    assert elapsed < 1.0, f"Profile query SLA violated: took {elapsed:.2f}s (expected < 1.0s)"


def test_trend_endpoint_latency_under_1_second(client: TestClient, onboarded_student_user: User, sample_knowledge_profile: KnowledgeProfile):
    """Verify trend timeline endpoint responds in under 1 second."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}

    start_time = time.time()
    res = client.get(f"/api/v1/knowledge/skills/{sample_knowledge_profile.skill_id}/trend", headers=headers)
    elapsed = time.time() - start_time

    assert res.status_code == 200
    assert elapsed < 1.0, f"Trend endpoint SLA violated: took {elapsed:.2f}s (expected < 1.0s)"
