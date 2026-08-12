"""Tests for Study Task completion and skipping APIs."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User, Skill, KnowledgeProfile
from app.services.adaptive.planner import RevisionPlanner
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill
from tests.fixtures.knowledge import sample_knowledge_profile


def test_complete_and_skip_task_apis(client: TestClient, db_session: Session, onboarded_student_user: User, sample_knowledge_profile: KnowledgeProfile):
    """Verify marking a study task completed and skipped."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}

    # Generate plan with tasks
    gen_res = client.post("/api/v1/recommendations/generate", headers=headers)
    assert gen_res.status_code == 201
    plan_id = gen_res.json()["id"]

    # Fetch plan tasks
    plan_res = client.get(f"/api/v1/study-plans/{plan_id}", headers=headers)
    assert plan_res.status_code == 200
    tasks = plan_res.json()["tasks"]
    assert len(tasks) >= 1
    first_task_id = tasks[0]["id"]

    # Mark complete
    res_complete = client.put(f"/api/v1/study-tasks/{first_task_id}/complete", headers=headers)
    assert res_complete.status_code == 200
    assert res_complete.json()["status"] == "completed"

    if len(tasks) > 1:
        second_task_id = tasks[1]["id"]
        res_skip = client.put(f"/api/v1/study-tasks/{second_task_id}/skip", headers=headers)
        assert res_skip.status_code == 200
        assert res_skip.json()["status"] == "skipped"
