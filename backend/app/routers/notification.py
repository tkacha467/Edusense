"""Notification REST API router."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models import User
from app.repositories import NotificationRepository
from app.schemas.notification import NotificationResponse, NotificationUnreadCountResponse
from app.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications Engine"])

def get_notification_service() -> NotificationService: return NotificationService()

@router.get("/me", response_model=List[NotificationResponse])
def get_user_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    notif_service: NotificationService = Depends(get_notification_service)
) -> Any:
    """List all notifications for current user."""
    # Using get_notifications to get all notifications. It returns a tuple of (items, total)
    # The router previously just returned a list. Let's return items.
    items, _ = notif_service.get_notifications(db, user_id=current_user.id, page=1, page_size=100)
    return items


@router.get("/unread-count", response_model=NotificationUnreadCountResponse)
def get_unread_notification_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    notif_service: NotificationService = Depends(get_notification_service)
) -> Any:
    """Get count of unread notifications."""
    count = notif_service.get_unread_count(db, user_id=current_user.id)
    return {"unread_count": count}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    notif_service: NotificationService = Depends(get_notification_service)
) -> Any:
    """Mark a notification as read."""
    notif = notif_service.mark_as_read(db, notification_id=notification_id)
    if notif.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.commit()
    return notif


@router.put("/read-all", response_model=dict)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    notif_service: NotificationService = Depends(get_notification_service)
) -> Any:
    """Mark all notifications as read for current user."""
    count = notif_service.mark_all_as_read(db, user_id=current_user.id)
    db.commit()
    return {"updated_count": count}
