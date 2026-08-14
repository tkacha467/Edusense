from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel as PydanticBase, Field, model_validator
from app.schemas.base import BaseResponse
from app.core.enums import NotificationType, NotificationPriority
import json

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

    @model_validator(mode="before")
    @classmethod
    def map_metadata(cls, data: Any) -> Any:
        if not isinstance(data, dict) and hasattr(data, "metadata_json"):
            meta_dict = None
            if data.metadata_json:
                try:
                    meta_dict = json.loads(data.metadata_json)
                except Exception:
                    meta_dict = {}
            return {
                "id": str(data.id),
                "created_at": data.created_at,
                "updated_at": data.updated_at,
                "user_id": str(data.user_id),
                "title": data.title,
                "message": data.message,
                "notification_type": data.notification_type,
                "priority": data.priority,
                "action_url": data.action_url,
                "metadata": meta_dict,
                "is_read": data.is_read,
                "read_at": data.read_at
            }
        return data

class NotificationBatchRead(PydanticBase):
    """Schema for marking a batch of notifications as read."""
    notification_ids: List[str]

class NotificationUnreadCountResponse(PydanticBase):
    """Schema for unread count response."""
    unread_count: int
