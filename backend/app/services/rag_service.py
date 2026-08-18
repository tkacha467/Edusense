"""Lightweight Database-Backed RAG Retrieval & Context Isolation Service (v1.10.1)."""
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.student import StudentProfile
from app.core.enums import UserRole
from app.core.exceptions import EduSenseException
from app.features.feature_store import StudentFeatureStore
from app.services.knowledge_decay_prediction import get_prediction_service
from app.services.adaptive_revision_scheduler import get_adaptive_scheduler
from app.services.faculty_intervention_service import get_faculty_intervention_service

logger = logging.getLogger(__name__)

class RAGService:
    """
    Database-backed context retrieval layer for grounded Ollama decision support.
    Enforces strict identity and role-based student context isolation.
    """
    def __init__(self):
        self.feature_store = StudentFeatureStore()
        self.pred_service = get_prediction_service()
        self.scheduler = get_adaptive_scheduler()
        self.intervention_service = get_faculty_intervention_service()

    def retrieve_student_context(
        self,
        db: Session,
        requesting_user: User,
        target_student_id: str,
        skill_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves grounded student learning context with strict cross-student security bounds.
        """
        if not requesting_user:
            raise EduSenseException(status_code=401, message="Unauthorized identity.")

        # RBAC & Identity Isolation Enforcement
        if requesting_user.role == UserRole.STUDENT:
            student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == requesting_user.id).first()
            if not student_profile or student_profile.id != target_student_id:
                logger.warning(f"Cross-student RAG retrieval blocked: User {requesting_user.id} requested Student {target_student_id}")
                raise EduSenseException(
                    status_code=403,
                    message="Forbidden: Access to another student's learning context is strictly denied."
                )
        elif requesting_user.role not in [UserRole.FACULTY, UserRole.ADMIN]:
            raise EduSenseException(status_code=403, message="Forbidden: Role unauthorized for student context retrieval.")

        # Retrieve Student Profile
        target_student = db.query(StudentProfile).filter(StudentProfile.id == target_student_id).first()
        if not target_student:
            raise EduSenseException(status_code=404, message=f"Student {target_student_id} not found.")

        # Retrieve Feature Vector & Deterministic ML Prediction
        feats = self.feature_store.compute_student_features(db, student_id=target_student_id, skill_id=skill_id)
        prediction = self.pred_service.predict_forgetting_risk(db, student_id=target_student_id, skill_id=skill_id)

        # Retrieve Intervention History
        interventions = self.intervention_service.get_student_interventions(db, faculty_user_id=requesting_user.id, student_id=target_student_id)

        retrieved_context = {
            "source_type": "STUDENT_CONTEXT",
            "source_id": target_student_id,
            "data": {
                "student_id": target_student_id,
                "grade_level": getattr(target_student, "grade_level", "Undergraduate"),
                "learning_style": getattr(target_student, "learning_style", "Visual"),
                "target_skill_id": skill_id or "general",
                "feature_snapshot": feats,
                "deterministic_ml_prediction": {
                    "forget_probability": prediction["forget_probability"],
                    "forget_probability_percentage": prediction["forget_probability_percentage"],
                    "risk_level": prediction["risk_level"],
                    "estimated_forgetting_window": prediction["estimated_forgetting_window"],
                    "recommended_revision_date": prediction["recommended_revision_date"],
                    "revision_priority": prediction["revision_priority"],
                    "top_risk_factors": prediction["top_risk_factors"],
                    "top_protective_factors": prediction["top_protective_factors"],
                    "model_version": prediction["model_version"]
                },
                "recent_interventions_count": len(interventions),
                "active_interventions": [
                    {
                        "id": intv.get("id"),
                        "skill_id": intv.get("skill_id"),
                        "intervention_type": intv.get("intervention_type"),
                        "priority": intv.get("priority"),
                        "status": intv.get("status")
                    } for intv in interventions[:3]
                ]
            }
        }

        logger.info(f"RAG Service successfully retrieved grounded context for Student {target_student_id} (Requested by User {requesting_user.id})")
        return retrieved_context

    def retrieve_academic_context(
        self,
        db: Session,
        subject_name: Optional[str] = "Computer Science",
        topic_name: Optional[str] = None,
        skill_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves academic curriculum and metadata context.
        """
        return {
            "source_type": "ACADEMIC_CURRICULUM_CONTEXT",
            "source_id": f"{subject_name}_{topic_name}_{skill_name}",
            "data": {
                "subject_name": subject_name,
                "topic_name": topic_name or "General Topic",
                "skill_name": skill_name or "General Skill",
                "difficulty_levels_supported": ["BEGINNER", "INTERMEDIATE", "ADVANCED"],
                "learning_objectives": [
                    f"Master core foundational principles of {skill_name or topic_name or subject_name}",
                    "Apply concepts to practical problem-solving assessments"
                ]
            }
        }

def get_rag_service() -> RAGService:
    return RAGService()
