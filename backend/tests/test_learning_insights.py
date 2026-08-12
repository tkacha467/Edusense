"""Tests for Learning Insights Engine and AI Observability APIs."""
import pytest
from fastapi.testclient import TestClient


def test_ai_usage_stats_api(client: TestClient):
    """Verify GET /api/v1/ai/usage and /api/v1/ai/history endpoints."""
    res_usage = client.get("/api/v1/ai/usage")
    assert res_usage.status_code == 200
    assert "total_requests" in res_usage.json()

    res_history = client.get("/api/v1/ai/history")
    assert res_history.status_code == 200
    assert "history" in res_history.json()
