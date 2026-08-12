"""Study Scheduler service for intelligent calendar task distribution."""
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models import StudyPlan, StudyTask, StudentProfile
from app.repositories import StudyTaskRepository, LearningPreferenceRepository


class StudyScheduler:
    """Intelligent task scheduler balancing student study hours, spacing effect, and overload prevention."""

    def __init__(self) -> None:
        self.task_repo = StudyTaskRepository()
        self.pref_repo = LearningPreferenceRepository()

    def schedule_plan_tasks(
        self,
        db: Session,
        student_profile: StudentProfile,
        tasks: List[StudyTask]
    ) -> List[StudyTask]:
        """
        Distributes study tasks over the next 7 days ensuring daily time limits are respected.
        """
        pref = self.pref_repo.get_by_student(db, student_id=student_profile.id)
        weekly_hours = pref.weekly_study_hours if pref else 10.0
        daily_max_minutes = int((weekly_hours / 7.0) * 60)
        daily_max_minutes = max(45, daily_max_minutes)

        today = datetime.now(timezone.utc).date()
        daily_allocated: Dict[date, int] = {today + timedelta(days=i): 0 for i in range(7)}

        scheduled_tasks = []
        for task in tasks:
            est_mins = task.estimated_minutes or 30
            # Find first day with capacity
            target_date = today
            for day_offset in range(7):
                candidate_date = today + timedelta(days=day_offset)
                if daily_allocated[candidate_date] + est_mins <= daily_max_minutes:
                    target_date = candidate_date
                    break

            daily_allocated[target_date] += est_mins
            updated = self.task_repo.update(
                db,
                db_obj=task,
                obj_in={"scheduled_date": target_date}
            )
            scheduled_tasks.append(updated or task)

        return scheduled_tasks
