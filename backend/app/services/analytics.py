"""Analytics service module."""
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.repositories import (
    StudentActivityRepository,
    AssessmentSessionRepository,
    KnowledgeProfileRepository,
    StudyPlanRepository,
    NotificationRepository
)
from app.models import StudentActivity
from app.core.enums import StudyPlanStatus


class AnalyticsService:
    """Service for handling student analytics, activity logs, and dashboard summaries."""

    def __init__(self) -> None:
        """Initialize AnalyticsService with required repositories."""
        self.activity_repo = StudentActivityRepository()
        self.assessment_repo = AssessmentSessionRepository()
        self.knowledge_repo = KnowledgeProfileRepository()
        self.plan_repo = StudyPlanRepository()
        self.notification_repo = NotificationRepository()

    def log_activity(
        self,
        db: Session,
        student_id: str,
        activity_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        subject_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        duration_seconds: Optional[int] = None
    ) -> StudentActivity:
        """
        Log a new activity for a student.

        Args:
            db (Session): Database session.
            student_id (str): Student ID.
            activity_type (str): Type of activity (e.g., 'assessment_completed', 'video_watched').
            entity_type (Optional[str]): Type of related entity.
            entity_id (Optional[str]): ID of related entity.
            subject_id (Optional[str]): ID of the related subject, if any.
            metadata (Optional[Dict[str, Any]]): Extra activity context.
            duration_seconds (Optional[int]): Time spent on the activity.

        Returns:
            StudentActivity: The created activity log.
        """
        activity_data = {
            "student_id": student_id,
            "activity_type": activity_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "subject_id": subject_id,
            "metadata": metadata,
            "duration_seconds": duration_seconds
        }
        return self.activity_repo.create(db, obj_in=activity_data)

    def get_student_activities(self, db: Session, student_id: str, page: int = 1, page_size: int = 50) -> Tuple[List[StudentActivity], int]:
        """
        Retrieve paginated activity logs for a student.

        Args:
            db (Session): Database session.
            student_id (str): Student ID.
            page (int): Page number.
            page_size (int): Items per page.

        Returns:
            Tuple[List[StudentActivity], int]: The list of activities and total count.
        """
        skip = (page - 1) * page_size
        return self.activity_repo.get_multi_by_student(db, student_id=student_id, skip=skip, limit=page_size)

    def get_activity_summary(self, db: Session, student_id: str) -> Dict[str, Any]:
        """
        Get an aggregate summary of a student's activities.

        Args:
            db (Session): Database session.
            student_id (str): Student ID.

        Returns:
            Dict[str, Any]: A summary dict containing total activities, study time, etc.
        """
        activities, total_activities = self.activity_repo.get_multi_by_student(db, student_id=student_id, skip=0, limit=10000)
        
        study_time_seconds = sum((act.duration_seconds or 0) for act in activities)
        study_time_minutes = study_time_seconds // 60
        
        activity_by_type = {}
        for act in activities:
            activity_by_type[act.activity_type] = activity_by_type.get(act.activity_type, 0) + 1
            
        assessments_completed = activity_by_type.get("assessment_completed", 0)
        skills_practiced = activity_by_type.get("skill_practiced", 0)

        return {
            "total_activities": total_activities,
            "study_time_minutes": study_time_minutes,
            "assessments_completed": assessments_completed,
            "skills_practiced": skills_practiced,
            "activity_by_type": activity_by_type
        }

    def get_weekly_activity(self, db: Session, student_id: str) -> Dict[str, Any]:
        """
        Retrieve activity summaries grouped by day for the last 7 days.

        Args:
            db (Session): Database session.
            student_id (str): Student ID.

        Returns:
            Dict[str, Any]: Activity count and duration per day.
        """
        now = datetime.now(timezone.utc)
        start_of_week = now - timedelta(days=7)
        
        activities = self.activity_repo.get_between_dates(
            db, student_id=student_id, start_date=start_of_week, end_date=now
        )
        
        daily_stats = {}
        # Pre-fill last 7 days
        for i in range(7):
            d_str = (now - timedelta(days=i)).date().isoformat()
            daily_stats[d_str] = {"count": 0, "duration_seconds": 0}
            
        for act in activities:
            if act.created_at:
                d_str = act.created_at.date().isoformat()
                if d_str in daily_stats:
                    daily_stats[d_str]["count"] += 1
                    daily_stats[d_str]["duration_seconds"] += (act.duration_seconds or 0)
                    
        return daily_stats

    def get_dashboard_data(self, db: Session, student_id: str, user_id: str) -> Dict[str, Any]:
        """
        Aggregate comprehensive data for a student's dashboard.

        Args:
            db (Session): Database session.
            student_id (str): Student ID (for learning data).
            user_id (str): User ID (for user-level data like notifications).

        Returns:
            Dict[str, Any]: Consolidated dashboard data.
        """
        recent_assessments, _ = self.assessment_repo.get_history_by_student(db, student_id=student_id, skip=0, limit=5)
        activity_summary = self.get_activity_summary(db, student_id)
        
        profiles = self.knowledge_repo.get_multi_by_student(db, student_id=student_id)
        mastered_count = sum(1 for p in profiles if p.mastered)
        at_risk_count = sum(1 for p in profiles if getattr(p, 'forget_probability', 0.0) >= 0.5)
        
        knowledge_summary = {
            "total_skills": len(profiles),
            "mastered_count": mastered_count,
            "at_risk_count": at_risk_count
        }
        
        active_plans = self.plan_repo.get_multi_by_student_and_status(
            db, student_id=student_id, status=StudyPlanStatus.ACTIVE
        )
        
        unread_notifications = self.notification_repo.count_unread_by_user(db, user_id=user_id)

        return {
            "recent_assessments": recent_assessments,
            "knowledge_summary": knowledge_summary,
            "activity_summary": activity_summary,
            "active_plans_count": len(active_plans),
            "unread_notification_count": unread_notifications
        }
