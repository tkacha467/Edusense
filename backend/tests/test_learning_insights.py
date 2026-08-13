"""Tests for Learning Insights Engine and AI Observability APIs."""
import pytest
from fastapi.testclient import TestClient
from app.models import User
from tests.fixtures.users import onboarded_student_user


def test_ai_usage_stats_api(client: TestClient, onboarded_student_user: User):
    """Verify GET /api/v1/ai/usage and /api/v1/ai/history endpoints."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}
    res_usage = client.get("/api/v1/ai/usage", headers=headers)
    assert res_usage.status_code == 200
    assert "total_requests" in res_usage.json()

    res_history = client.get("/api/v1/ai/history", headers=headers)
    assert res_history.status_code == 200
    assert "history" in res_history.json()
