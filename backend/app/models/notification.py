"""Notification models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Index, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, GUID
from app.core.enums import NotificationType, NotificationPriority

class Notification(BaseModel):
    """Notification model."""
    __tablename__ = 'notifications'

    user_id: Mapped[str] = mapped_column(GUID(), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType), nullable=False)
    priority: Mapped[NotificationPriority] = mapped_column(SAEnum(NotificationPriority), nullable=False, default=NotificationPriority.NORMAL)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    action_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)

    __table_args__ = (
        Index('ix_notif_user_read', 'user_id', 'is_read'),
    )

    user: Mapped["User"] = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.notification_type}')>"
