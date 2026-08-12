"""Tests for Explanation Engine and /ai/explain API."""
import pytest
from fastapi.testclient import TestClient


def test_explain_concept_api(client: TestClient):
    """Verify POST /api/v1/ai/explain endpoint."""
    payload = {"concept_name": "Logistic Regression", "subject_name": "Machine Learning", "difficulty": "intermediate"}
    res = client.post("/api/v1/ai/explain", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "explanation" in data
    assert data["concept_name"] == "Logistic Regression"
