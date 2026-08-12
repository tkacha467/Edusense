from datetime import date
from typing import Optional, Dict
from pydantic import BaseModel as PydanticBase
from app.schemas.base import BaseResponse
from app.core.enums import ActivityType

class StudentActivityCreate(PydanticBase):
    """Schema for creating a student activity record."""
    student_id: str
    activity_type: ActivityType
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    subject_id: Optional[str] = None
    metadata: Optional[dict] = None
    duration_seconds: Optional[int] = None
    activity_date: date

class StudentActivityResponse(BaseResponse):
    """Response schema for a student activity record."""
    student_id: str
    activity_type: ActivityType
    entity_type: Optional[str]
    entity_id: Optional[str]
    subject_id: Optional[str]
    metadata: Optional[dict]
    duration_seconds: Optional[int]
    activity_date: date

class ActivitySummary(PydanticBase):
    """Schema for an aggregated summary of student activities."""
    total_activities: int
    study_time_minutes: int
    assessments_completed: int
    skills_practiced: int
    activity_by_type: Dict[str, int]
