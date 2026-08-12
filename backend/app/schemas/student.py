from typing import Optional
from pydantic import BaseModel as PydanticBase, Field
from app.schemas.base import BaseResponse
from app.schemas.user import UserPublic

class StudentProfileCreate(PydanticBase):
    """Schema for creating a student profile."""
    user_id: str
    institution: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    semester: Optional[int] = Field(None, ge=1, le=12)
    enrollment_year: Optional[int] = None
    learning_goal: Optional[str] = None
    preferred_language: str = Field('en', max_length=10)

class StudentProfileUpdate(PydanticBase):
    """Schema for updating a student profile."""
    institution: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    semester: Optional[int] = Field(None, ge=1, le=12)
    enrollment_year: Optional[int] = None
    learning_goal: Optional[str] = None
    preferred_language: Optional[str] = Field(None, max_length=10)
    onboarding_completed: Optional[bool] = None

class StudentProfileResponse(BaseResponse):
    """Response schema for a student profile."""
    user_id: str
    institution: Optional[str]
    department: Optional[str]
    semester: Optional[int]
    enrollment_year: Optional[int]
    learning_goal: Optional[str]
    preferred_language: str
    onboarding_completed: bool
    user: Optional[UserPublic] = None

class StudentDashboardResponse(PydanticBase):
    """Dashboard summary response schema for a student."""
    profile: StudentProfileResponse
    knowledge_summary: dict
    recent_assessments: list[dict]
    active_study_plans: int
    unread_notifications: int
