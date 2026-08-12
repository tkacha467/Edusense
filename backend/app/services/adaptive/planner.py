"""Revision Planner service for creating personalized Study Plans."""
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.enums import StudyPlanType, StudyPlanStatus, TaskType, TaskStatus, TaskPriority
from app.models import StudyPlan, StudyTask, StudentProfile, KnowledgeProfile
from app.repositories import StudyPlanRepository, StudyTaskRepository, KnowledgeProfileRepository, LearningPreferenceRepository
from app.services.adaptive.decision_engine import RecommendationDecisionEngine, RecommendationDecision


class RevisionPlanner:
    """Service generating structured Study Plans and Study Tasks from Recommendation Decisions."""

    def __init__(self) -> None:
        self.decision_engine = RecommendationDecisionEngine()
        self.plan_repo = StudyPlanRepository()
        self.task_repo = StudyTaskRepository()
        self.kp_repo = KnowledgeProfileRepository()
        self.pref_repo = LearningPreferenceRepository()

    def generate_adaptive_study_plan(
        self,
        db: Session,
        student_profile: StudentProfile,
        subject_id: Optional[str] = None
    ) -> StudyPlan:
        """
        Scans all student knowledge profiles, runs RecommendationDecisionEngine,
        and generates an active StudyPlan with prioritized StudyTasks.
        """
        # Fetch knowledge profiles
        profiles = self.kp_repo.get_by_student(db, student_id=student_profile.id)
        if not profiles:
            # Create a default plan if no profiles exist yet
            plan = self.plan_repo.create(
                db,
                student_id=student_profile.id,
                subject_id=subject_id,
                title="Adaptive Revision Plan",
                description="Personalized study plan based on knowledge decay analytics.",
                plan_type=StudyPlanType.REVISION,
                status=StudyPlanStatus.ACTIVE,
                start_date=datetime.now(timezone.utc).date(),
                end_date=datetime.now(timezone.utc).date() + timedelta(days=7)
            )
            return plan

        # Evaluate decisions for all profiles
        decisions: List[RecommendationDecision] = [
            self.decision_engine.evaluate_skill_decision(db, student_profile, p)
            for p in profiles
        ]

        # Sort decisions by priority (High/Critical first) & forgetting probability descending
        decisions.sort(key=lambda d: (0 if d.priority == TaskPriority.HIGH else 1, -d.forget_probability))

        # Deactivate existing active plans
        active_plans = self.plan_repo.get_active_by_student(db, student_id=student_profile.id)
        for p in active_plans:
            self.plan_repo.update(db, db_obj=p, obj_in={"status": StudyPlanStatus.ARCHIVED})

        # Create new active plan
        plan = self.plan_repo.create(
            db,
            student_id=student_profile.id,
            subject_id=subject_id or (decisions[0].subject_id if decisions else None),
            title="Adaptive Revision Plan",
            description=f"Generated plan prioritizing {len([d for d in decisions if d.priority == TaskPriority.HIGH])} high-risk skills.",
            plan_type=StudyPlanType.REVISION,
            status=StudyPlanStatus.ACTIVE,
            start_date=datetime.now(timezone.utc).date(),
            end_date=datetime.now(timezone.utc).date() + timedelta(days=7)
        )

        # Generate Tasks for top decisions
        for idx, dec in enumerate(decisions[:5]):
            task_type = TaskType.REVISION if dec.forget_probability < 0.60 else TaskType.PRACTICE
            self.task_repo.create(
                db,
                study_plan_id=plan.id,
                topic_id=dec.topic_id,
                skill_id=dec.skill_id,
                title=f"Revise {dec.skill_name}",
                task_type=task_type,
                priority=dec.priority,
                status=TaskStatus.PENDING,
                estimated_minutes=dec.estimated_duration_minutes,
                scheduled_date=dec.recommended_date,
                order_index=idx
            )

        db.commit()
        return plan
