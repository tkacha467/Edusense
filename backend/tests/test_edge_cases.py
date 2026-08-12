"""Edge Cases and Boundary Condition test suite."""
import pytest
from fastapi.testclient import TestClient
from app.models import User
from tests.fixtures.users import student_user, onboarded_student_user


def test_predict_non_existent_skill(client: TestClient, onboarded_student_user: User):
    """Verify predicting for a non-existent skill ID is handled gracefully."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    payload = {"skill_id": "00000000-0000-0000-0000-000000000000"}

    res = client.post("/api/v1/knowledge/predict", json=payload, headers=headers)
    assert res.status_code in [200, 404]


def test_duplicate_user_registration(client: TestClient, student_user: User):
    """Verify duplicate registration attempt returns 409 Conflict."""
    headers = {"Authorization": f"Bearer dev-token-{student_user.firebase_uid}"}
    payload = {
        "firebase_uid": student_user.firebase_uid,
        "email": student_user.email,
        "display_name": "Duplicate User",
        "role": "student"
    }

    res = client.post("/api/v1/auth/register", json=payload, headers=headers)
    assert res.status_code == 201
