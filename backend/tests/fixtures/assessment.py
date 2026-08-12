"""Assessment session, Question, and QuestionOption test fixtures."""
import pytest
from sqlalchemy.orm import Session
from app.core.enums import AssessmentStatus, GenerationMethod, AssessmentDifficulty, QuestionDifficulty, QuestionType
from app.models import AssessmentSession, Question, QuestionOption, User, Subject, Topic, Skill
from app.repositories import AssessmentSessionRepository, QuestionRepository, QuestionOptionRepository

session_repo = AssessmentSessionRepository()
question_repo = QuestionRepository()
option_repo = QuestionOptionRepository()


@pytest.fixture
def sample_assessment_session(db_session: Session, enrolled_student: User, sample_subject: Subject, sample_topic: Topic) -> AssessmentSession:
    """Fixture providing a pending assessment session."""
    student_profile = enrolled_student.student_profile
    session = session_repo.create(
        db_session,
        student_id=student_profile.id,
        subject_id=sample_subject.id,
        topic_id=sample_topic.id,
        title="BST Quiz 1",
        difficulty_level=AssessmentDifficulty.INTERMEDIATE,
        total_questions=2,
        total_marks=2.0,
        time_limit_seconds=600,
        generation_method=GenerationMethod.AI,
        status=AssessmentStatus.PENDING
    )
    db_session.commit()
    return session


@pytest.fixture
def session_with_questions(db_session: Session, sample_assessment_session: AssessmentSession, sample_skill: Skill) -> AssessmentSession:
    """Fixture providing an assessment session populated with 2 MCQ questions and options."""
    q1 = question_repo.create(
        db_session,
        assessment_session_id=sample_assessment_session.id,
        topic_id=sample_assessment_session.topic_id,
        skill_id=sample_skill.id,
        question_text="What is the average search complexity in a balanced BST?",
        question_type=QuestionType.MCQ,
        difficulty_level=QuestionDifficulty.MEDIUM,
        marks=1.0,
        correct_answer="B",
        explanation="Balanced BST halving search space",
        order_index=0
    )
    option_repo.create(db_session, question_id=q1.id, option_label="A", option_text="O(1)", is_correct=False, order_index=0)
    option_repo.create(db_session, question_id=q1.id, option_label="B", option_text="O(log N)", is_correct=True, order_index=1)
    option_repo.create(db_session, question_id=q1.id, option_label="C", option_text="O(N)", is_correct=False, order_index=2)

    q2 = question_repo.create(
        db_session,
        assessment_session_id=sample_assessment_session.id,
        topic_id=sample_assessment_session.topic_id,
        skill_id=sample_skill.id,
        question_text="Which traversal visits nodes in ascending key order?",
        question_type=QuestionType.MCQ,
        difficulty_level=QuestionDifficulty.EASY,
        marks=1.0,
        correct_answer="A",
        explanation="In-order traversal visits left subtree, root, right subtree",
        order_index=1
    )
    option_repo.create(db_session, question_id=q2.id, option_label="A", option_text="In-order", is_correct=True, order_index=0)
    option_repo.create(db_session, question_id=q2.id, option_label="B", option_text="Pre-order", is_correct=False, order_index=1)
    option_repo.create(db_session, question_id=q2.id, option_label="C", option_text="Post-order", is_correct=False, order_index=2)

    db_session.commit()
    return sample_assessment_session
