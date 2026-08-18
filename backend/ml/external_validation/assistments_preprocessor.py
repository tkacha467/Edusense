"""Point-in-Time Temporal Feature Engineering for External Validation (v1.11)."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import numpy as np

from ml.external_validation.assistments_schema import StandardizedLearningEvent, FEATURE_SCHEMA_ORDER

logger = logging.getLogger(__name__)

class ASSISTmentsPointInTimePreprocessor:
    """
    Computes point-in-time feature vectors matching feature_schema.json strictly using historical events (t < cutoff_time).
    Guarantees 0 future event temporal leakage.
    """
    def compute_point_in_time_features(
        self,
        events: List[StandardizedLearningEvent],
        student_id: str,
        cutoff_time: datetime,
        skill_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Extracts historical feature vector strictly for events < cutoff_time.
        """
        # Strict temporal filtering (t < cutoff_time)
        history = [
            e for e in events 
            if e.external_student_id == student_id and e.event_timestamp < cutoff_time
        ]

        if skill_id:
            skill_history = [e for e in history if e.skill_id == skill_id]
        else:
            skill_history = history

        total_attempts = len(history)
        if total_attempts == 0:
            # Cold-start fallback
            return {
                "days_since_last_review": 14.0,
                "total_attempts": 0,
                "correct_attempts": 0,
                "historical_accuracy": 0.75,
                "consecutive_correct_streak": 0,
                "avg_response_time_seconds": 15.0,
                "practice_frequency": 0.5,
                "decay_vulnerability_index": 0.5
            }

        # 1. Days since last review
        last_event = max(history, key=lambda x: x.event_timestamp)
        days_gap = max(0.0, (cutoff_time - last_event.event_timestamp).total_seconds() / 86400.0)

        # 2 & 3. Attempts & Correct Attempts
        correct_attempts = sum(e.correct for e in history)
        historical_accuracy = round(correct_attempts / total_attempts, 4)

        # 4. Consecutive correct streak
        history_sorted = sorted(history, key=lambda x: x.event_timestamp, reverse=True)
        streak = 0
        for e in history_sorted:
            if e.correct == 1:
                streak += 1
            else:
                break

        # 5. Average response time in seconds
        avg_resp = float(np.mean([e.response_time_seconds for e in history]))

        # 6. Practice frequency (sessions per week in 30-day window)
        window_start = cutoff_time - timedelta(days=30)
        recent_history = [e for e in history if e.event_timestamp >= window_start]
        unique_days = len(set(e.event_timestamp.date() for e in recent_history))
        practice_freq = round((unique_days / 30.0) * 7.0, 2)

        # 7. Decay Vulnerability Index (Ebbinghaus Decay Logit)
        decay_idx = round(min(1.0, max(0.0, 1.0 - (historical_accuracy * np.exp(-0.08 * days_gap)))), 4)

        return {
            "days_since_last_review": round(days_gap, 2),
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "historical_accuracy": historical_accuracy,
            "consecutive_correct_streak": streak,
            "avg_response_time_seconds": round(avg_resp, 2),
            "practice_frequency": practice_freq,
            "decay_vulnerability_index": decay_idx
        }
