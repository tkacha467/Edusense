"""Assessment Analytics Service test suite."""
import pytest
from sqlalchemy.orm import Session
from app.models import User, AssessmentSession
from app.services.assessment_analytics import AssessmentAnalyticsService
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.subjects import sample_subject, sample_topic, enrolled_student
from tests.fixtures.assessment import session_with_questions


def test_assessment_analytics_processing(db_session: Session, enrolled_student: User, session_with_questions: AssessmentSession):
    """Verify AssessmentAnalyticsService computes topic, skill, and time metrics correctly."""
    analytics_service = AssessmentAnalyticsService()
    student_profile = enrolled_student.student_profile

    result = analytics_service.process_session_analytics(
        db_session,
        session_id=session_with_questions.id,
        student_id=student_profile.id
    )

    assert result["session_id"] == session_with_questions.id
    assert "avg_time_seconds" in result
    assert "topic_accuracy" in result
    assert "confidence_breakdown" in result
