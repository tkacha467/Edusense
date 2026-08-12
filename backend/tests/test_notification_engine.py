"""Tests for Notification Engine and Notification APIs."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from app.services.adaptive.notification_engine import AdaptiveNotificationEngine
from tests.fixtures.users import onboarded_student_user


def test_adaptive_notification_engine(db_session: Session, onboarded_student_user: User):
    """Verify AdaptiveNotificationEngine creates alerts."""
    engine = AdaptiveNotificationEngine()

    notif = engine.send_decay_alert(
        db_session,
        user_id=onboarded_student_user.id,
        skill_name="Binary Search",
        forget_probability=0.82
    )

    assert notif.user_id == onboarded_student_user.id
    assert "Binary Search" in notif.message


def test_notification_apis(client: TestClient, onboarded_student_user: User):
    """Verify notification REST API endpoints."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}

    # List notifications
    res_list = client.get("/api/v1/notifications/me", headers=headers)
    assert res_list.status_code == 200

    # Unread count
    res_count = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert res_count.status_code == 200
    assert "unread_count" in res_count.json()
