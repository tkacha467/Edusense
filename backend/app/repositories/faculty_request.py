"""Faculty Request repository."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.faculty_request import FacultyRequest
from app.core.enums import FacultyRequestStatus

class FacultyRequestRepository:
    """Repository for managing FacultyRequest entities."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, request_id: str) -> Optional[FacultyRequest]:
        """Get a faculty request by ID."""
        return self.db.query(FacultyRequest).filter(FacultyRequest.id == request_id).first()

    def get_by_user_id(self, user_id: str) -> Optional[FacultyRequest]:
        """Get the latest faculty request for a user."""
        return self.db.query(FacultyRequest).filter(FacultyRequest.user_id == user_id).order_by(FacultyRequest.created_at.desc()).first()

    def get_pending_requests(self) -> List[FacultyRequest]:
        """Get all pending faculty requests."""
        return self.db.query(FacultyRequest).options(joinedload(FacultyRequest.user)).filter(FacultyRequest.status == FacultyRequestStatus.PENDING).order_by(FacultyRequest.created_at.asc()).all()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[FacultyRequest]:
        """Get all faculty requests with pagination."""
        return self.db.query(FacultyRequest).options(joinedload(FacultyRequest.user)).order_by(FacultyRequest.created_at.desc()).offset(offset).limit(limit).all()

    def create(self, request: FacultyRequest) -> FacultyRequest:
        """Create a new faculty request."""
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def update(self, request: FacultyRequest) -> FacultyRequest:
        """Update an existing faculty request."""
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
