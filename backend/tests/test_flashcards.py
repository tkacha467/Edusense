"""Tests for Flashcard Generator and /ai/flashcards API."""
import pytest
from fastapi.testclient import TestClient


def test_generate_flashcards_api(client: TestClient):
    """Verify POST /api/v1/ai/flashcards endpoint."""
    payload = {"skill_name": "Binary Search Trees", "difficulty": "intermediate", "count": 2}
    res = client.post("/api/v1/ai/flashcards", json=payload)
    assert res.status_code == 200
    cards = res.json()
    assert isinstance(cards, list)
    assert len(cards) >= 1
