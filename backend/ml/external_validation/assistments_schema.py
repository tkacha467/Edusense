"""Standardized Schema & Event Data Contracts for ASSISTments External Validation (v1.11)."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

ASSISTMENTS_COLUMN_MAP = {
    "user_id": "external_student_id",
    "skill_name": "skill_name",
    "skill_id": "skill_id",
    "correct": "correct",
    "ms_first_response": "response_time_ms",
    "timestamp": "event_timestamp",
    "order_id": "order_id"
}

FEATURE_SCHEMA_ORDER = [
    "days_since_last_review",
    "total_attempts",
    "correct_attempts",
    "historical_accuracy",
    "consecutive_correct_streak",
    "avg_response_time_seconds",
    "practice_frequency",
    "decay_vulnerability_index"
]

@dataclass
class StandardizedLearningEvent:
    external_student_id: str
    skill_id: str
    skill_name: str
    event_timestamp: datetime
    correct: int
    response_time_seconds: float
    order_id: Optional[int] = None
    raw_payload: Dict[str, Any] = field(default_factory=dict)
