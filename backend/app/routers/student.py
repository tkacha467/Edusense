"""Student profile and enrolment management router."""
from typing import Any, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.dependencies.auth import get_current_user, require_role
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.student import StudentProfileResponse, StudentProfileUpdate
from app.schemas.learning import StudentSubjectResponse
from app.services import StudentService, get_student_service

router = APIRouter(prefix="/students", tags=["Student Management"])


@router.get("/me/profile", response_model=StudentProfileResponse)
def get_my_profile(
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service)
) -> Any:
    """
    Fetch the currently authenticated student's profile.
    """
    profile = student_service.get_profile_by_user_id(db, user_id=current_user.id)
    return profile


@router.put("/me/profile", response_model=StudentProfileResponse)
def update_my_profile(
    update_data: StudentProfileUpdate,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service)
) -> Any:
    """
    Update the authenticated student's profile parameters.
    """
    profile = student_service.get_profile_by_user_id(db, user_id=current_user.id)
    updated_profile = student_service.update_profile(
        db=db,
        student_id=profile.id,
        **update_data.model_dump(exclude_unset=True)
    )
    return updated_profile


@router.get("/me/subjects", response_model=List[StudentSubjectResponse])
def get_my_enrolled_subjects(
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service)
) -> Any:
    """
    List all subjects in which the student is currently enrolled.
    """
    profile = student_service.get_profile_by_user_id(db, user_id=current_user.id)
    subjects = student_service.get_enrolled_subjects(db, student_id=profile.id)
    return subjects


@router.delete("/me/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll_from_subject(
    subject_id: str,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service)
) -> None:
    """
    Unenroll student from a target subject.
    """
    profile = student_service.get_profile_by_user_id(db, user_id=current_user.id)
    student_service.unenroll_from_subject(db, student_id=profile.id, subject_id=subject_id)
