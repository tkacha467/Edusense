"""Smoke, Deployment, and Health Check Verification Tests."""
import pytest
from fastapi.testclient import TestClient


def test_health_check_endpoints(client: TestClient):
    """Verify /health, /ready, /live endpoints respond with 200 OK."""
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"

    res_live = client.get("/live")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "alive"


def test_security_headers_injected(client: TestClient):
    """Verify ProductionSecurityMiddleware injects security headers and correlation ID."""
    res = client.get("/health")
    assert "X-Correlation-ID" in res.headers
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["X-XSS-Protection"] == "1; mode=block"
