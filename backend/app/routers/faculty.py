"""Faculty profile and teaching portfolio management router."""
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.dependencies.auth import get_current_user, require_role
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.faculty import FacultyProfileCreate, FacultyProfileResponse, FacultyProfileUpdate
from app.schemas.learning import FacultySubjectResponse
from app.schemas.student import StudentProfileResponse
from app.schemas.base import PaginatedResponse
from app.services import FacultyService, get_faculty_service, StudentService, get_student_service

router = APIRouter(prefix="/faculty", tags=["Faculty Management"])


class FacultySubjectAssignmentInput(BaseModel):
    """Input payload for assigning teaching subjects."""
    subject_ids: List[str] = Field(..., min_items=1)


@router.get("/me/profile", response_model=FacultyProfileResponse)
def get_my_faculty_profile(
    current_user: User = Depends(require_role(UserRole.FACULTY)),
    db: Session = Depends(get_db),
    faculty_service: FacultyService = Depends(get_faculty_service)
) -> Any:
    """
    Fetch the currently authenticated faculty member's profile.
    """
    profile = faculty_service.get_profile_by_user_id(db, user_id=current_user.id)
    return profile


@router.put("/me/profile", response_model=FacultyProfileResponse)
def update_my_faculty_profile(
    update_data: FacultyProfileUpdate,
    current_user: User = Depends(require_role(UserRole.FACULTY)),
    db: Session = Depends(get_db),
    faculty_service: FacultyService = Depends(get_faculty_service)
) -> Any:
    """
    Update the authenticated faculty member's profile attributes.
    """
    profile = faculty_service.get_profile_by_user_id(db, user_id=current_user.id)
    updated_profile = faculty_service.update_profile(
        db=db,
        faculty_id=profile.id,
        **update_data.model_dump(exclude_unset=True)
    )
    return updated_profile


@router.post("/me/subjects", response_model=List[FacultySubjectResponse])
def assign_teaching_subjects(
    input_data: FacultySubjectAssignmentInput,
    current_user: User = Depends(require_role(UserRole.FACULTY)),
    db: Session = Depends(get_db),
    faculty_service: FacultyService = Depends(get_faculty_service)
) -> Any:
    """
    Assign subjects to the faculty member's teaching portfolio.
    """
    profile = faculty_service.get_profile_by_user_id(db, user_id=current_user.id)
    assignments = faculty_service.assign_subjects(
        db=db,
        faculty_id=profile.id,
        subject_ids=input_data.subject_ids
    )
    return assignments


@router.get("/students", response_model=PaginatedResponse[StudentProfileResponse])
def list_enrolled_students(
    subject_id: Optional[str] = Query(None, description="Filter students by assigned subject ID"),
    search: Optional[str] = Query(None, description="Search query for student institution or department"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db),
    faculty_service: FacultyService = Depends(get_faculty_service),
    student_service: StudentService = Depends(get_student_service)
) -> Any:
    """
    Search and list students enrolled in the faculty member's assigned teaching subjects.
    """
    faculty_profile = faculty_service.get_profile_by_user_id(db, user_id=current_user.id)
    assigned_subjects = faculty_service.get_assigned_subjects(db, faculty_id=faculty_profile.id)
    
    assigned_subject_ids = [fs.subject_id for fs in assigned_subjects]
    
    if subject_id and subject_id in assigned_subject_ids:
        target_subject_ids = [subject_id]
    else:
        target_subject_ids = assigned_subject_ids

    # Query students enrolled in target subjects
    from sqlalchemy import select, func
    from app.models.student import StudentProfile
    from app.models.learning import StudentSubject

    stmt = select(StudentProfile).join(StudentSubject).where(
        StudentSubject.subject_id.in_(target_subject_ids)
    )
    if search:
        stmt = stmt.where(
            (StudentProfile.institution.ilike(f"%{search}%")) |
            (StudentProfile.department.ilike(f"%{search}%"))
        )

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(total_stmt).scalar() or 0

    stmt = stmt.distinct().offset((page - 1) * page_size).limit(page_size)
    students = db.execute(stmt).scalars().all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return {
        "items": [StudentProfileResponse.model_validate(s) for s in students],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/analytics/overview")
def get_faculty_class_overview(
    subject_id: Optional[str] = Query(None, description="Optional subject filter"),
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db),
    faculty_service: FacultyService = Depends(get_faculty_service)
) -> Any:
    """
    Fetch comprehensive class-wide analytics overview for faculty dashboard.
    """
    faculty_profile = faculty_service.get_profile_by_user_id(db, user_id=current_user.id)
    return faculty_service.get_class_analytics_overview(
        db=db,
        faculty_id=faculty_profile.id,
        subject_id=subject_id
    )


@router.get("/students/{student_id}/analytics")
def get_student_deep_dive_analytics(
    student_id: str,
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db),
    faculty_service: FacultyService = Depends(get_faculty_service)
) -> Any:
    """
    Fetch deep-dive knowledge retention, decay forecasts, and recommendations for a single student.
    """
    return faculty_service.get_student_deep_dive_analytics(
        db=db,
        student_id=student_id
    )


@router.get("/students/{student_id}/risk-profile")
def get_student_risk_profile(
    student_id: str,
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch authorized student knowledge decay risk profile and ML predictions for faculty inspection.
    """
    from app.services.knowledge_decay_prediction import get_prediction_service
    pred_service = get_prediction_service()
    prediction = pred_service.predict_forgetting_risk(db=db, student_id=student_id)
    return prediction


@router.get("/analytics/risk-heatmap")
def get_cohort_risk_heatmap(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch cohort risk matrix populated with live ML Knowledge Decay predictions.
    """
    from app.services.revision_recommendation import get_revision_engine
    engine = get_revision_engine()
    heatmap = engine.generate_cohort_risk_heatmap(db, faculty_user_id=current_user.id)
    return heatmap


@router.get("/analytics/intervention-effectiveness")
def get_faculty_intervention_effectiveness(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch cohort-wide recommendation outcome & intervention effectiveness metrics for faculty analytics.
    """
    from app.services.revision_outcome_service import get_outcome_service
    service = get_outcome_service()
    metrics = service.get_faculty_intervention_effectiveness(db, faculty_user_id=current_user.id)
    return metrics


@router.get("/students/{student_id}/intervention-history")
def get_student_intervention_history(
    student_id: str,
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch student intervention history and learning outcome metrics for faculty deep-dive inspection.
    """
    from app.services.revision_outcome_service import get_outcome_service
    service = get_outcome_service()
    history = service.get_student_effectiveness(db, student_id=student_id)
    return history


@router.get("/analytics/cohort-skills")
def get_faculty_cohort_skills_analytics(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch skill-level cohort weakness summary for faculty curriculum planning.
    """
    from app.services.analytics import AnalyticsService
    service = AnalyticsService()
    return service.get_cohort_skill_analytics(db)


@router.get("/analytics/research")
def get_research_intelligence_analytics(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch research monitoring metrics and model intelligence analytics.
    """
    from app.services.analytics import AnalyticsService
    service = AnalyticsService()
    return service.get_research_analytics_summary(db)
