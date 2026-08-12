"""Authentication endpoints router."""
from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.firebase import verify_firebase_token
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services import UserService, get_user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Synchronize a newly registered Firebase user into the database.
    Automatically instantiates a linked StudentProfile or FacultyProfile
    based on the assigned role.
    """
    user = user_service.register_user(
        db=db,
        firebase_uid=user_data.firebase_uid,
        email=user_data.email,
        display_name=user_data.display_name,
        role=user_data.role,
        avatar_url=user_data.avatar_url
    )
    return user


@router.post("/login", response_model=Dict[str, Any])
def record_login(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    Record user login activity and return authenticated user session context.
    """
    user = user_service.record_login(db, user_id=current_user.id)
    
    profile_id = None
    onboarding_completed = False
    
    if user.student_profile:
        profile_id = user.student_profile.id
        onboarding_completed = user.student_profile.onboarding_completed
    elif user.faculty_profile:
        profile_id = user.faculty_profile.id
        onboarding_completed = True

    return {
        "user": UserResponse.model_validate(user),
        "profile_id": profile_id,
        "onboarding_completed": onboarding_completed,
        "role": user.role
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Fetch identity details of the currently authenticated user.
    """
    return current_user
