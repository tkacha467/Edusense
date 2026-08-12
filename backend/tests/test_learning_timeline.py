"""Tests for Learning Timeline service."""
import pytest
from sqlalchemy.orm import Session
from app.models import User
from app.services.adaptive.timeline import LearningTimelineService
from tests.fixtures.users import onboarded_student_user


def test_timeline_event_recording(db_session: Session, onboarded_student_user: User):
    """Verify recording and fetching student timeline events."""
    timeline_service = LearningTimelineService()

    event = timeline_service.record_event(
        db_session,
        user_id=onboarded_student_user.id,
        event_name="recommendation.generated",
        entity_type="StudyPlan",
        entity_id="plan_123",
        details="Generated 3 revision tasks"
    )

    assert event.action == "recommendation.generated"
    events = timeline_service.get_student_timeline(db_session, user_id=onboarded_student_user.id)
    assert len(events) >= 1
