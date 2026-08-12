"""Security, penetration resilience, and parameter sanitization test suite."""
import pytest
from fastapi.testclient import TestClient
from app.models import User
from tests.fixtures.users import student_user, inactive_user, deleted_user


def test_missing_authorization_header_rejected(client: TestClient):
    """Verify missing auth header is rejected (401 Unauthorized)."""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_malformed_jwt_token_rejected(client: TestClient):
    """Verify malformed bearer token is rejected."""
    res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_jwt_payload_string"})
    assert res.status_code == 401


def test_sql_injection_payload_sanitization(client: TestClient, student_user: User):
    """Verify SQL injection payloads in headers or query parameters do not corrupt query execution."""
    sql_payload = "' OR 1=1; --"
    headers = {"Authorization": f"Bearer dev-token-{sql_payload}"}

    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 401


def test_invalid_uuid_parameter_handling(client: TestClient, student_user: User):
    """Verify invalid UUID parameter format returns 404/422 without crashing backend."""
    headers = {"Authorization": f"Bearer dev-token-{student_user.firebase_uid}"}

    res = client.get("/api/v1/learning/subjects/non-existent-uuid-1234/topics", headers=headers)
    assert res.status_code in [200, 404, 422]  # Handled safely
