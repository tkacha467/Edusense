"""Learning Timeline service for tracking end-to-end learning event progression."""
from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.models import AuditLog, StudentProfile
from app.repositories import AuditLogRepository, StudentActivityRepository


class LearningTimelineService:
    """Powers student timeline UI, progress analytics, and faculty dashboards."""

    def __init__(self) -> None:
        self.audit_repo = AuditLogRepository()
        self.activity_repo = StudentActivityRepository()

    def record_event(
        self,
        db: Session,
        user_id: str,
        event_name: str,
        entity_type: str,
        entity_id: str,
        details: str | None = None
    ) -> AuditLog:
        """Records a learning timeline milestone event."""
        return self.audit_repo.log_action(
            db,
            user_id=user_id,
            action=event_name,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )

    def get_student_timeline(
        self,
        db: Session,
        user_id: str,
        limit: int = 50
    ) -> List[AuditLog]:
        """Fetches chronological audit timeline events for a student."""
        return self.audit_repo.get_by_user(db, user_id=user_id, limit=limit)
