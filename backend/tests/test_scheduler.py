"""Tests for Study Scheduler service."""
import pytest
from sqlalchemy.orm import Session
from app.models import User, Skill, KnowledgeProfile
from app.services.adaptive.planner import RevisionPlanner
from app.services.adaptive.scheduler import StudyScheduler
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.skills import sample_skill
from tests.fixtures.knowledge import sample_knowledge_profile


def test_scheduler_distributes_tasks(db_session: Session, onboarded_student_user: User, sample_knowledge_profile: KnowledgeProfile):
    """Verify StudyScheduler schedules tasks across dates respecting study limits."""
    planner = RevisionPlanner()
    scheduler = StudyScheduler()
    student_profile = onboarded_student_user.student_profile

    plan = planner.generate_adaptive_study_plan(db_session, student_profile)
    scheduled_tasks = scheduler.schedule_plan_tasks(db_session, student_profile, plan.tasks)

    assert len(scheduled_tasks) == len(plan.tasks)
    assert all(t.scheduled_date is not None for t in scheduled_tasks)
