"""User and Profile test fixtures."""
import pytest
from sqlalchemy.orm import Session
from app.core.enums import UserRole
from app.models import User, StudentProfile, FacultyProfile
from app.repositories import UserRepository, StudentProfileRepository, FacultyProfileRepository

user_repo = UserRepository()
student_repo = StudentProfileRepository()
faculty_repo = FacultyProfileRepository()


@pytest.fixture
def student_user(db_session: Session) -> User:
    """Fixture providing a registered student user (onboarding incomplete)."""
    user = user_repo.create(
        db_session,
        firebase_uid="uid_student_001",
        email="student@edusense.ai",
        display_name="Alice Student",
        role=UserRole.STUDENT.value,
        is_active=True
    )
    student_repo.create(db_session, user_id=user.id, onboarding_completed=False)
    db_session.commit()
    return user


@pytest.fixture
def onboarded_student_user(db_session: Session) -> User:
    """Fixture providing a student user with completed onboarding."""
    user = user_repo.create(
        db_session,
        firebase_uid="uid_student_onboarded",
        email="onboarded@edusense.ai",
        display_name="Bob Onboarded",
        role=UserRole.STUDENT.value,
        is_active=True
    )
    student_repo.create(
        db_session,
        user_id=user.id,
        institution="Stanford",
        department="CS",
        semester=4,
        enrollment_year=2024,
        onboarding_completed=True
    )
    db_session.commit()
    return user


@pytest.fixture
def faculty_user(db_session: Session) -> User:
    """Fixture providing a registered faculty user."""
    user = user_repo.create(
        db_session,
        firebase_uid="uid_faculty_001",
        email="faculty@edusense.ai",
        display_name="Prof. Knuth",
        role=UserRole.FACULTY.value,
        is_active=True
    )
    faculty_repo.create(db_session, user_id=user.id, institution="Stanford", department="CS")
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Fixture providing an admin user."""
    user = user_repo.create(
        db_session,
        firebase_uid="uid_admin_001",
        email="admin@edusense.ai",
        display_name="Admin User",
        role=UserRole.ADMIN.value,
        is_active=True
    )
    db_session.commit()
    return user


@pytest.fixture
def inactive_user(db_session: Session) -> User:
    """Fixture providing an inactive user."""
    user = user_repo.create(
        db_session,
        firebase_uid="uid_inactive_001",
        email="inactive@edusense.ai",
        display_name="Inactive User",
        role=UserRole.STUDENT.value,
        is_active=False
    )
    db_session.commit()
    return user


@pytest.fixture
def deleted_user(db_session: Session) -> User:
    """Fixture providing a soft-deleted user."""
    from datetime import datetime, timezone
    user = user_repo.create(
        db_session,
        firebase_uid="uid_deleted_001",
        email="deleted@edusense.ai",
        display_name="Deleted User",
        role=UserRole.STUDENT.value,
        is_active=True,
        deleted_at=datetime.now(timezone.utc)
    )
    db_session.commit()
    return user
