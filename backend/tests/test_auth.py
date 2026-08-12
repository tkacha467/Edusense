"""Unit and integration tests for Authentication and Identity APIs."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from tests.fixtures.users import student_user, faculty_user, admin_user, inactive_user, deleted_user


def test_register_student_success(client: TestClient, db_session: Session):
    """Verify student registration sync creates user and student profile."""
    payload = {
        "firebase_uid": "uid_new_student_999",
        "email": "newstudent@edusense.ai",
        "display_name": "New Student",
        "role": "student"
    }
    headers = {"Authorization": "Bearer dev-token-uid_new_student_999"}
    response = client.post("/api/v1/auth/register", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newstudent@edusense.ai"
    assert data["role"] == "student"


def test_login_student_success(client: TestClient, student_user: User):
    """Verify login updates timestamp and returns user session payload."""
    headers = {"Authorization": f"Bearer dev-token-{student_user.firebase_uid}"}
    response = client.post("/api/v1/auth/login", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == student_user.email
    assert data["onboarding_completed"] is False


def test_get_current_user_me(client: TestClient, student_user: User):
    """Verify /auth/me returns identity payload for valid Bearer token."""
    headers = {"Authorization": f"Bearer dev-token-{student_user.firebase_uid}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(student_user.id)


def test_unauthenticated_request_returns_401(client: TestClient):
    """Verify unauthenticated access is rejected with 401 Unauthorized."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_invalid_bearer_token_returns_401(client: TestClient):
    """Verify malformed authorization header returns 401."""
    response = client.get("/api/v1/auth/me", headers={"Authorization": "InvalidScheme token"})
    assert response.status_code == 401


def test_inactive_user_returns_403(client: TestClient, inactive_user: User):
    """Verify inactive account is blocked with 403 Forbidden."""
    headers = {"Authorization": f"Bearer dev-token-{inactive_user.firebase_uid}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 403


def test_deleted_user_returns_403(client: TestClient, deleted_user: User):
    """Verify soft-deleted user account is blocked with 403 Forbidden."""
    headers = {"Authorization": f"Bearer dev-token-{deleted_user.firebase_uid}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 403
