"""Role-Based Access Control (RBAC) test suite."""
import pytest
from fastapi.testclient import TestClient
from app.models import User
from tests.fixtures.users import student_user, faculty_user, admin_user


def test_student_cannot_access_faculty_profile(client: TestClient, student_user: User):
    """Verify Student role is rejected from Faculty-only endpoint (403 Forbidden)."""
    headers = {"Authorization": f"Bearer dev-token-{student_user.firebase_uid}"}
    response = client.get("/api/v1/faculty/me/profile", headers=headers)
    assert response.status_code == 403


def test_faculty_can_access_faculty_profile(client: TestClient, faculty_user: User):
    """Verify Faculty role is authorized for Faculty endpoint."""
    headers = {"Authorization": f"Bearer dev-token-{faculty_user.firebase_uid}"}
    response = client.get("/api/v1/faculty/me/profile", headers=headers)
    assert response.status_code == 200


def test_student_cannot_create_subject(client: TestClient, student_user: User):
    """Verify Student role cannot create learning subjects."""
    headers = {"Authorization": f"Bearer dev-token-{student_user.firebase_uid}"}
    payload = {
        "name": "Unauthorized Subject",
        "code": "BAD101",
        "description": "Should fail",
        "category": "Test",
        "semester": 1
    }
    response = client.post("/api/v1/learning/subjects", json=payload, headers=headers)
    assert response.status_code == 403


def test_faculty_and_admin_can_create_subject(client: TestClient, faculty_user: User, admin_user: User):
    """Verify Faculty and Admin roles can create learning subjects."""
    # Faculty test
    headers_f = {"Authorization": f"Bearer dev-token-{faculty_user.firebase_uid}"}
    payload_f = {"name": "Physics I", "code": "PHY101", "description": "Physics", "category": "Science", "semester": 1}
    res_f = client.post("/api/v1/learning/subjects", json=payload_f, headers=headers_f)
    assert res_f.status_code == 201

    # Admin test
    headers_a = {"Authorization": f"Bearer dev-token-{admin_user.firebase_uid}"}
    payload_a = {"name": "Chemistry I", "code": "CHM101", "description": "Chemistry", "category": "Science", "semester": 1}
    res_a = client.post("/api/v1/learning/subjects", json=payload_a, headers=headers_a)
    assert res_a.status_code == 201
