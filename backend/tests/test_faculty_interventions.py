"""Tests for Faculty Intervention Engine."""
import pytest
from sqlalchemy.orm import Session
from app.models import User, Skill, KnowledgeProfile
from app.services.adaptive.faculty_intervention import FacultyInterventionEngine
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill


def test_faculty_intervention_trigger(db_session: Session, onboarded_student_user: User, sample_skill: Skill):
    """Verify faculty intervention triggers on critical decay risk (forget_prob > 0.85)."""
    engine = FacultyInterventionEngine()
    student_profile = onboarded_student_user.student_profile

    high_risk_kp = KnowledgeProfile(
        student_id=student_profile.id,
        skill_id=sample_skill.id,
        interaction_order=3,
        past_attempts=3,
        past_correct=1,
        past_accuracy=0.33,
        rolling_accuracy=0.33,
        mastered=False,
        forget_probability=0.90
    )
    db_session.add(high_risk_kp)
    db_session.commit()

    result = engine.check_and_trigger_intervention(db_session, student_profile, high_risk_kp)
    assert result is not None
    assert result["intervention_triggered"] is True
