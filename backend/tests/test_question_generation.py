"""Tests for AI Question Generator and /ai/questions API."""
import pytest
from fastapi.testclient import TestClient
from app.models import User
from tests.fixtures.users import onboarded_student_user


def test_question_generation_api(client: TestClient, onboarded_student_user: User):
    """Verify POST /api/v1/ai/questions endpoint."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    payload = {"topic_name": "Graph Algorithms", "question_type": "mcq", "difficulty": "hard", "count": 2}
    res = client.post("/api/v1/ai/questions", json=payload, headers=headers)
    assert res.status_code == 200
    questions = res.json()
    assert isinstance(questions, list)
    assert len(questions) >= 1
