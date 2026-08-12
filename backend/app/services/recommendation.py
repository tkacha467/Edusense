"""Recommendation and study plan service module."""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.repositories import StudyPlanRepository, StudyTaskRepository, KnowledgeProfileRepository
from app.models import StudyPlan, StudyTask
from app.core.exceptions import NotFoundException
from app.core.enums import StudyPlanStatus, TaskStatus


class RecommendationService:
    """Service for managing AI-recommended study plans and study tasks."""

    def __init__(self) -> None:
        """Initialize RecommendationService with necessary repositories."""
        self.plan_repo = StudyPlanRepository()
        self.task_repo = StudyTaskRepository()
        self.knowledge_repo = KnowledgeProfileRepository()

    def create_study_plan(
        self, 
        db: Session, 
        student_id: str, 
        title: str, 
        plan_type: str, 
        subject_id: Optional[str] = None, 
        description: Optional[str] = None, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
        ai_model_used: Optional[str] = None
    ) -> StudyPlan:
        """
        Create a new study plan.

        Args:
            db (Session): Database session.
            student_id (str): Student ID.
            title (str): Title of the plan.
            plan_type (str): Type of the plan (e.g., 'remedial', 'advanced').
            subject_id (Optional[str]): Subject ID if applicable.
            description (Optional[str]): Description of the plan.
            start_date (Optional[datetime]): Start date.
            end_date (Optional[datetime]): End date.
            ai_model_used (Optional[str]): The AI model generating this plan.

        Returns:
            StudyPlan: The created study plan.
        """
        plan_data = {
            "student_id": student_id,
            "title": title,
            "plan_type": plan_type,
            "subject_id": subject_id,
            "description": description,
            "start_date": start_date or datetime.now(timezone.utc),
            "end_date": end_date,
            "ai_model_used": ai_model_used,
            "status": StudyPlanStatus.ACTIVE
        }
        return self.plan_repo.create(db, obj_in=plan_data)

    def add_tasks_to_plan(self, db: Session, plan_id: str, tasks_data: List[Dict[str, Any]]) -> List[StudyTask]:
        """
        Add generated tasks to a study plan.

        Args:
            db (Session): Database session.
            plan_id (str): ID of the study plan.
            tasks_data (List[Dict[str, Any]]): List of task dictionaries.

        Returns:
            List[StudyTask]: The list of created study tasks.

        Raises:
            NotFoundException: If the plan does not exist.
        """
        plan = self.plan_repo.get_by_id(db, plan_id)
        if not plan:
            raise NotFoundException(f"StudyPlan '{plan_id}' not found.")

        created_tasks = []
        for task_data in tasks_data:
            task_data["study_plan_id"] = plan_id
            task_data["status"] = TaskStatus.PENDING
            task = self.task_repo.create(db, obj_in=task_data)
            created_tasks.append(task)
            
        return created_tasks

    def get_active_plans(self, db: Session, student_id: str) -> List[StudyPlan]:
        """
        Get all currently active study plans for a student.

        Args:
            db (Session): Database session.
            student_id (str): Student ID.

        Returns:
            List[StudyPlan]: List of active study plans.
        """
        return self.plan_repo.get_active_plans(db, student_id=student_id)

    def get_plan_detail(self, db: Session, plan_id: str) -> StudyPlan:
        """
        Retrieve a study plan with all its nested tasks.

        Args:
            db (Session): Database session.
            plan_id (str): Study plan ID.

        Returns:
            StudyPlan: Study plan with tasks loaded.
            
        Raises:
            NotFoundException: If the plan does not exist.
        """
        plan = self.plan_repo.get_by_id(db, plan_id)
        if not plan:
            raise NotFoundException(f"StudyPlan '{plan_id}' not found.")
        return plan

    def complete_plan(self, db: Session, plan_id: str) -> StudyPlan:
        """
        Mark a study plan as completed.

        Args:
            db (Session): Database session.
            plan_id (str): Study plan ID.

        Returns:
            StudyPlan: The updated study plan.
        """
        plan = self.plan_repo.get_by_id(db, plan_id)
        if not plan:
            raise NotFoundException(f"StudyPlan '{plan_id}' not found.")
        return self.plan_repo.update(db, db_obj=plan, obj_in={"status": StudyPlanStatus.COMPLETED})

    def archive_plan(self, db: Session, plan_id: str) -> StudyPlan:
        """
        Mark a study plan as archived.

        Args:
            db (Session): Database session.
            plan_id (str): Study plan ID.

        Returns:
            StudyPlan: The updated study plan.
        """
        plan = self.plan_repo.get_by_id(db, plan_id)
        if not plan:
            raise NotFoundException(f"StudyPlan '{plan_id}' not found.")
        return self.plan_repo.update(db, db_obj=plan, obj_in={"status": StudyPlanStatus.ARCHIVED})

    def get_today_tasks(self, db: Session, student_id: str) -> List[StudyTask]:
        """
        Retrieve all study tasks scheduled for today.

        Args:
            db (Session): Database session.
            student_id (str): Student ID.

        Returns:
            List[StudyTask]: Tasks scheduled for today.
        """
        return self.task_repo.get_today_tasks(db, student_id=student_id)

    def complete_task(self, db: Session, task_id: str) -> StudyTask:
        """
        Mark a study task as completed.

        Args:
            db (Session): Database session.
            task_id (str): Task ID.

        Returns:
            StudyTask: The updated task.
        """
        task = self.task_repo.get_by_id(db, task_id)
        if not task:
            raise NotFoundException(f"StudyTask '{task_id}' not found.")
        return self.task_repo.update(
            db, db_obj=task, obj_in={"status": TaskStatus.COMPLETED, "completed_at": datetime.now(timezone.utc)}
        )

    def skip_task(self, db: Session, task_id: str) -> StudyTask:
        """
        Mark a study task as skipped.

        Args:
            db (Session): Database session.
            task_id (str): Task ID.

        Returns:
            StudyTask: The updated task.
        """
        task = self.task_repo.get_by_id(db, task_id)
        if not task:
            raise NotFoundException(f"StudyTask '{task_id}' not found.")
        return self.task_repo.update(db, db_obj=task, obj_in={"status": TaskStatus.SKIPPED})

    def get_pending_tasks(self, db: Session, student_id: str) -> List[StudyTask]:
        """
        Retrieve all pending tasks for a student.

        Args:
            db (Session): Database session.
            student_id (str): Student ID.

        Returns:
            List[StudyTask]: Pending study tasks.
        """
        return self.task_repo.get_pending_tasks(db, student_id=student_id)
