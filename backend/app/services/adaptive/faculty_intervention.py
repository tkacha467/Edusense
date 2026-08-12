"""Faculty Intervention Engine for automated academic support alerts."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.enums import NotificationType, NotificationPriority
from app.models import KnowledgeProfile, StudentProfile, User
from app.repositories import NotificationRepository, AuditLogRepository


class FacultyInterventionEngine:
    """Detects critical learning stagnation / decay and triggers Faculty Intervention alerts."""

    def __init__(self) -> None:
        self.notif_repo = NotificationRepository()
        self.audit_repo = AuditLogRepository()

    def check_and_trigger_intervention(
        self,
        db: Session,
        student_profile: StudentProfile,
        profile: KnowledgeProfile
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluates criteria for Faculty Intervention:
        Condition: forget_probability > 0.85 AND past_attempts >= 3 AND past_accuracy < 0.40
        """
        forget_prob = profile.forget_probability or 0.0
        attempts = profile.past_attempts or 0
        accuracy = profile.past_accuracy or 0.0

        if forget_prob >= 0.85 and attempts >= 3 and accuracy < 0.40:
            skill_name = profile.skill.name if getattr(profile, 'skill', None) else "Target Skill"
            user_id = student_profile.user_id

            # Create Student Warning Notification
            self.notif_repo.create(
                db,
                user_id=user_id,
                title="Faculty Support Initiated",
                message=f"Critical retention risk on '{skill_name}'. Your faculty member has been notified to assist you.",
                notification_type=NotificationType.FACULTY_INTERVENTION.value,
                priority=NotificationPriority.URGENT.value
            )

            # Audit Event Log for Faculty Dashboard
            audit = self.audit_repo.log_action(
                db,
                user_id=user_id,
                action="faculty.intervention.created",
                entity_type="KnowledgeProfile",
                entity_id=profile.id,
                details=f"Triggered for student {student_profile.id} on skill {profile.skill_id} (forget_prob={forget_prob})"
            )

            return {
                "intervention_triggered": True,
                "student_id": student_profile.id,
                "skill_id": profile.skill_id,
                "skill_name": skill_name,
                "forget_probability": forget_prob,
                "audit_id": audit.id
            }

        return None
