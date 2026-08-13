"""Notification service module."""
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.repositories import NotificationRepository
from app.models import Notification
from app.core.exceptions import NotFoundException
from app.core.enums import NotificationType


class NotificationService:
    """Service for managing user notifications."""

    def __init__(self) -> None:
        """Initialize NotificationService with necessary repositories."""
        self.notification_repo = NotificationRepository()

    def send_notification(
        self,
        db: Session,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: str = 'normal',
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Create and send a notification to a user.

        Args:
            db (Session): Database session.
            user_id (str): User ID to receive the notification.
            title (str): Notification title.
            message (str): Notification body text.
            notification_type (NotificationType): The category of the notification.
            priority (str): Priority level ('low', 'normal', 'high').
            action_url (Optional[str]): Link to action.
            metadata (Optional[Dict[str, Any]]): JSON payload for extra data.

        Returns:
            Notification: The newly created notification entity.
        """
        notif_data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "priority": priority,
            "action_url": action_url,
            "metadata": metadata,
            "is_read": False
        }
        return self.notification_repo.create(db, obj_in=notif_data)

    def get_notifications(self, db: Session, user_id: str, page: int = 1, page_size: int = 20) -> Tuple[List[Notification], int]:
        """
        Retrieve a paginated list of notifications for a user.

        Args:
            db (Session): Database session.
            user_id (str): User ID.
            page (int): Page number.
            page_size (int): Items per page.

        Returns:
            Tuple[List[Notification], int]: Notifications list and total count.
        """
        skip = (page - 1) * page_size
        return self.notification_repo.get_by_user(db, user_id=user_id, skip=skip, limit=page_size), 0

    def get_unread_notifications(self, db: Session, user_id: str) -> List[Notification]:
        """
        Retrieve all unread notifications for a user.

        Args:
            db (Session): Database session.
            user_id (str): User ID.

        Returns:
            List[Notification]: Unread notifications.
        """
        return self.notification_repo.get_unread_by_user(db, user_id=user_id)

    def get_unread_count(self, db: Session, user_id: str) -> int:
        """
        Count the number of unread notifications for a user.

        Args:
            db (Session): Database session.
            user_id (str): User ID.

        Returns:
            int: The unread count.
        """
        return self.notification_repo.get_unread_count(db, user_id=user_id)

    def mark_as_read(self, db: Session, notification_id: str, user_id: str) -> Notification:
        """
        Mark a specific notification as read.

        Args:
            db (Session): Database session.
            notification_id (str): Notification ID.
            user_id (str): ID of the requesting user.

        Returns:
            Notification: The updated notification.
            
        Raises:
            NotFoundException: If not found.
            ForbiddenException: If not owned by user.
        """
        notification = self.notification_repo.get_by_id(db, entity_id=notification_id)
        if not notification:
            raise NotFoundException(f"Notification '{notification_id}' not found.")
        if notification.user_id != user_id:
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException("Notification does not belong to this user.")
        return self.notification_repo.update(db, db_obj=notification, obj_in={"is_read": True})

    def mark_all_as_read(self, db: Session, user_id: str) -> int:
        """
        Mark all unread notifications for a user as read.

        Args:
            db (Session): Database session.
            user_id (str): User ID.

        Returns:
            int: The number of notifications marked as read.
        """
        return self.notification_repo.mark_all_as_read(db, user_id=user_id)

    def send_prediction_alert(self, db: Session, user_id: str, skill_name: str, forget_probability: float) -> Notification:
        """
        Convenience method to send a knowledge decay alert.

        Args:
            db (Session): Database session.
            user_id (str): User ID.
            skill_name (str): Name of the skill at risk.
            forget_probability (float): The calculated probability of forgetting.

        Returns:
            Notification: The sent notification.
        """
        title = "Knowledge Decay Alert"
        message = f"You are at risk of forgetting '{skill_name}'. Your forget probability is {int(forget_probability * 100)}%. Review recommended."
        return self.send_notification(
            db=db,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.DECAY_ALERT,
            priority='high',
            metadata={"skill_name": skill_name, "forget_probability": forget_probability}
        )

    def send_study_reminder(self, db: Session, user_id: str, plan_title: str) -> Notification:
        """
        Convenience method to send a study plan reminder.

        Args:
            db (Session): Database session.
            user_id (str): User ID.
            plan_title (str): Title of the study plan.

        Returns:
            Notification: The sent notification.
        """
        title = "Study Reminder"
        message = f"Don't forget to complete your tasks for your study plan: '{plan_title}'."
        return self.send_notification(
            db=db,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.STUDY_REMINDER,
            priority='normal'
        )
