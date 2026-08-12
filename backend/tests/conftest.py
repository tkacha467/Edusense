"""Global Pytest configuration, database fixtures, and FastAPI TestClient dependency overrides."""
import os
import sys
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database.database import Base, create_all_tables
from app.dependencies.database import get_db

# Import all fixtures to expose them globally to pytest
from tests.fixtures.users import student_user, onboarded_student_user, faculty_user, admin_user, inactive_user, deleted_user
from tests.fixtures.subjects import sample_subject, sample_topic, enrolled_student
from tests.fixtures.skills import sample_skill, topic_skill_link
from tests.fixtures.assessment import sample_assessment_session, session_with_questions
from tests.fixtures.knowledge import sample_knowledge_profile, sample_prediction_history

# Use in-memory SQLite for ultra-fast, completely isolated test runs
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a clean, isolated database session per test function.
    Materializes all 22 SQLAlchemy tables and drops them afterwards.
    """
    create_all_tables(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    FastAPI TestClient with get_db dependency overridden to use in-memory db_session.
    """
    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def make_auth_header():
    """Helper factory for generating Dev Bearer Authorization headers."""
    def _auth_header(uid: str) -> dict:
        return {"Authorization": f"Bearer dev-token-{uid}"}
    return _auth_header
