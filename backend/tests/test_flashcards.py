"""Tests for Flashcard Generator and /ai/flashcards API."""
import pytest
from fastapi.testclient import TestClient
from app.models import User
from tests.fixtures.users import onboarded_student_user


def test_generate_flashcards_api(client: TestClient, onboarded_student_user: User):
    """Verify POST /api/v1/ai/flashcards endpoint."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    payload = {"skill_name": "Binary Search Trees", "difficulty": "intermediate", "count": 2}
    res = client.post("/api/v1/ai/flashcards", json=payload, headers=headers)
    assert res.status_code == 200
    cards = res.json()
    assert isinstance(cards, list)
    assert len(cards) >= 1
