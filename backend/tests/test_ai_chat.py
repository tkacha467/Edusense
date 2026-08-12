"""Tests for AI Study Assistant and /ai/chat API."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from tests.fixtures.users import onboarded_student_user


def test_ai_chat_assistant_api(client: TestClient, onboarded_student_user: User):
    """Verify POST /api/v1/ai/chat endpoint with student authentication."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    payload = {"query": "Explain how binary search halving works."}

    res = client.post("/api/v1/ai/chat", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "retrieved_context" in data
