import logging
from sqlalchemy.orm import Session
from app.core.events import EventDispatcher
from app.services.knowledge import KnowledgeDecayService
from app.services.adaptive.planner import RevisionPlanner
from app.services.adaptive.timeline import LearningTimelineService
from app.models.student import StudentProfile

logger = logging.getLogger(__name__)

def handle_assessment_completed(db: Session, student_id: str, session_id: str, skill_updates: list[str]) -> None:
    """
    Orchestrates the adaptive loop after an assessment is submitted.
    Listens for 'AssessmentCompleted' domain event.
    """
    logger.info(f"Orchestrating adaptive loop for AssessmentSession {session_id}")
    try:
        # 1. Update Knowledge Profile and Run Prediction Engine
        kd_service = KnowledgeDecayService()
        for skill_id in skill_updates:
            kd_service.run_prediction_pipeline(
                db=db, 
                student_id=student_id, 
                skill_id=skill_id
            )
        
        # 2. Feed Revision Queue via RevisionPlanner
        # We need the student_profile for the revision planner and timeline
        student_profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        
        if student_profile:
            planner = RevisionPlanner()
            planner.generate_adaptive_study_plan(
                db=db, 
                student_profile=student_profile
            )

        # 3. Create Timeline Event
        timeline_service = LearningTimelineService()
        timeline_service.record_event(
            db=db,
            user_id=student_profile.user_id if student_profile else student_id,
            event_name="Assessment Completed",
            entity_type="AssessmentSession",
            entity_id=session_id,
            details=f"Completed assessment and generated adaptive recommendations."
        )

        # Note: Notification is already triggered inside KnowledgeDecayService.run_prediction_pipeline
        
        # 4. Refresh Cache / Commit 
        # (Since this runs in a background task, we must commit our own transaction if we modified anything)
        db.commit()
        logger.info(f"Successfully completed adaptive orchestration for AssessmentSession {session_id}")

    except Exception as e:
        logger.error(f"Failed to orchestrate adaptive loop for session {session_id}: {e}")
        db.rollback()

from app.core.enums import UserStatus, FacultyRequestStatus
from app.models.user import User
from app.models.faculty_request import FacultyRequest
from app.models.audit import AuditLog

def handle_faculty_approved(db: Session, request_id: str, reviewer_id: str) -> None:
    """Handles logic when a faculty request is approved."""
    logger.info(f"Handling FacultyApproved event for request {request_id}")
    try:
        request = db.query(FacultyRequest).filter(FacultyRequest.id == request_id).first()
        if not request:
            return
            
        user = db.query(User).filter(User.id == request.user_id).first()
        if user:
            user.status = UserStatus.ACTIVE
            
            # Create Audit Log
            audit = AuditLog(
                user_id=reviewer_id,
                action="FACULTY_APPROVED",
                resource_type="FacultyRequest",
                resource_id=request_id,
                request_id=request_id,
                old_value='{"status": "PENDING"}',
                new_value='{"status": "APPROVED"}',
                details=f"Faculty request {request_id} approved."
            )
            db.add(audit)
            db.commit()
    except Exception as e:
        logger.error(f"Failed to handle FacultyApproved for {request_id}: {e}")
        db.rollback()

def handle_faculty_rejected(db: Session, request_id: str, reviewer_id: str, reason: str) -> None:
    """Handles logic when a faculty request is rejected."""
    logger.info(f"Handling FacultyRejected event for request {request_id}")
    try:
        request = db.query(FacultyRequest).filter(FacultyRequest.id == request_id).first()
        if not request:
            return
            
        user = db.query(User).filter(User.id == request.user_id).first()
        if user:
            user.status = UserStatus.REJECTED
            
            # Create Audit Log
            audit = AuditLog(
                user_id=reviewer_id,
                action="FACULTY_REJECTED",
                resource_type="FacultyRequest",
                resource_id=request_id,
                request_id=request_id,
                old_value='{"status": "PENDING"}',
                new_value='{"status": "REJECTED"}',
                details=f"Faculty request {request_id} rejected. Reason: {reason}"
            )
            db.add(audit)
            db.commit()
    except Exception as e:
        logger.error(f"Failed to handle FacultyRejected for {request_id}: {e}")
        db.rollback()

# Register domain event listeners
EventDispatcher.subscribe("AssessmentCompleted", handle_assessment_completed)
EventDispatcher.subscribe("FacultyApproved", handle_faculty_approved)
EventDispatcher.subscribe("FacultyRejected", handle_faculty_rejected)
