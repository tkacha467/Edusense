"""Dashboard endpoints router for Faculty Analytics."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, RequireFaculty
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.dashboard import (
    ProfileSummaryResponse,
    DashboardSummaryResponse,
    KnowledgeHealthResponse,
    RevisionQueueResponse,
    WeakSkillItem,
    RecentActivityItem,
)
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service() -> DashboardService:
    """Dependency provider for DashboardService."""
    return DashboardService()


@router.get(
    "/profile-summary",
    response_model=ProfileSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get faculty profile header summary"
)
def get_profile_summary(
    current_user: User = Depends(RequireFaculty),
    db: Session = Depends(get_db),
    service: DashboardService = Depends(get_dashboard_service)
) -> ProfileSummaryResponse:
    """Fetch current faculty user's name, institution, department, and role details."""
    return service.get_profile_summary(db, user_id=current_user.id)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get high-level summary metrics"
)
def get_dashboard_summary(
    current_user: User = Depends(RequireFaculty),
    db: Session = Depends(get_db),
    service: DashboardService = Depends(get_dashboard_service)
) -> DashboardSummaryResponse:
    """Fetch total students, total skills, high risk count, pending revisions, etc."""
    return service.get_dashboard_summary(db)


@router.get(
    "/knowledge-health",
    response_model=KnowledgeHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get knowledge health time-series"
)
def get_knowledge_health(
    current_user: User = Depends(RequireFaculty),
    db: Session = Depends(get_db),
    service: DashboardService = Depends(get_dashboard_service)
) -> KnowledgeHealthResponse:
    """Fetch daily time-series retention and forget probability data."""
    return service.get_knowledge_health(db)


@router.get(
    "/revision-queue",
    response_model=RevisionQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Get paginated student revision queue"
)
def get_revision_queue(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("forget_probability", description="Sort field (forget_probability, student_name, skill_name)"),
    sort_order: str = Query("desc", description="Sort direction (asc, desc)"),
    search: Optional[str] = Query(None, description="Search by student name, email, or skill"),
    priority_filter: Optional[str] = Query(None, description="Filter by priority (HIGH, MEDIUM, LOW)"),
    status_filter: Optional[str] = Query(None, description="Filter by status (PENDING, COMPLETED)"),
    current_user: User = Depends(RequireFaculty),
    db: Session = Depends(get_db),
    service: DashboardService = Depends(get_dashboard_service)
) -> RevisionQueueResponse:
    """Fetch paginated, filterable student knowledge profile items requiring revision."""
    return service.get_revision_queue(
        db=db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        priority_filter=priority_filter,
        status_filter=status_filter
    )


@router.get(
    "/weak-skills",
    response_model=List[WeakSkillItem],
    status_code=status.HTTP_200_OK,
    summary="Get weak skills list"
)
def get_weak_skills(
    limit: int = Query(5, ge=1, le=20, description="Max items to return"),
    current_user: User = Depends(RequireFaculty),
    db: Session = Depends(get_db),
    service: DashboardService = Depends(get_dashboard_service)
) -> List[WeakSkillItem]:
    """Fetch skills with lowest average mastery or highest forget probability."""
    return service.get_weak_skills(db, limit=limit)


@router.get(
    "/recent-activities",
    response_model=List[RecentActivityItem],
    status_code=status.HTTP_200_OK,
    summary="Get recent student activity stream"
)
def get_recent_activities(
    limit: int = Query(10, ge=1, le=50, description="Max activities to return"),
    current_user: User = Depends(RequireFaculty),
    db: Session = Depends(get_db),
    service: DashboardService = Depends(get_dashboard_service)
) -> List[RecentActivityItem]:
    """Fetch recent learning activities logged across all students."""
    return service.get_recent_activities(db, limit=limit)
