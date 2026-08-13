"""Dashboard service module for orchestrating dashboard operations."""
import math
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    ProfileSummaryResponse,
    DashboardSummaryResponse,
    KnowledgeHealthResponse,
    KnowledgeHealthPoint,
    RevisionQueueResponse,
    RevisionQueueItem,
    WeakSkillItem,
    RecentActivityItem,
)


class DashboardService:
    """Service layer for computing faculty dashboard insights and analytics."""

    def __init__(self) -> None:
        self.repo = DashboardRepository()

    def get_profile_summary(self, db: Session, user_id: str) -> ProfileSummaryResponse:
        """Fetch faculty identity and department profile details."""
        user, faculty_profile = self.repo.get_faculty_profile(db, user_id=user_id)
        if not user:
            return ProfileSummaryResponse(
                full_name="Faculty Member",
                email="",
                institution="EduSense Platform",
                department="Academic Department",
                designation="Faculty",
                role="faculty"
            )

        full_name = user.display_name or (user.email.split("@")[0] if user.email else "Faculty Member")
        institution = faculty_profile.institution if (faculty_profile and faculty_profile.institution) else "EduSense University"
        department = faculty_profile.department if (faculty_profile and faculty_profile.department) else "Computer Science & AI"
        designation = faculty_profile.designation if (faculty_profile and faculty_profile.designation) else "Professor"

        return ProfileSummaryResponse(
            full_name=full_name,
            email=user.email,
            institution=institution,
            department=department,
            designation=designation,
            role=user.role if isinstance(user.role, str) else user.role.value
        )

    def get_dashboard_summary(self, db: Session) -> DashboardSummaryResponse:
        """Return aggregated platform metrics."""
        metrics = self.repo.get_summary_metrics(db)
        return DashboardSummaryResponse(**metrics)

    def get_knowledge_health(self, db: Session) -> KnowledgeHealthResponse:
        """Return time-series decay and retention points."""
        points_data = self.repo.get_knowledge_health_time_series(db)
        points = [KnowledgeHealthPoint(**p) for p in points_data]
        return KnowledgeHealthResponse(points=points)

    def get_revision_queue(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        sort_by: str = "forget_probability",
        sort_order: str = "desc",
        search: Optional[str] = None,
        priority_filter: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> RevisionQueueResponse:
        """Return paginated revision queue items."""
        raw_items, total = self.repo.get_revision_queue_paginated(
            db,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            priority_filter=priority_filter,
            status_filter=status_filter
        )

        items = [RevisionQueueItem(**item) for item in raw_items]
        pages = math.ceil(total / size) if size > 0 else 0

        return RevisionQueueResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    def get_weak_skills(self, db: Session, limit: int = 5) -> List[WeakSkillItem]:
        """Return top weak skills requiring faculty intervention."""
        raw_skills = self.repo.get_weak_skills(db, limit=limit)
        return [WeakSkillItem(**item) for item in raw_skills]

    def get_recent_activities(self, db: Session, limit: int = 10) -> List[RecentActivityItem]:
        """Return recent learning activity feed."""
        raw_activities = self.repo.get_recent_activities(db, limit=limit)
        return [RecentActivityItem(**item) for item in raw_activities]
