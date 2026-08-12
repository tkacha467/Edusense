"""Notification Engine for automated adaptive alerts and reminders."""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.enums import NotificationType, NotificationPriority
from app.models import Notification, StudentProfile, StudyTask
from app.repositories import NotificationRepository

class AdaptiveNotificationEngine:
    """Automated notification dispatch for decay alerts, study reminders, missed tasks, and streaks."""

    def __init__(self) -> None:
        self.notif_repo = NotificationRepository()

    def send_decay_alert(
        self,
        db: Session,
        user_id: str,
        skill_name: str,
        forget_probability: float
    ) -> Notification:
        """Dispatches high decay probability alert."""
        return self.notif_repo.create(
            db,
            user_id=user_id,
            title="Knowledge Decay Alert!",
            message=f"High forgetting risk ({int(forget_probability * 100)}%) detected for '{skill_name}'. Revision recommended today.",
            notification_type=NotificationType.PREDICTION_ALERT.value,
            priority=NotificationPriority.HIGH.value
        )

    def send_daily_tasks_reminder(
        self,
        db: Session,
        user_id: str,
        task_count: int
    ) -> Notification:
        """Dispatches daily study plan tasks reminder."""
        return self.notif_repo.create(
            db,
            user_id=user_id,
            title="Today's Study Schedule Ready",
            message=f"You have {task_count} study tasks scheduled for today. Keep your learning momentum going!",
            notification_type=NotificationType.STUDY_REMINDER.value,
            priority=NotificationPriority.NORMAL.value
        )

    def send_missed_tasks_alert(
        self,
        db: Session,
        user_id: str,
        missed_count: int
    ) -> Notification:
        """Dispatches alert for overdue study tasks."""
        return self.notif_repo.create(
            db,
            user_id=user_id,
            title="Overdue Study Tasks",
            message=f"You have {missed_count} missed study tasks from previous days. Catch up to prevent retention loss.",
            notification_type=NotificationType.STUDY_REMINDER.value,
            priority=NotificationPriority.HIGH.value
        )

    def send_streak_achievement(
        self,
        db: Session,
        user_id: str,
        streak_days: int
    ) -> Notification:
        """Dispatches streak milestone achievement notification."""
        return self.notif_repo.create(
            db,
            user_id=user_id,
            title="Study Streak Milestone!",
            message=f"Congratulations! You've maintained a {streak_days}-day study streak. Fantastic dedication!",
            notification_type=NotificationType.ACHIEVEMENT.value,
            priority=NotificationPriority.NORMAL.value
        )
