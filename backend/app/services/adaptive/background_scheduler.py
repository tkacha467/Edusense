"""Background Scheduler Service for recurring daily tasks and automated checks."""
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models import StudentProfile
from app.repositories import StudentProfileRepository, KnowledgeProfileRepository, StudyTaskRepository
from app.services.adaptive.planner import RevisionPlanner
from app.services.adaptive.notification_engine import AdaptiveNotificationEngine
from app.services.adaptive.faculty_intervention import FacultyInterventionEngine


class AdaptiveBackgroundJobsService:
    """
    Interface-compatible background job runner for APScheduler / Celery / Redis Queue.
    Includes daily recommendation generation, revision checks, missed task alerts, and faculty alerts.
    """

    def __init__(self) -> None:
        self.student_repo = StudentProfileRepository()
        self.kp_repo = KnowledgeProfileRepository()
        self.task_repo = StudyTaskRepository()
        self.planner = RevisionPlanner()
        self.notif_engine = AdaptiveNotificationEngine()
        self.faculty_engine = FacultyInterventionEngine()

    def run_daily_recommendations_job(self, db: Session) -> Dict[str, int]:
        """Scans all active onboarded students and generates updated Study Plans."""
        students = self.student_repo.get_all(db)
        generated_count = 0

        for student in students:
            if student.onboarding_completed:
                self.planner.generate_adaptive_study_plan(db, student)
                generated_count += 1

        return {"status": "success", "study_plans_generated": generated_count}

    def run_missed_tasks_check_job(self, db: Session) -> Dict[str, int]:
        """Scans pending tasks with past scheduled dates and sends missed task notifications."""
        students = self.student_repo.get_all(db)
        alert_count = 0

        for student in students:
            tasks = self.task_repo.get_pending_tasks(db, student_id=student.id)
            today = datetime.now(timezone.utc).date()
            missed = [t for t in tasks if t.scheduled_date and t.scheduled_date < today]

            if missed:
                self.notif_engine.send_missed_tasks_alert(db, user_id=student.user_id, missed_count=len(missed))
                alert_count += 1

        return {"status": "success", "notifications_sent": alert_count}

    def run_faculty_alert_check_job(self, db: Session) -> Dict[str, int]:
        """Scans high decay knowledge profiles and generates faculty intervention alerts."""
        students = self.student_repo.get_all(db)
        interventions_count = 0

        for student in students:
            profiles = self.kp_repo.get_at_risk_profiles(db, student_id=student.id, threshold=0.85)
            for p in profiles:
                res = self.faculty_engine.check_and_trigger_intervention(db, student, p)
                if res and res.get("intervention_triggered"):
                    interventions_count += 1

        return {"status": "success", "faculty_interventions_triggered": interventions_count}
