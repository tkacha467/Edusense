"""Admin endpoints router."""
from typing import List, Any
from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import RequireAdmin
from app.models.user import User
from app.schemas.faculty_request import FacultyRequestOut, FacultyRequestReview
from app.services.faculty_request import FacultyRequestService
from app.services.admin_analytics import AdminAnalyticsService

router = APIRouter(prefix="/admin", tags=["Admin"])
faculty_service = FacultyRequestService()

@router.get("/faculty-requests", response_model=List[FacultyRequestOut])
def list_faculty_requests(
    limit: int = 100,
    offset: int = 0,
    status_filter: str = None,
    current_user: User = Depends(RequireAdmin),
    db: Session = Depends(get_db)
) -> Any:
    """Get a list of faculty requests."""
    if status_filter == "pending":
        return faculty_service.get_pending_requests(db)
    return faculty_service.get_all_requests(db, limit, offset)


@router.post("/faculty-requests/{request_id}/approve", response_model=FacultyRequestOut)
def approve_faculty_request(
    request_id: str,
    review_data: FacultyRequestReview,
    current_user: User = Depends(RequireAdmin),
    db: Session = Depends(get_db)
) -> Any:
    """Approve a faculty request."""
    return faculty_service.approve_request(db, request_id, current_user.id, review_data)


@router.post("/faculty-requests/{request_id}/reject", response_model=FacultyRequestOut)
def reject_faculty_request(
    request_id: str,
    review_data: FacultyRequestReview,
    current_user: User = Depends(RequireAdmin),
    db: Session = Depends(get_db)
) -> Any:
    """Reject a faculty request."""
    return faculty_service.reject_request(db, request_id, current_user.id, review_data)


@router.get("/analytics/faculty-approvals")
def get_faculty_approval_analytics(
    current_user: User = Depends(RequireAdmin),
    db: Session = Depends(get_db)
) -> Any:
    """Get metrics for the faculty approval dashboard."""
    return AdminAnalyticsService.get_faculty_approval_metrics(db)
