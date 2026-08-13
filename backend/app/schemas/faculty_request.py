"""Faculty Request schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from app.core.enums import FacultyRequestStatus

class FacultyRequestBase(BaseModel):
    """Base schema for Faculty Request."""
    institution_id: Optional[str] = None
    department_id: Optional[str] = None

class FacultyRequestCreate(FacultyRequestBase):
    """Schema for creating a Faculty Request."""
    pass

class FacultyRequestUpdate(BaseModel):
    """Schema for updating a Faculty Request."""
    status: FacultyRequestStatus
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None

class FacultyRequestReview(BaseModel):
    """Schema for Admin reviewing a Faculty Request."""
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None

class FacultyRequestUserOut(BaseModel):
    """Nested user schema for Faculty Request."""
    email: str
    display_name: str
    model_config = ConfigDict(from_attributes=True)

class FacultyRequestOut(FacultyRequestBase):
    """Schema for outputting a Faculty Request."""
    id: str
    user_id: str
    user: FacultyRequestUserOut
    request_number: int
    status: FacultyRequestStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
