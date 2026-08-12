"""Audit repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from typing import Any
from app.repositories.base import BaseRepository
from app.models import AuditLog

class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog model. Append only."""
    
    def __init__(self) -> None:
        """Initialize with AuditLog model."""
        super().__init__(AuditLog)

    def get_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        """Get audit logs by user."""
        stmt = select(AuditLog).where(AuditLog.user_id == user_id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def log_action(
        self,
        db: Session,
        user_id: str,
        action: str,
        entity_type: str = "Resource",
        entity_id: str = "",
        details: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> AuditLog:
        """Create and append an audit log entry."""
        audit = self.model(
            user_id=user_id,
            action=action,
            resource_type=entity_type,
            resource_id=entity_id if entity_id else None,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit)
        db.flush()
        return audit

    def get_by_action(self, db: Session, action: str, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        """Get audit logs by action."""
        stmt = select(AuditLog).where(AuditLog.action == action).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_resource(self, db: Session, resource_type: str, resource_id: str, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        """Get audit logs by resource type and ID."""
        stmt = select(AuditLog).where(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_by_date_range(self, db: Session, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        """Get audit logs in a date range."""
        stmt = select(AuditLog).where(
            AuditLog.created_at >= start_date,
            AuditLog.created_at <= end_date
        ).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def log(
        self,
        db: Session,
        action: str,
        resource_type: str,
        user_id: str | None = None,
        resource_id: str | None = None,
        details: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> AuditLog:
        """Create a new audit log entry."""
        audit_log = self.model(
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        db.flush()
        return audit_log

    def delete(self, db: Session, entity_id: str) -> bool:
        """Override delete to prevent modifying audit logs."""
        raise NotImplementedError("Audit logs cannot be deleted.")

    def update(self, db: Session, entity_id: str, **kwargs: Any) -> AuditLog | None:
        """Override update to prevent modifying audit logs."""
        raise NotImplementedError("Audit logs cannot be updated.")
