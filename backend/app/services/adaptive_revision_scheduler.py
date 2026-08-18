"""Adaptive Revision Scheduler for EduSense AI Knowledge Decay System (v1.5)."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.services.knowledge_decay_prediction import get_prediction_service
from app.services.revision_outcome_service import get_outcome_service

logger = logging.getLogger(__name__)

# Persistent in-memory store for student-skill adaptive states
_ADAPTIVE_STATES: Dict[str, Dict[str, Any]] = {}

class AdaptiveRevisionScheduler:
    """
    Operates ABOVE the ML model to dynamically adjust revision intervals based on
    observed student performance and recommendation outcomes.
    The ML model probability P(forgetting within 7 days) remains untouched.
    """
    def __init__(self):
        self.prediction_service = get_prediction_service()
        self.outcome_service = get_outcome_service()

    def get_or_create_adaptive_state(self, student_id: str, skill_id: str) -> Dict[str, Any]:
        """Fetches or initializes adaptive state for a (student_id, skill_id) pair."""
        key = f"{student_id}_{skill_id}"
        if key not in _ADAPTIVE_STATES:
            _ADAPTIVE_STATES[key] = {
                "student_id": student_id,
                "skill_id": skill_id,
                "previous_interval_days": 5,
                "new_interval_days": 5,
                "adaptation_direction": "MAINTAIN",
                "adaptation_reason": "Default initial interval assigned.",
                "successful_revision_count": 0,
                "consecutive_successes": 0,
                "consecutive_failures": 0,
                "last_adapted_at": datetime.now(timezone.utc).isoformat()
            }
        return _ADAPTIVE_STATES[key]

    def compute_adaptive_schedule(
        self,
        db: Session,
        student_id: str,
        skill_id: str,
        subject_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Computes personalized next revision interval and date based on ML prediction & historical performance.
        Interval bounds: Min 1 day, Max 30 days.
        """
        # 1. Get ML Prediction from validated model (MUST NOT BE MODIFIED)
        pred = self.prediction_service.predict_forgetting_risk(
            db=db,
            student_id=student_id,
            skill_id=skill_id,
            subject_id=subject_id
        )

        forget_prob = pred["forget_probability"]
        risk_level = pred["risk_level"]
        feats = pred.get("feature_vector", {})
        hist_acc = feats.get("historical_accuracy", 0.75)

        # 2. Get existing adaptive state
        state = self.get_or_create_adaptive_state(student_id, skill_id)
        prev_interval = state.get("new_interval_days", 5)

        # 3. Base interval based on ML risk classification
        if risk_level == "HIGH":
            base_interval = 2
        elif risk_level == "MEDIUM":
            base_interval = 5
        else:
            base_interval = 14

        # 4. Outcome & Performance Adjustment Rules
        if hist_acc >= 0.85:
            # Strong performance: Extend interval
            direction = "EXTEND"
            bonus = min(4, state.get("consecutive_successes", 0))
            raw_interval = int(round(base_interval * 1.4)) + bonus
            amount = max(1, raw_interval - prev_interval)
            reason = f"Strong post-revision accuracy ({int(hist_acc * 100)}%). Extending revision interval by {amount} days."
        elif hist_acc < 0.70:
            # Weak performance: Shorten interval
            direction = "SHORTEN"
            raw_interval = max(1, int(round(base_interval * 0.6)))
            amount = max(1, prev_interval - raw_interval)
            reason = f"Historical accuracy below mastery threshold ({int(hist_acc * 100)}%). Shortening revision interval by {amount} days."
        else:
            # Moderate performance: Maintain
            direction = "MAINTAIN"
            raw_interval = base_interval
            amount = 0
            reason = f"Stable performance ({int(hist_acc * 100)}%). Maintaining standard revision interval."

        # 5. Enforce strict interval bounds (1 to 30 days)
        final_interval = max(1, min(30, raw_interval))
        next_date = (datetime.now(timezone.utc) + timedelta(days=final_interval)).strftime("%Y-%m-%d")

        # 6. Update adaptive state
        state["previous_interval_days"] = prev_interval
        state["new_interval_days"] = final_interval
        state["adaptation_direction"] = direction
        state["adaptation_reason"] = reason
        state["last_adapted_at"] = datetime.now(timezone.utc).isoformat()

        return {
            "student_id": student_id,
            "skill_id": skill_id,
            "forget_probability": forget_prob,
            "forget_probability_percentage": pred["forget_probability_percentage"],
            "risk_level": risk_level,
            "previous_interval_days": prev_interval,
            "new_interval_days": final_interval,
            "adjustment_direction": direction,
            "adjustment_amount_days": amount,
            "recommended_revision_date": next_date,
            "adaptation_reason": reason,
            "model_version": pred["model_version"]
        }

    def process_assessment_completion_adaptation(
        self,
        db: Session,
        student_id: str,
        skill_id: str
    ) -> Dict[str, Any]:
        """
        Triggers adaptive state update upon completion of a new assessment/practice session.
        """
        schedule = self.compute_adaptive_schedule(db, student_id, skill_id)
        logger.info(f"Processed closed-loop adaptation for student {student_id[:8]}, skill {skill_id}: New interval = {schedule['new_interval_days']} days ({schedule['adjustment_direction']})")
        return schedule

def get_adaptive_scheduler() -> AdaptiveRevisionScheduler:
    return AdaptiveRevisionScheduler()
