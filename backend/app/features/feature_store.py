"""Student Knowledge Decay Feature Store Engine for EduSense AI."""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.assessment import AssessmentSession, StudentResponse
from app.models.learning import StudentSkill

class StudentFeatureStore:
    """
    Decoupled Feature Store for calculating standardized feature vectors 
    for Student Knowledge Decay Prediction & Machine Learning Models.
    """
    def __init__(self):
        pass

    def compute_student_features(self, db: Session, student_id: str, subject_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates normalized ML feature vectors for a given student.
        
        Returns:
            Dict containing:
            - days_since_last_review (float)
            - total_attempts (int)
            - correct_attempts (int)
            - historical_accuracy (float)
            - consecutive_correct_streak (int)
            - avg_response_time_seconds (float)
            - decay_vulnerability_index (float)
        """
        stmt = select(StudentResponse).where(StudentResponse.student_id == student_id)
        if subject_id:
            stmt = stmt.join(AssessmentSession).where(AssessmentSession.subject_id == subject_id)
        
        responses = list(db.execute(stmt).scalars().all())

        if not responses:
            return {
                "days_since_last_review": 1.0,
                "total_attempts": 0,
                "correct_attempts": 0,
                "historical_accuracy": 0.5,
                "consecutive_correct_streak": 0,
                "avg_response_time_seconds": 15.0,
                "decay_vulnerability_index": 0.5
            }

        total_attempts = len(responses)
        correct_attempts = sum(1 for r in responses if r.is_correct)
        historical_accuracy = float(correct_attempts / total_attempts)

        # Sort by creation timestamp
        sorted_responses = sorted(responses, key=lambda r: r.created_at or datetime.now(timezone.utc), reverse=True)
        latest_response = sorted_responses[0]

        now = datetime.now(timezone.utc)
        latest_time = latest_response.created_at
        if latest_time:
            if latest_time.tzinfo is None:
                latest_time = latest_time.replace(tzinfo=timezone.utc)
            delta = now - latest_time
            days_since_last_review = max(0.01, float(delta.total_seconds() / 86400.0))
        else:
            days_since_last_review = 1.0

        # Calculate streak
        consecutive_streak = 0
        for r in sorted_responses:
            if r.is_correct:
                consecutive_streak += 1
            else:
                break

        avg_time = float(sum(r.time_taken_seconds for r in responses) / total_attempts)

        # Decay vulnerability formula: v = (1 - accuracy) * (1 + 0.1 * days)
        decay_vulnerability = float(min(1.0, max(0.0, (1.0 - historical_accuracy) * (1.0 + 0.05 * days_since_last_review))))

        return {
            "days_since_last_review": round(days_since_last_review, 2),
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "historical_accuracy": round(historical_accuracy, 4),
            "consecutive_correct_streak": consecutive_streak,
            "avg_response_time_seconds": round(avg_time, 2),
            "decay_vulnerability_index": round(decay_vulnerability, 4)
        }

def get_feature_store() -> StudentFeatureStore:
    return StudentFeatureStore()
