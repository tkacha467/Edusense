"""Faculty Request service."""
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.models.faculty_request import FacultyRequest
from app.repositories.faculty_request import FacultyRequestRepository
from app.core.enums import FacultyRequestStatus
from app.core.events import EventDispatcher
from app.schemas.faculty_request import FacultyRequestCreate, FacultyRequestReview
from app.services.user import UserService
from app.core.enums import UserStatus

class FacultyRequestService:
    """Service for managing faculty requests and approval workflow."""

    def __init__(self):
        # Service is stateless, dependencies injected via methods
        pass

    def get_request(self, db: Session, request_id: str) -> FacultyRequest:
        """Get a specific request."""
        repo = FacultyRequestRepository(db)
        request = repo.get(request_id)
        if not request:
            raise ValueError(f"Faculty request {request_id} not found")
        return request
    
    def get_all_requests(self, db: Session, limit: int = 100, offset: int = 0) -> List[FacultyRequest]:
        """Get all requests."""
        repo = FacultyRequestRepository(db)
        return repo.get_all(limit, offset)

    def get_pending_requests(self, db: Session) -> List[FacultyRequest]:
        """Get pending requests."""
        repo = FacultyRequestRepository(db)
        return repo.get_pending_requests()

    def submit_request(self, db: Session, user_id: str, data: FacultyRequestCreate) -> FacultyRequest:
        """Submit a new faculty request or resubmit an existing one."""
        repo = FacultyRequestRepository(db)
        
        # Check if user already has a request
        existing_request = repo.get_by_user_id(user_id)
        
        if existing_request:
            if existing_request.status == FacultyRequestStatus.PENDING:
                raise ValueError("User already has a pending faculty request.")
            if existing_request.status == FacultyRequestStatus.APPROVED:
                raise ValueError("User is already an approved faculty.")
            
            # Resubmit rejected request
            existing_request.status = FacultyRequestStatus.PENDING
            existing_request.request_number += 1
            existing_request.submitted_at = datetime.utcnow()
            existing_request.reviewed_at = None
            existing_request.reviewed_by = None
            existing_request.review_notes = None
            existing_request.rejection_reason = None
            if data.institution_id:
                existing_request.institution_id = data.institution_id
            if data.department_id:
                existing_request.department_id = data.department_id
            
            return repo.update(existing_request)
        
        # Create new request
        new_request = FacultyRequest(
            user_id=user_id,
            institution_id=data.institution_id,
            department_id=data.department_id,
            status=FacultyRequestStatus.PENDING,
            request_number=1
        )
        return repo.create(new_request)

    def approve_request(self, db: Session, request_id: str, reviewer_id: str, review_data: FacultyRequestReview) -> FacultyRequest:
        """Approve a faculty request."""
        repo = FacultyRequestRepository(db)
        request = repo.get(request_id)
        
        if not request:
            raise ValueError("Request not found.")
        
        if request.status != FacultyRequestStatus.PENDING:
            raise ValueError(f"Cannot approve request with status {request.status}")
            
        request.status = FacultyRequestStatus.APPROVED
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.utcnow()
        request.review_notes = review_data.notes
        
        updated_request = repo.update(request)
        
        # Update user status
        user_service = UserService()
        user_service.update_user(db, request.user_id, status=UserStatus.ACTIVE, is_active=True)
        
        # Fire Domain Event
        EventDispatcher.dispatch("FacultyApproved", db, request.id, reviewer_id)
        
        return updated_request

    def reject_request(self, db: Session, request_id: str, reviewer_id: str, review_data: FacultyRequestReview) -> FacultyRequest:
        """Reject a faculty request."""
        repo = FacultyRequestRepository(db)
        request = repo.get(request_id)
        
        if not request:
            raise ValueError("Request not found.")
            
        if request.status != FacultyRequestStatus.PENDING:
            raise ValueError(f"Cannot reject request with status {request.status}")
            
        if not review_data.rejection_reason:
            raise ValueError("Rejection reason is required.")
            
        request.status = FacultyRequestStatus.REJECTED
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.utcnow()
        request.review_notes = review_data.notes
        request.rejection_reason = review_data.rejection_reason
        
        updated_request = repo.update(request)
        
        # Update user status
        user_service = UserService()
        user_service.update_user(db, request.user_id, status=UserStatus.REJECTED)
        
        # Fire Domain Event
        EventDispatcher.dispatch("FacultyRejected", db, request.id, reviewer_id, review_data.rejection_reason)
        
        return updated_request
