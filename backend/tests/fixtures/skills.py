"""Skill and TopicSkill test fixtures."""
import pytest
from sqlalchemy.orm import Session
from app.models import Skill, TopicSkill, Topic
from app.repositories import SkillRepository, TopicSkillRepository

skill_repo = SkillRepository()
topic_skill_repo = TopicSkillRepository()


@pytest.fixture
def sample_skill(db_session: Session) -> Skill:
    """Fixture providing a sample Skill entity."""
    sk = skill_repo.create(
        db_session,
        name="BST Insertion Algorithm",
        description="Inserting elements into a BST",
        category="Algorithms"
    )
    db_session.commit()
    return sk


@pytest.fixture
def topic_skill_link(db_session: Session, sample_topic: Topic, sample_skill: Skill) -> TopicSkill:
    """Fixture linking a Topic to a Skill."""
    link = topic_skill_repo.create(
        db_session,
        topic_id=sample_topic.id,
        skill_id=sample_skill.id,
        relevance_weight=1.0
    )
    db_session.commit()
    return link
