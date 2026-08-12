"""Student Onboarding Wizard test suite."""
import pytest
from fastapi.testclient import TestClient
from app.models import User, Subject
from tests.fixtures.users import student_user, onboarded_student_user
from tests.fixtures.subjects import sample_subject


def test_onboarding_wizard_full_flow(client: TestClient, student_user: User, sample_subject: Subject):
    """Verify complete 4-step student onboarding wizard flow."""
    headers = {"Authorization": f"Bearer dev-token-{student_user.firebase_uid}"}

    # Initial status check
    res_status = client.get("/api/v1/onboarding/status", headers=headers)
    assert res_status.status_code == 200
    assert res_status.json()["onboarding_completed"] is False

    # Step 1: Institution
    res_step1 = client.put("/api/v1/onboarding/institution", json={
        "institution": "MIT",
        "department": "EECS",
        "semester": 3,
        "enrollment_year": 2024
    }, headers=headers)
    assert res_step1.status_code == 200

    # Step 2: Preferences
    res_step2 = client.put("/api/v1/onboarding/preferences", json={
        "weekly_study_hours": 10.0,
        "preferred_difficulty": "intermediate",
        "preferred_session_length": 30,
        "target_score": 85.0
    }, headers=headers)
    assert res_step2.status_code == 200

    # Step 3: Subjects
    res_step3 = client.post("/api/v1/onboarding/subjects", json={
        "subject_ids": [str(sample_subject.id)]
    }, headers=headers)
    assert res_step3.status_code == 200

    # Step 4: Complete
    res_step4 = client.post("/api/v1/onboarding/complete", headers=headers)
    assert res_step4.status_code == 200
    assert res_step4.json()["onboarding_completed"] is True


def test_incomplete_onboarding_blocks_protected_endpoints(client: TestClient, student_user: User):
    """Verify protected endpoints require completed onboarding."""
    headers = {"Authorization": f"Bearer dev-token-{student_user.firebase_uid}"}
    res = client.get("/api/v1/knowledge/profiles", headers=headers)
    assert res.status_code == 403
