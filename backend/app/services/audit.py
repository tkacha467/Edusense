"""Audit log service module."""
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.repositories import AuditLogRepository
from app.models import AuditLog


class AuditService:
    """Service for logging critical system actions and maintaining an audit trail."""

    def __init__(self) -> None:
        """Initialize AuditService with AuditLogRepository."""
        self.audit_repo = AuditLogRepository()

    def log(
        self,
        db: Session,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Record a new audit log entry.

        Args:
            db (Session): Database session.
            action (str): The action performed (e.g., 'UPDATE', 'DELETE', 'LOGIN').
            resource_type (str): Type of resource affected (e.g., 'User', 'Assessment').
            user_id (Optional[str]): ID of the user performing the action.
            resource_id (Optional[str]): ID of the resource affected.
            details (Optional[Dict[str, Any]]): JSON payload with extra details or diffs.
            ip_address (Optional[str]): IP address of the requester.
            user_agent (Optional[str]): User agent of the requester.

        Returns:
            AuditLog: The created audit log entity.
        """
        log_data = {
            "action": action,
            "resource_type": resource_type,
            "user_id": user_id,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        return self.audit_repo.create(db, obj_in=log_data)

    def get_logs(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 50,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> Tuple[List[AuditLog], int]:
        """
        Retrieve paginated and optionally filtered audit logs.

        Args:
            db (Session): Database session.
            page (int): Page number.
            page_size (int): Items per page.
            user_id (Optional[str]): Filter by user.
            action (Optional[str]): Filter by action.
            resource_type (Optional[str]): Filter by resource type.

        Returns:
            Tuple[List[AuditLog], int]: The list of audit logs and total count.
        """
        skip = (page - 1) * page_size
        return self.audit_repo.get_filtered_logs(
            db, 
            user_id=user_id, 
            action=action, 
            resource_type=resource_type, 
            skip=skip, 
            limit=page_size
        )

    def get_user_audit_trail(self, db: Session, user_id: str, page: int = 1, page_size: int = 50) -> Tuple[List[AuditLog], int]:
        """
        Retrieve all actions performed by a specific user.

        Args:
            db (Session): Database session.
            user_id (str): User ID.
            page (int): Page number.
            page_size (int): Items per page.

        Returns:
            Tuple[List[AuditLog], int]: The list of audit logs and total count.
        """
        return self.get_logs(db, page=page, page_size=page_size, user_id=user_id)

    def get_resource_history(self, db: Session, resource_type: str, resource_id: str) -> List[AuditLog]:
        """
        Retrieve the entire audit history for a specific resource.

        Args:
            db (Session): Database session.
            resource_type (str): Type of resource.
            resource_id (str): ID of the resource.

        Returns:
            List[AuditLog]: List of all related audit logs.
        """
        # Fetching all without pagination since it's a specific resource history
        logs, _ = self.audit_repo.get_filtered_logs(
            db,
            resource_type=resource_type,
            resource_id=resource_id,
            skip=0,
            limit=1000
        )
        return logs
