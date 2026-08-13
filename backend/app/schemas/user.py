from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBase, Field, ConfigDict
from app.schemas.base import BaseResponse
from app.core.enums import UserRole, UserStatus

class UserCreate(PydanticBase):
    """Schema for creating a new user."""
    firebase_uid: str = Field(min_length=1, max_length=128)
    email: str = Field(max_length=255, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    display_name: str = Field(min_length=1, max_length=150)
    role: UserRole
    avatar_url: Optional[str] = None
    institution_id: Optional[str] = None
    department_id: Optional[str] = None

class UserUpdate(PydanticBase):
    """Schema for updating an existing user."""
    display_name: Optional[str] = Field(None, max_length=150)
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_email_verified: Optional[bool] = None

class UserPublic(PydanticBase):
    """Public user profile schema with limited fields."""
    id: str
    display_name: str
    role: UserRole
    avatar_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseResponse):
    """Full user response schema."""
    firebase_uid: str
    email: str
    display_name: str
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str]
    is_active: bool
    is_email_verified: bool
    last_login_at: Optional[datetime]
    deleted_at: Optional[datetime]
