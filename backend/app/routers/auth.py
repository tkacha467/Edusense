"""Authentication endpoints router."""
from typing import Any, Dict
from fastapi import APIRouter, Depends, status, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.firebase import verify_firebase_token
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services import UserService, get_user_service
from app.core.enums import UserStatus

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    authorization: str = Header(..., alias="Authorization"),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Synchronize a newly registered Firebase user into the database.
    Automatically instantiates a linked StudentProfile or FacultyProfile
    based on the assigned role.
    """
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("Invalid token scheme. Expected 'Bearer <token>'.")

    id_token = authorization.split("Bearer ")[1].strip()
    claims = verify_firebase_token(id_token)
    firebase_uid = claims.get("uid")

    if not firebase_uid:
        raise UnauthorizedException("Invalid token claims: Missing UID.")

    user = user_service.register_user(
        db=db,
        firebase_uid=firebase_uid,
        email=user_data.email,
        display_name=user_data.display_name,
        role=user_data.role,
        avatar_url=user_data.avatar_url,
        institution_id=user_data.institution_id,
        department_id=user_data.department_id
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
    if current_user.status == UserStatus.PENDING:
        raise HTTPException(status_code=403, detail="Your account is awaiting administrator approval.")
    if current_user.status == UserStatus.REJECTED:
        raise HTTPException(status_code=403, detail="Your request was rejected. Contact administrator.")
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Your account is inactive.")

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
