"""Admin Analytics service."""
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.models.faculty_request import FacultyRequest
from app.core.enums import FacultyRequestStatus

class AdminAnalyticsService:
    """Service for gathering administrative metrics and analytics."""

    @staticmethod
    def get_faculty_approval_metrics(db: Session) -> Dict[str, Any]:
        """Gather metrics for the faculty approval dashboard."""
        now = datetime.utcnow()
        start_of_day = datetime(now.year, now.month, now.day)
        seven_days_ago = now - timedelta(days=7)

        # Pending count
        pending_count = db.query(func.count(FacultyRequest.id)).filter(FacultyRequest.status == FacultyRequestStatus.PENDING).scalar()

        # Approved today
        approved_today = db.query(func.count(FacultyRequest.id)).filter(
            and_(
                FacultyRequest.status == FacultyRequestStatus.APPROVED,
                FacultyRequest.reviewed_at >= start_of_day
            )
        ).scalar()

        # Rejected today
        rejected_today = db.query(func.count(FacultyRequest.id)).filter(
            and_(
                FacultyRequest.status == FacultyRequestStatus.REJECTED,
                FacultyRequest.reviewed_at >= start_of_day
            )
        ).scalar()

        # Pending > 7 days
        pending_old = db.query(func.count(FacultyRequest.id)).filter(
            and_(
                FacultyRequest.status == FacultyRequestStatus.PENDING,
                FacultyRequest.submitted_at <= seven_days_ago
            )
        ).scalar()

        # Simple Python-side average calculation:
        approved_reqs = db.query(FacultyRequest.submitted_at, FacultyRequest.reviewed_at).filter(FacultyRequest.status == FacultyRequestStatus.APPROVED).all()
        
        avg_approval_time_hours = 0
        if approved_reqs:
            total_seconds = sum(
                (req.reviewed_at - req.submitted_at).total_seconds() 
                for req in approved_reqs if req.reviewed_at and req.submitted_at
            )
            avg_approval_time_hours = (total_seconds / len(approved_reqs)) / 3600

        return {
            "pending_requests": pending_count,
            "approved_today": approved_today,
            "rejected_today": rejected_today,
            "pending_over_7_days": pending_old,
            "avg_approval_time_hours": round(avg_approval_time_hours, 1)
        }
