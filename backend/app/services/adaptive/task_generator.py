"""Task Generator service for building granular learning tasks."""
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional
from app.core.enums import TaskType, TaskPriority, TaskStatus
from app.models import StudyTask


class TaskGenerator:
    """Factory generating specialized learning tasks with duration, priority, and deadlines."""

    @staticmethod
    def create_task_spec(
        title: str,
        task_type: TaskType,
        priority: TaskPriority = TaskPriority.MEDIUM,
        estimated_minutes: int = 30,
        topic_id: Optional[str] = None,
        skill_id: Optional[str] = None,
        scheduled_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Creates a validated dictionary payload for creating a StudyTask."""
        return {
            "title": title,
            "task_type": task_type,
            "priority": priority,
            "status": TaskStatus.PENDING,
            "estimated_minutes": max(10, estimated_minutes),
            "topic_id": topic_id,
            "skill_id": skill_id,
            "scheduled_date": scheduled_date or datetime.now(timezone.utc).date()
        }
