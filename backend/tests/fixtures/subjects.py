"""Subject, Topic, and Enrolment test fixtures."""
import pytest
from sqlalchemy.orm import Session
from app.models import Subject, Topic, StudentSubject, User
from app.repositories import SubjectRepository, TopicRepository, StudentSubjectRepository

subject_repo = SubjectRepository()
topic_repo = TopicRepository()
student_sub_repo = StudentSubjectRepository()


@pytest.fixture
def sample_subject(db_session: Session) -> Subject:
    """Fixture providing a sample Subject entity."""
    sub = subject_repo.create(
        db_session,
        name="Data Structures",
        code="CS101",
        description="Fundamental data structures",
        category="Computer Science",
        semester=1,
        is_active=True
    )
    db_session.commit()
    return sub


@pytest.fixture
def sample_topic(db_session: Session, sample_subject: Subject) -> Topic:
    """Fixture providing a sample Topic entity."""
    top = topic_repo.create(
        db_session,
        subject_id=sample_subject.id,
        name="Binary Search Trees",
        difficulty_level="intermediate",
        description="Tree properties and traversal",
        order_index=1
    )
    db_session.commit()
    return top


@pytest.fixture
def enrolled_student(db_session: Session, onboarded_student_user: User, sample_subject: Subject) -> User:
    """Fixture enrolling an onboarded student into a subject."""
    student_profile = onboarded_student_user.student_profile
    student_sub_repo.create(
        db_session,
        student_id=student_profile.id,
        subject_id=sample_subject.id,
        is_active=True
    )
    db_session.commit()
    return onboarded_student_user
