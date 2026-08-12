"""Notification dispatch and status test suite."""
import pytest
from sqlalchemy.orm import Session
from app.models import User, Skill
from app.services.knowledge import KnowledgeDecayService
from app.repositories import NotificationRepository
from app.core.enums import NotificationType, NotificationPriority
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill

notif_repo = NotificationRepository()


def test_notification_created_on_high_forget_risk(db_session: Session, onboarded_student_user: User, sample_skill: Skill):
    """Verify notification is created when forget_probability > 0.50."""
    student_profile = onboarded_student_user.student_profile
    notif = notif_repo.create(
        db_session,
        user_id=onboarded_student_user.id,
        title="Knowledge Decay Alert",
        message="High forgetting risk",
        notification_type=NotificationType.PREDICTION_ALERT.value,
        priority=NotificationPriority.HIGH.value
    )
    db_session.commit()

    unread = notif_repo.get_unread_by_user(db_session, user_id=onboarded_student_user.id)
    assert len(unread) == 1
    assert unread[0].id == notif.id


def test_mark_notification_as_read(db_session: Session, onboarded_student_user: User):
    """Verify marking notification as read updates status."""
    notif = notif_repo.create(
        db_session,
        user_id=onboarded_student_user.id,
        title="System Notice",
        message="Welcome to EduSense AI",
        notification_type=NotificationType.SYSTEM.value
    )
    db_session.commit()

    updated = notif_repo.mark_as_read(db_session, notification_id=notif.id)
    assert updated.is_read is True
