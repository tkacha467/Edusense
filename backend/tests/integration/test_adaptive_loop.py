"""Integration tests for the Adaptive Learning Loop."""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
import uuid

from app.models import (
    User, Subject, Topic, AssessmentSession, Question, QuestionOption, 
    StudentResponse, StudentProfile, StudentSkill, KnowledgeProfile
)
from app.core.enums import AssessmentDifficulty, QuestionDifficulty, GenerationMethod
from app.services.knowledge import KnowledgeDecayService, PredictionEngineService
from app.events.handlers import handle_assessment_completed

# ---------------------------------------------------------
# Helper Fixtures & Setup
# ---------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_prediction_engine(monkeypatch):
    """Force fallback to the logistic regression formula for continuous outputs."""
    def fake_predict(self, interaction_order, past_attempts, past_correct, past_accuracy, rolling_accuracy, mastered):
        import numpy as np
        logit = 1.2 - (0.15 * interaction_order) - (2.5 * rolling_accuracy) - (1.0 if mastered else 0.0)
        forget_prob = 1.0 / (1.0 + np.exp(-logit))
        forget_prob = float(np.clip(forget_prob, 0.01, 0.99))
        retention_score = round(1.0 - forget_prob, 4)
        return round(forget_prob, 4), retention_score, 0.85
    
    monkeypatch.setattr(PredictionEngineService, "predict_forgetting_probability", fake_predict)

@pytest.fixture
def test_student(db_session: Session):
    student_id = str(uuid.uuid4())
    user = User(id=student_id, firebase_uid=f"mock_{student_id}", email=f"{student_id}@test.com", display_name="Test Student", role="student", is_active=True)
    db_session.add(user)
    db_session.flush()
    profile = StudentProfile(id=str(uuid.uuid4()), user_id=user.id, preferred_language='en', onboarding_completed=True)
    db_session.add(profile)
    db_session.flush()
    db_session.commit()
    return profile

@pytest.fixture
def test_subject(db_session: Session):
    subject = Subject(id=str(uuid.uuid4()), name="Test Subject", code="TS101", is_active=True)
    db_session.add(subject)
    db_session.flush()
    db_session.commit()
    return subject

@pytest.fixture
def test_topic(db_session: Session, test_subject: Subject):
    topic = Topic(id=str(uuid.uuid4()), subject_id=test_subject.id, name="Test Topic", difficulty_level="beginner", is_active=True, order_index=1)
    db_session.add(topic)
    db_session.flush()
    db_session.commit()
    return topic

@pytest.fixture
def test_skill(db_session: Session, test_topic: Topic):
    from app.models import Skill, TopicSkill
    skill = Skill(id=str(uuid.uuid4()), name=f"Test Skill {uuid.uuid4()}", description="Test")
    db_session.add(skill)
    db_session.flush()
    ts = TopicSkill(id=str(uuid.uuid4()), topic_id=test_topic.id, skill_id=skill.id)
    db_session.add(ts)
    db_session.flush()
    db_session.commit()
    return skill

def run_assessment_cycle(db: Session, student: StudentProfile, subject: Subject, topic: Topic, skill, score_ratio: float, time_taken: int = 10) -> KnowledgeProfile:
    # 1. Create session
    session_id = str(uuid.uuid4())
    session = AssessmentSession(
        id=session_id, student_id=student.id, subject_id=subject.id, topic_id=topic.id,
        title="Test Assesment", difficulty_level="beginner", total_questions=1,
        total_marks=1.0, scored_marks=score_ratio, percentage=score_ratio*100,
        time_limit_seconds=300, time_taken_seconds=time_taken, status="completed",
        generation_method="manual"
    )
    db.add(session)
    db.flush()
    
    # 2. Update StudentSkill (simulate assessment completion)
    student_skill = db.query(StudentSkill).filter_by(student_id=student.id, skill_id=skill.id).first()
    if not student_skill:
        student_skill = StudentSkill(id=str(uuid.uuid4()), student_id=student.id, skill_id=skill.id, proficiency_level=score_ratio, total_attempts=1, correct_attempts=1 if score_ratio > 0.5 else 0)
        db.add(student_skill)
    else:
        student_skill.proficiency_level = (student_skill.proficiency_level + score_ratio) / 2.0
        student_skill.total_attempts += 1
        student_skill.correct_attempts += 1 if score_ratio > 0.5 else 0
    db.flush()
    
    # 3. Trigger handler
    handle_assessment_completed(db, student.id, session.id, [skill.id])
    
    return db.query(KnowledgeProfile).filter_by(student_id=student.id, skill_id=skill.id).first()

# ---------------------------------------------------------
# Test Scenarios
# ---------------------------------------------------------

def test_first_time_assessment_sparse_history(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 1: First time assessment (Sparse history) with 80% score."""
    profile = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.8)
    assert profile is not None
    assert profile.interaction_order == 1
    assert profile.past_attempts == 1
    assert profile.past_accuracy == 1.0
    assert profile.forget_probability > 0.0

def test_perfect_score_first_attempt(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 2: Perfect score on first attempt"""
    profile = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    assert profile.past_accuracy == 1.0
    assert profile.forget_probability < 0.8

def test_zero_score_first_attempt(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 3: Zero score on first attempt"""
    profile = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.0)
    assert profile.past_accuracy == 0.0
    assert profile.forget_probability > 0.7  # Low accuracy yields high forget risk

def test_high_past_accuracy_low_current_accuracy(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 4: High past accuracy, low current accuracy (sudden drop)"""
    p1 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    p2 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    p2_risk = p2.forget_probability
    p3 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.0) # sudden drop
    
    assert p3.interaction_order == 3
    assert p3.forget_probability > p2_risk # risk increased

def test_low_past_accuracy_high_current_accuracy(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 5: Low past accuracy, high current accuracy (sudden improvement)"""
    p1 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.0)
    p1_risk = p1.forget_probability
    p2 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    
    assert p2.forget_probability < p1_risk # risk decreased

def test_multiple_fast_responses_guessing(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 6: Multiple fast responses (guessing behavior simulation)"""
    # Just running multiple rapid assessments with low scores
    p1 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.5, time_taken=2)
    p2 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.5, time_taken=2)
    assert p2.interaction_order == 2

def test_perfect_score_with_long_history_mastered(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 7: Perfect score with long history (Mastered)"""
    # Need to simulate enough history to trigger 'mastered=True' if implemented
    for _ in range(5):
        profile = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    
    assert profile.rolling_accuracy == 1.0
    assert profile.forget_probability < 0.5 # Very stable

def test_long_period_inactivity_forgetting_curve(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 8: Long period of inactivity"""
    # The current logic uses time implicitly in next iterations if handled.
    p1 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    p1_risk = p1.forget_probability
    
    # Simulate time passing by altering last_interaction_at
    p1.last_interaction_at = datetime.now(timezone.utc) - timedelta(days=30)
    db_session.commit()
    
    p2 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.5)
    assert p2.forget_probability > p1_risk

def test_inconsistent_scores_fluctuating(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 9: Inconsistent scores (fluctuating)"""
    run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.0)
    run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    p = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.0)
    assert p.rolling_accuracy < 1.0

def test_consistent_average_scores(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 10: Consistent average scores"""
    for _ in range(2):
        run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
        p = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.0)
    assert p.past_accuracy == 0.5

def test_stability_monotonically_decreasing_score(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 11: Monotonically decreasing score -> monotonically increasing forget prob"""
    p1 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    p1_risk = p1.forget_probability
    p2 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.6)
    p2_risk = p2.forget_probability
    p3 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.2)
    assert p1_risk < p2_risk
    assert p2_risk < p3.forget_probability

def test_stability_monotonically_increasing_score(db_session: Session, test_student, test_subject, test_topic, test_skill):
    """Scenario 12: Monotonically increasing score -> monotonically decreasing forget prob"""
    p1 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.2)
    p1_risk = p1.forget_probability
    p2 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 0.6)
    p2_risk = p2.forget_probability
    p3 = run_assessment_cycle(db_session, test_student, test_subject, test_topic, test_skill, 1.0)
    assert p1_risk > p2_risk
    assert p2_risk > p3.forget_probability

