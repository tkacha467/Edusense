"""Recommendation repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select, asc
from datetime import datetime, timezone, date
from app.repositories.base import BaseRepository
from app.models import StudyPlan, StudyTask
from app.core.enums import StudyPlanStatus, TaskStatus

class StudyPlanRepository(BaseRepository[StudyPlan]):
    """Repository for StudyPlan model."""
    
    def __init__(self) -> None:
        """Initialize with StudyPlan model."""
        super().__init__(StudyPlan)

    def get_by_student(self, db: Session, student_id: str, skip: int = 0, limit: int = 100) -> list[StudyPlan]:
        """Get study plans by student."""
        stmt = select(StudyPlan).where(StudyPlan.student_id == student_id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_active_plans(self, db: Session, student_id: str) -> list[StudyPlan]:
        """Get active study plans."""
        stmt = select(StudyPlan).where(
            StudyPlan.student_id == student_id,
            StudyPlan.status == StudyPlanStatus.ACTIVE
        )
        return list(db.execute(stmt).scalars().all())

    get_active_by_student = get_active_plans

    def get_by_subject(self, db: Session, student_id: str, subject_id: str) -> list[StudyPlan]:
        """Get study plans for a subject."""
        stmt = select(StudyPlan).where(
            StudyPlan.student_id == student_id,
            StudyPlan.subject_id == subject_id
        )
        return list(db.execute(stmt).scalars().all())

    def archive_plan(self, db: Session, plan_id: str) -> StudyPlan | None:
        """Archive a study plan."""
        plan = self.get_by_id(db, plan_id)
        if plan:
            plan.status = StudyPlanStatus.ARCHIVED
            db.flush()
        return plan

    def complete_plan(self, db: Session, plan_id: str) -> StudyPlan | None:
        """Complete a study plan."""
        plan = self.get_by_id(db, plan_id)
        if plan:
            plan.status = StudyPlanStatus.COMPLETED
            db.flush()
        return plan


class StudyTaskRepository(BaseRepository[StudyTask]):
    """Repository for StudyTask model."""
    
    def __init__(self) -> None:
        """Initialize with StudyTask model."""
        super().__init__(StudyTask)

    def get_by_plan(self, db: Session, plan_id: str) -> list[StudyTask]:
        """Get tasks by study plan ordered by index."""
        stmt = select(StudyTask).where(StudyTask.study_plan_id == plan_id).order_by(asc(StudyTask.order_index))
        return list(db.execute(stmt).scalars().all())

    def get_by_status(self, db: Session, plan_id: str, status: TaskStatus) -> list[StudyTask]:
        """Get tasks by status."""
        stmt = select(StudyTask).where(
            StudyTask.study_plan_id == plan_id,
            StudyTask.status == status
        )
        return list(db.execute(stmt).scalars().all())

    def get_pending_tasks(self, db: Session, student_id: str) -> list[StudyTask]:
        """Get all pending tasks for a student."""
        stmt = (
            select(StudyTask)
            .join(StudyPlan)
            .where(
                StudyPlan.student_id == student_id,
                StudyTask.status == TaskStatus.PENDING
            )
        )
        return list(db.execute(stmt).scalars().all())

    def get_today_tasks(self, db: Session, student_id: str) -> list[StudyTask]:
        """Get tasks scheduled for today."""
        today = date.today()
        stmt = (
            select(StudyTask)
            .join(StudyPlan)
            .where(
                StudyPlan.student_id == student_id,
                StudyTask.scheduled_date == today
            )
        )
        return list(db.execute(stmt).scalars().all())

    def complete_task(self, db: Session, task_id: str) -> StudyTask | None:
        """Complete a task."""
        task = self.get_by_id(db, task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            db.flush()
        return task

    def skip_task(self, db: Session, task_id: str) -> StudyTask | None:
        """Skip a task."""
        task = self.get_by_id(db, task_id)
        if task:
            task.status = TaskStatus.SKIPPED
            db.flush()
        return task
