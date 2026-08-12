from typing import Optional
from pydantic import BaseModel as PydanticBase, Field
from app.schemas.base import BaseResponse
from app.schemas.user import UserPublic

class FacultyProfileCreate(PydanticBase):
    """Schema for creating a faculty profile."""
    user_id: str
    institution: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=100)
    specialization: Optional[str] = None

class FacultyProfileUpdate(PydanticBase):
    """Schema for updating a faculty profile."""
    institution: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=100)
    specialization: Optional[str] = None

class FacultyProfileResponse(BaseResponse):
    """Response schema for a faculty profile."""
    user_id: str
    institution: Optional[str]
    department: Optional[str]
    designation: Optional[str]
    specialization: Optional[str]
    user: Optional[UserPublic] = None
