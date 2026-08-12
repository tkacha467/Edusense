from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBase
from app.schemas.base import BaseResponse

class AuditLogCreate(PydanticBase):
    """Schema for creating an audit log entry."""
    user_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogResponse(BaseResponse):
    """Response schema for an audit log entry."""
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]

class AuditLogFilter(PydanticBase):
    """Schema for filtering audit logs."""
    user_id: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
