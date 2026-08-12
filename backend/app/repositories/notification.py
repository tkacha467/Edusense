"""Notification repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, update
from app.repositories.base import BaseRepository
from app.models import Notification
from app.core.enums import NotificationType

class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification model."""
    
    def __init__(self) -> None:
        """Initialize with Notification model."""
        super().__init__(Notification)

    def get_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> list[Notification]:
        """Get notifications for a user."""
        stmt = select(Notification).where(Notification.user_id == user_id).order_by(desc(Notification.created_at)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_unread(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> list[Notification]:
        """Get unread notifications for a user."""
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(desc(Notification.created_at)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    get_unread_by_user = get_unread

    def get_unread_count(self, db: Session, user_id: str) -> int:
        """Get count of unread notifications."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        return db.execute(stmt).scalar_one()

    def mark_as_read(self, db: Session, notification_id: str) -> Notification | None:
        """Mark single notification as read."""
        notification = self.get_by_id(db, notification_id)
        if notification and not notification.is_read:
            notification.is_read = True
            db.flush()
        return notification

    def mark_all_as_read(self, db: Session, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        stmt = update(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).values(is_read=True)
        result = db.execute(stmt)
        db.flush()
        return result.rowcount

    def get_by_type(self, db: Session, user_id: str, notification_type: NotificationType, skip: int = 0, limit: int = 100) -> list[Notification]:
        """Get notifications by type."""
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.notification_type == notification_type
        ).order_by(desc(Notification.created_at)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())
