"""Assessment Analytics Service for computing topic, skill, time, and confidence metrics."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.repositories import (
    AssessmentSessionRepository,
    QuestionRepository,
    StudentResponseRepository,
    StudentSkillRepository,
    StudentActivityRepository
)
from app.models import StudentActivity
from app.core.enums import ActivityType


class AssessmentAnalyticsService:
    """Service computing processed analytics from raw assessment responses."""

    def __init__(self) -> None:
        self.session_repo = AssessmentSessionRepository()
        self.question_repo = QuestionRepository()
        self.response_repo = StudentResponseRepository()
        self.skill_repo = StudentSkillRepository()
        self.activity_repo = StudentActivityRepository()

    def process_session_analytics(
        self,
        db: Session,
        session_id: str,
        student_id: str
    ) -> Dict[str, Any]:
        """
        Compute rich analytics metrics for a completed assessment session:
        - Topic & Skill accuracy breakdown
        - Average time per question
        - Confidence alignment
        - Logs structured activity record
        """
        session = self.session_repo.get_by_id(db, session_id)
        if not session:
            return {}

        responses = self.response_repo.get_by_session(db, session_id=session_id)
        questions = self.question_repo.get_by_assessment(db, session_id=session_id)
        question_map = {q.id: q for q in questions}

        total_questions = len(responses)
        total_time_seconds = sum((r.time_taken_seconds or 0) for r in responses)
        avg_time_seconds = (total_time_seconds / total_questions) if total_questions > 0 else 0.0

        # Topic & Skill accuracy tracking
        topic_stats: Dict[str, Dict[str, int]] = {}
        skill_stats: Dict[str, Dict[str, int]] = {}
        confidence_counts: Dict[str, int] = {"low": 0, "medium": 0, "high": 0}

        for r in responses:
            q = question_map.get(r.question_id)
            if not q:
                continue

            # Confidence breakdown
            conf = (r.confidence_level.value if hasattr(r.confidence_level, 'value') else str(r.confidence_level or "medium")).lower()
            if conf in confidence_counts:
                confidence_counts[conf] += 1

            # Topic tracking
            if q.topic_id:
                if q.topic_id not in topic_stats:
                    topic_stats[q.topic_id] = {"attempts": 0, "correct": 0}
                topic_stats[q.topic_id]["attempts"] += 1
                if r.is_correct:
                    topic_stats[q.topic_id]["correct"] += 1

            # Skill tracking
            if q.skill_id:
                if q.skill_id not in skill_stats:
                    skill_stats[q.skill_id] = {"attempts": 0, "correct": 0}
                skill_stats[q.skill_id]["attempts"] += 1
                if r.is_correct:
                    skill_stats[q.skill_id]["correct"] += 1

        # Calculate accuracy maps
        topic_accuracy = {
            t_id: (s["correct"] / s["attempts"]) if s["attempts"] > 0 else 0.0
            for t_id, s in topic_stats.items()
        }
        skill_accuracy = {
            s_id: (s["correct"] / s["attempts"]) if s["attempts"] > 0 else 0.0
            for s_id, s in skill_stats.items()
        }

        analytics_result = {
            "session_id": session_id,
            "student_id": student_id,
            "subject_id": session.subject_id,
            "total_questions": total_questions,
            "total_time_seconds": total_time_seconds,
            "avg_time_seconds": round(avg_time_seconds, 2),
            "topic_accuracy": topic_accuracy,
            "skill_accuracy": skill_accuracy,
            "confidence_breakdown": confidence_counts,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }

        # Log activity entry for analytics dashboard
        self.activity_repo.create(
            db,
            student_id=student_id,
            activity_type=ActivityType.ASSESSMENT_COMPLETED,
            entity_type="AssessmentSession",
            entity_id=session_id,
            subject_id=session.subject_id,
            duration_seconds=total_time_seconds,
            activity_date=datetime.now(timezone.utc).date()
        )

        return analytics_result
