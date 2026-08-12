"""Unit tests for Stage A FeatureEngineeringService."""
import pytest
from sqlalchemy.orm import Session
from app.models import User, Skill, KnowledgeProfile
from app.services.knowledge import FeatureEngineeringService
from app.repositories import StudentSkillRepository
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill

skill_repo = StudentSkillRepository()


def test_feature_engineering_first_interaction(db_session: Session, onboarded_student_user: User, sample_skill: Skill):
    """Verify feature calculation on student's first attempt."""
    fe_service = FeatureEngineeringService()
    student_profile = onboarded_student_user.student_profile

    # Record 1 correct attempt
    skill_repo.update_proficiency(db_session, student_id=student_profile.id, skill_id=sample_skill.id, is_correct=True)

    profile = fe_service.compute_and_update_features(db_session, student_id=student_profile.id, skill_id=sample_skill.id)

    assert profile.interaction_order == 1
    assert profile.past_attempts == 1
    assert profile.past_correct == 1
    assert profile.past_accuracy == 1.0
    assert profile.rolling_accuracy == 1.0
    assert profile.mastered is False  # Needs >= 5 attempts


def test_feature_engineering_multiple_mixed_interactions(db_session: Session, onboarded_student_user: User, sample_skill: Skill):
    """Verify feature calculation after 5 mixed attempts (4 correct, 1 wrong = 80% accuracy -> mastered=True)."""
    fe_service = FeatureEngineeringService()
    student_profile = onboarded_student_user.student_profile

    # 4 correct, 1 wrong
    for is_correct in [True, True, True, False, True]:
        skill_repo.update_proficiency(db_session, student_id=student_profile.id, skill_id=sample_skill.id, is_correct=is_correct)
        profile = fe_service.compute_and_update_features(db_session, student_id=student_profile.id, skill_id=sample_skill.id)

    assert profile.interaction_order == 5
    assert profile.past_attempts == 5
    assert profile.past_correct == 4
    assert profile.past_accuracy == 0.8
    assert profile.rolling_accuracy == 0.8
    assert profile.mastered is True
