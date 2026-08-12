"""Progress Tracker service for computing study completion streaks and metrics."""
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.enums import TaskStatus, ActivityType
from app.models import StudentProfile, StudyTask, StudentActivity
from app.repositories import StudyTaskRepository, StudentActivityRepository


class ProgressTracker:
    """Calculates study completion percentage, streaks, and learning consistency metrics."""

    def __init__(self) -> None:
        self.task_repo = StudyTaskRepository()
        self.act_repo = StudentActivityRepository()

    def calculate_student_progress(
        self,
        db: Session,
        student_id: str
    ) -> Dict[str, Any]:
        """
        Computes progress overview:
        - Completed tasks count & percentage
        - Current study streak (consecutive days with completed tasks/activity)
        - Pending & Overdue tasks count
        """
        tasks = self.task_repo.get_by_student(db, student_id=student_id)
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        pending_tasks = len([t for t in tasks if t.status == TaskStatus.PENDING])

        today = datetime.now(timezone.utc).date()
        overdue_tasks = len([
            t for t in tasks
            if t.status == TaskStatus.PENDING and t.scheduled_date and t.scheduled_date < today
        ])

        completion_pct = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0

        # Calculate current daily streak
        streak_days = 0
        current_check = today
        for _ in range(30):
            day_activities = self.act_repo.get_by_student_and_date(db, student_id=student_id, activity_date=current_check)
            if day_activities or any(t.completed_at and t.completed_at.date() == current_check for t in tasks):
                streak_days += 1
                current_check -= timedelta(days=1)
            else:
                break

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_percentage": round(completion_pct, 1),
            "current_streak_days": streak_days
        }
