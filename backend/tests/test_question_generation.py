"""Tests for AI Question Generator and /ai/questions API."""
import pytest
from fastapi.testclient import TestClient


def test_question_generation_api(client: TestClient):
    """Verify POST /api/v1/ai/questions endpoint."""
    payload = {"topic_name": "Graph Algorithms", "question_type": "mcq", "difficulty": "hard", "count": 2}
    res = client.post("/api/v1/ai/questions", json=payload)
    assert res.status_code == 200
    questions = res.json()
    assert isinstance(questions, list)
    assert len(questions) >= 1
