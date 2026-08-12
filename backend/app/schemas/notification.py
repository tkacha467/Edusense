from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel as PydanticBase, Field
from app.schemas.base import BaseResponse
from app.core.enums import NotificationType, NotificationPriority

class NotificationCreate(PydanticBase):
    """Schema for creating a notification."""
    user_id: str
    title: str = Field(..., max_length=255)
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_url: Optional[str] = None
    metadata: Optional[dict] = None

class NotificationUpdate(PydanticBase):
    """Schema for updating a notification (e.g. marking as read)."""
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None

class NotificationResponse(BaseResponse):
    """Response schema for a notification."""
    user_id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    action_url: Optional[str]
    metadata: Optional[dict]
    is_read: bool
    read_at: Optional[datetime]

class NotificationBatchRead(PydanticBase):
    """Schema for marking a batch of notifications as read."""
    notification_ids: List[str]

class NotificationUnreadCountResponse(PydanticBase):
    """Schema for unread count response."""
    unread_count: int
