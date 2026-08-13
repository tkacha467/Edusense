"""Tests for Explanation Engine and /ai/explain API."""
import pytest
from fastapi.testclient import TestClient
from app.models import User
from tests.fixtures.users import onboarded_student_user


def test_explain_concept_api(client: TestClient, onboarded_student_user: User):
    """Verify POST /api/v1/ai/explain endpoint."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    payload = {"concept_name": "Logistic Regression", "subject_name": "Machine Learning", "difficulty": "intermediate"}
    res = client.post("/api/v1/ai/explain", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "explanation" in data
    assert data["concept_name"] == "Logistic Regression"
