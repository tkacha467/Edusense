"""System Event Flow integration test suite."""
import pytest
from sqlalchemy.orm import Session
from app.models import User, Skill
from app.services.knowledge import KnowledgeDecayService
from app.repositories import AuditLogRepository
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill

audit_repo = AuditLogRepository()


def test_assessment_completion_event_chain(db_session: Session, onboarded_student_user: User, sample_skill: Skill):
    """Verify end-to-end event chain from assessment completion to feature update and prediction history persistence."""
    knowledge_service = KnowledgeDecayService()
    student_profile = onboarded_student_user.student_profile

    # Execute full pipeline
    profile, snapshot = knowledge_service.run_prediction_pipeline(
        db_session,
        student_id=student_profile.id,
        skill_id=str(sample_skill.id)
    )

    assert profile.interaction_order == 1
    assert snapshot.knowledge_profile_id == profile.id

    # Log audit event
    audit = audit_repo.log_action(
        db_session,
        user_id=onboarded_student_user.id,
        action="assessment.completed",
        entity_type="AssessmentSession",
        entity_id="test_session_id"
    )
    assert audit.action == "assessment.completed"
