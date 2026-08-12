"""Standalone Onboarding Wizard Module router."""
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.dependencies.auth import get_current_user, require_role
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.student import StudentProfileResponse, StudentProfileUpdate
from app.schemas.learning import LearningPreferenceCreate, LearningPreferenceUpdate, LearningPreferenceResponse, StudentSubjectResponse
from app.services import StudentService, get_student_service

router = APIRouter(prefix="/onboarding", tags=["Student Onboarding Wizard"])


class InstitutionStepInput(BaseModel):
    """Input payload for Step 1 of onboarding."""
    institution: str = Field(..., max_length=255)
    department: str = Field(..., max_length=255)
    semester: int = Field(..., ge=1, le=12)
    enrollment_year: int = Field(..., ge=2000, le=2030)


class SubjectSelectionInput(BaseModel):
    """Input payload for Step 3 of onboarding."""
    subject_ids: List[str] = Field(..., min_items=1)


@router.get("/status", response_model=Dict[str, Any])
def get_onboarding_status(
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service)
) -> Dict[str, Any]:
    """
    Fetch student's current onboarding status and progress across steps.
    """
    profile = student_service.get_profile_by_user_id(db, user_id=current_user.id)
    prefs = student_service.get_learning_preferences(db, student_id=profile.id)
    enrolled = student_service.get_enrolled_subjects(db, student_id=profile.id)

    step_1_done = bool(profile.institution and profile.department and profile.semester)
    step_2_done = bool(prefs is not None)
    step_3_done = bool(len(enrolled) > 0)

    current_step = 1
    if step_1_done:
        current_step = 2
    if step_1_done and step_2_done:
        current_step = 3
    if step_1_done and step_2_done and step_3_done:
        current_step = 4

    return {
        "onboarding_completed": profile.onboarding_completed,
        "current_step": current_step,
        "steps": {
            "institution_completed": step_1_done,
            "preferences_completed": step_2_done,
            "subjects_completed": step_3_done
        }
    }


@router.put("/institution", response_model=StudentProfileResponse)
def submit_institution_step(
    input_data: InstitutionStepInput,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service)
) -> Any:
    """
    Step 1: Save student institutional and academic details.
    """
    profile = student_service.get_profile_by_user_id(db, user_id=current_user.id)
    updated_profile = student_service.update_profile(
        db=db,
        student_id=profile.id,
        institution=input_data.institution,
        department=input_data.department,
        semester=input_data.semester,
        enrollment_year=input_data.enrollment_year
    )
    return updated_profile


@router.put("/preferences", response_model=LearningPreferenceResponse)
def submit_preferences_step(
    input_data: LearningPreferenceUpdate,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service)
) -> Any:
    """
    Step 2: Save student learning style, target study hours, and difficulty.
    """
    profile = student_service.get_profile_by_user_id(db, user_id=current_user.id)
    prefs = student_service.set_learning_preferences(
        db=db,
        student_id=profile.id,
        learning_style=input_data.learning_style,
        weekly_study_hours=input_data.weekly_study_hours,
        preferred_difficulty=input_data.preferred_difficulty,
        preferred_session_length=input_data.preferred_session_length,
        target_score=input_data.target_score
    )
    return prefs


@router.post("/subjects", response_model=List[StudentSubjectResponse])
def submit_subjects_step(
    input_data: SubjectSelectionInput,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service)
) -> Any:
    """
    Step 3: Enroll student in initial baseline target subjects.
    """
    profile = student_service.get_profile_by_user_id(db, user_id=current_user.id)
    enrolled = student_service.enroll_in_subjects(
        db=db,
        student_id=profile.id,
        subject_ids=input_data.subject_ids
    )
    return enrolled


@router.post("/complete", response_model=Dict[str, Any])
def complete_onboarding(
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service)
) -> Dict[str, Any]:
    """
    Step 4: Finalize wizard and lock student onboarding state.
    """
    profile = student_service.get_profile_by_user_id(db, user_id=current_user.id)
    completed_profile = student_service.complete_onboarding(db, student_id=profile.id)
    
    return {
        "message": "Onboarding completed successfully.",
        "onboarding_completed": completed_profile.onboarding_completed,
        "student_id": completed_profile.id
    }
