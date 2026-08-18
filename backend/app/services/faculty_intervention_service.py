"""Faculty Intervention Intelligence Service for EduSense AI (v1.7)."""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.student import StudentProfile
from app.models.learning import Subject, Topic
from app.core.enums import UserRole
from app.core.exceptions import ForbiddenException, NotFoundException, BadRequestException
from app.services.knowledge_decay_prediction import get_prediction_service
from app.services.revision_outcome_service import get_outcome_service
from app.services.revision_recommendation import get_revision_engine

logger = logging.getLogger(__name__)

# Persistent storage for faculty interventions in current session
_FACULTY_INTERVENTIONS: List[Dict[str, Any]] = []

class FacultyInterventionService:
    """
    Manages targeted faculty learning interventions for at-risk students.
    Preserves original prediction snapshots at intervention creation without modifying ML probabilities.
    """
    def __init__(self):
        self.prediction_service = get_prediction_service()
        self.outcome_service = get_outcome_service()
        self.revision_engine = get_revision_engine()

    def create_intervention(
        self,
        db: Session,
        faculty_user_id: str,
        student_id: str,
        skill_id: str,
        intervention_type: str = "REVISION",
        priority: str = "URGENT",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a targeted faculty intervention for a student's at-risk skill.
        Preserves original prediction snapshot and pushes task into student revision queue.
        """
        # 1. Validate student existence
        student = db.query(StudentProfile).filter_by(id=student_id).first()
        if not student:
            # Fallback check by user_id
            student = db.query(StudentProfile).filter_by(user_id=student_id).first()
            if not student:
                raise NotFoundException(f"Student profile '{student_id}' not found.")

        resolved_student_id = student.id

        # 2. Check duplicate active intervention for same student + skill
        existing_active = [
            i for i in _FACULTY_INTERVENTIONS
            if i["student_id"] == resolved_student_id and i["skill_id"] == skill_id and i["status"] in ["PENDING", "ACTIVE", "DUE"]
        ]
        if existing_active:
            raise BadRequestException(f"An active intervention already exists for student {resolved_student_id[:8]} on skill '{skill_id}'.")

        # 3. Get current ML Prediction snapshot (MUST NOT BE OVERRIDDEN)
        pred = self.prediction_service.predict_forgetting_risk(
            db=db,
            student_id=resolved_student_id,
            skill_id=skill_id
        )

        intervention_id = f"intv_{faculty_user_id[:6]}_{resolved_student_id[:6]}_{len(_FACULTY_INTERVENTIONS) + 1}"

        # 4. Construct intervention record
        record = {
            "intervention_id": intervention_id,
            "faculty_user_id": faculty_user_id,
            "student_id": resolved_student_id,
            "skill_id": skill_id,
            "intervention_type": intervention_type,
            "priority": priority,
            "notes": notes or f"Faculty-initiated targeted {intervention_type.lower()} intervention.",
            "status": "PENDING",
            "forget_probability_at_intervention": pred["forget_probability"],
            "forget_probability_percentage": pred["forget_probability_percentage"],
            "risk_level_at_intervention": pred["risk_level"],
            "model_version_at_intervention": pred["model_version"],
            "recommended_revision_date": pred["recommended_revision_date"],
            "top_risk_factors": pred["top_risk_factors"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "viewed_at": None,
            "started_at": None,
            "completed_at": None,
            "post_intervention_forget_probability": None,
            "observed_risk_reduction": None,
            "outcome_status": "PENDING_STUDENT_ACTION"
        }

        # Preserve prediction snapshot in outcome tracking service
        self.outcome_service.preserve_initial_prediction(intervention_id, pred)
        self.outcome_service.record_event(intervention_id, resolved_student_id, skill_id, "CREATED", {"created_by": faculty_user_id})

        _FACULTY_INTERVENTIONS.append(record)
        logger.info(f"Created Faculty Intervention {intervention_id} for student {resolved_student_id[:8]} on skill {skill_id}")
        return record

    def list_faculty_interventions(self, db: Session, faculty_user_id: str) -> List[Dict[str, Any]]:
        """Lists all interventions initiated by the specified faculty member."""
        return [i for i in _FACULTY_INTERVENTIONS if i["faculty_user_id"] == faculty_user_id]

    def get_student_interventions(self, db: Session, faculty_user_id: str, student_id: str) -> List[Dict[str, Any]]:
        """Lists intervention history for a specific authorized student."""
        student_interventions = [i for i in _FACULTY_INTERVENTIONS if i["student_id"] == student_id]
        
        # Update outcome metrics for completed interventions
        for item in student_interventions:
            if item["status"] == "COMPLETED" and item["post_intervention_forget_probability"] is None:
                post_pred = self.prediction_service.predict_forgetting_risk(db, student_id=student_id, skill_id=item["skill_id"])
                post_prob = post_pred["forget_probability"]
                pre_prob = item["forget_probability_at_intervention"]
                risk_red = round(pre_prob - post_prob, 4)
                
                item["post_intervention_forget_probability"] = post_prob
                item["observed_risk_reduction"] = risk_red
                item["outcome_status"] = "OBSERVED_IMPROVEMENT" if risk_red > 0 else "NO_SIGNIFICANT_CHANGE"

        return student_interventions

def get_faculty_intervention_service() -> FacultyInterventionService:
    return FacultyInterventionService()
