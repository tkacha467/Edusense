"""Recommendation Decision Engine & Priority Calculator."""
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.core.enums import TaskPriority, TaskType, QuestionDifficulty
from app.models import KnowledgeProfile, PredictionHistory, StudentActivity, LearningPreference, StudentProfile
from app.repositories import KnowledgeProfileRepository, StudentSkillRepository, LearningPreferenceRepository, AssessmentSessionRepository


class PriorityCalculator:
    """Configurable priority calculator based on forgetting probability and risk."""

    @staticmethod
    def calculate_priority(forget_probability: float) -> TaskPriority:
        """
        Calculates TaskPriority enum based on forgetting probability:
        - forget_probability >= 0.80 -> TaskPriority.HIGH (Critical)
        - 0.60 <= forget_probability < 0.80 -> TaskPriority.HIGH
        - 0.40 <= forget_probability < 0.60 -> TaskPriority.MEDIUM
        - forget_probability < 0.40 -> TaskPriority.LOW
        """
        if forget_probability >= 0.60:
            return TaskPriority.HIGH
        elif forget_probability >= 0.40:
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.LOW

    @staticmethod
    def calculate_revision_difficulty(rolling_accuracy: float) -> str:
        """Determines target difficulty based on student's rolling accuracy."""
        if rolling_accuracy >= 0.80:
            return "hard"
        elif rolling_accuracy >= 0.50:
            return "intermediate"
        else:
            return "beginner"


@dataclass
class RecommendationDecision:
    """Structured decision output from RecommendationDecisionEngine."""
    student_id: str
    skill_id: str
    skill_name: str
    topic_id: Optional[str]
    subject_id: Optional[str]
    priority: TaskPriority
    forget_probability: float
    retention_score: float
    revision_type: str
    recommended_difficulty: str
    estimated_duration_minutes: int
    recommended_date: date
    study_mode: str
    notification_required: bool
    faculty_intervention_required: bool


class RecommendationDecisionEngine:
    """
    Heart of Phase 5: Purely deterministic decision engine transforming ML predictions,
    learning preferences, and activity metrics into personalized learning decisions.
    """

    def __init__(self) -> None:
        self.kp_repo = KnowledgeProfileRepository()
        self.pref_repo = LearningPreferenceRepository()
        self.session_repo = AssessmentSessionRepository()

    def evaluate_skill_decision(
        self,
        db: Session,
        student_profile: StudentProfile,
        profile: KnowledgeProfile
    ) -> RecommendationDecision:
        """
        Evaluates a KnowledgeProfile for a student and generates a RecommendationDecision.
        """
        pref = self.pref_repo.get_by_student(db, student_id=student_profile.id)
        preferred_session_len = pref.preferred_session_length if pref else 30

        forget_prob = profile.forget_probability or 0.0
        retention = profile.retention_score or (1.0 - forget_prob)
        priority = PriorityCalculator.calculate_priority(forget_prob)
        difficulty = PriorityCalculator.calculate_revision_difficulty(profile.rolling_accuracy or 0.0)

        # Revision type decision based on forgetting probability and mastery
        if forget_prob >= 0.80:
            revision_type = "URGENT_REVISION"
            study_mode = "SPACED_REPETITION"
            est_minutes = preferred_session_len
        elif profile.mastered:
            revision_type = "MASTERY_REINFORCEMENT"
            study_mode = "ADVANCED_PRACTICE"
            est_minutes = max(15, preferred_session_len // 2)
        else:
            revision_type = "CONCEPT_REVIEW"
            study_mode = "ACTIVE_RECALL"
            est_minutes = preferred_session_len

        # Flags for notifications and faculty intervention
        notification_required = bool(forget_prob >= 0.50)
        faculty_intervention_required = bool(forget_prob >= 0.85 and (profile.past_attempts or 0) >= 3 and (profile.past_accuracy or 0.0) < 0.40)

        skill_name = profile.skill.name if getattr(profile, 'skill', None) else "Target Skill"
        topic_id = None
        subject_id = None
        if getattr(profile, 'skill', None) and getattr(profile.skill, 'topic_skills', None):
            topic_id = profile.skill.topic_skills[0].topic_id
            if getattr(profile.skill.topic_skills[0], 'topic', None):
                subject_id = profile.skill.topic_skills[0].topic.subject_id

        today = datetime.now(timezone.utc).date()
        target_date = today if priority == TaskPriority.HIGH else today + timedelta(days=1)

        return RecommendationDecision(
            student_id=student_profile.id,
            skill_id=profile.skill_id,
            skill_name=skill_name,
            topic_id=topic_id,
            subject_id=subject_id,
            priority=priority,
            forget_probability=forget_prob,
            retention_score=retention,
            revision_type=revision_type,
            recommended_difficulty=difficulty,
            estimated_duration_minutes=est_minutes,
            recommended_date=target_date,
            study_mode=study_mode,
            notification_required=notification_required,
            faculty_intervention_required=faculty_intervention_required
        )
