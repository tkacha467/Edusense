"""Production Knowledge Decay Prediction Service & Revision Recommendation Layer."""
import os
import json
import pickle
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
import numpy as np
from sqlalchemy.orm import Session

from app.features.feature_store import get_feature_store
from app.core.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ml/artifacts'))
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "knowledge_decay_model.pkl")
SCHEMA_PATH = os.path.join(ARTIFACTS_DIR, "feature_schema.json")
METRICS_PATH = os.path.join(ARTIFACTS_DIR, "model_metrics.json")

class KnowledgeDecayPredictionService:
    """
    Production Inference Service loading serialized model artifacts, 
    computing point-in-time feature vectors via Feature Store,
    predicting probability of knowledge decay, and generating deterministic revision interventions.
    """
    def __init__(self):
        self.feature_store = get_feature_store()
        self.model = None
        self.feature_names = []
        self.model_version = "knowledge-decay-v1.0"
        self._load_model_artifacts()

    def _load_model_artifacts(self):
        try:
            if os.path.exists(MODEL_PATH):
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded trained model artifact from {MODEL_PATH}")
            
            if os.path.exists(SCHEMA_PATH):
                with open(SCHEMA_PATH, "r") as f:
                    schema_data = json.load(f)
                    self.feature_names = schema_data.get("feature_names", [])
                    self.model_version = schema_data.get("model_version", "knowledge-decay-v1.0")
        except Exception as e:
            logger.warning(f"Failed to load trained model artifacts: {str(e)}. Running algorithmic fallback model.")

    def predict_forgetting_risk(
        self, 
        db: Session, 
        student_id: str, 
        skill_id: Optional[str] = None, 
        subject_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predicts forgetting probability and derives revision interventions for a student.
        """
        # 1. Retrieve feature vector from Feature Store
        feats = self.feature_store.compute_student_features(
            db=db,
            student_id=student_id,
            subject_id=subject_id,
            skill_id=skill_id
        )

        # 2. Extract input vector matching schema order
        feature_order = self.feature_names or [
            "days_since_last_review",
            "total_attempts",
            "correct_attempts",
            "historical_accuracy",
            "consecutive_correct_streak",
            "avg_response_time_seconds",
            "practice_frequency",
            "decay_vulnerability_index"
        ]
        X_vec = np.array([[feats.get(f, 0.0) for f in feature_order]])

        # 3. Model Inference or Deterministic Mathematical Fallback
        if self.model:
            try:
                probs = self.model.predict_proba(X_vec)[0]
                forget_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            except Exception as e:
                logger.warning(f"Model prediction error ({str(e)}), reverting to feature store decay index.")
                forget_prob = float(feats.get("decay_vulnerability_index", 0.5))
        else:
            # Formula-based Ebbinghaus Memory Decay Fallback:
            # P(forget) = 1 - p * exp(-0.08 * t)
            days = feats["days_since_last_review"]
            acc = feats["historical_accuracy"]
            retention = acc * np.exp(-0.08 * days)
            forget_prob = float(min(1.0, max(0.0, 1.0 - retention)))

        forget_prob = round(float(min(1.0, max(0.0, forget_prob))), 4)
        forget_prob_pct = round(forget_prob * 100.0, 1)

        # 4. Risk Classification Bands
        if forget_prob < 0.35:
            risk_level = "LOW"
            est_window = "15-30 days"
            rev_days = 14
            priority = "low"
        elif forget_prob < 0.65:
            risk_level = "MEDIUM"
            est_window = "4-7 days"
            rev_days = 4
            priority = "medium"
        else:
            risk_level = "HIGH"
            est_window = "1-3 days"
            rev_days = 1
            priority = "urgent"

        recommended_rev_date = (datetime.now(timezone.utc) + timedelta(days=rev_days)).isoformat()

        # 5. Model Explainability Factor Attribution
        risk_factors = []
        protective_factors = []

        if feats["days_since_last_review"] > 7.0:
            risk_factors.append(f"Extended period without practice ({feats['days_since_last_review']} days)")
        if feats["historical_accuracy"] < 0.70:
            risk_factors.append(f"Below-threshold historical accuracy ({int(feats['historical_accuracy']*100)}%)")
        if feats["consecutive_correct_streak"] < 2:
            risk_factors.append("Low recent consecutive correct streak")

        if feats["historical_accuracy"] >= 0.80:
            protective_factors.append(f"Strong historical mastery ({int(feats['historical_accuracy']*100)}%)")
        if feats["consecutive_correct_streak"] >= 3:
            protective_factors.append(f"Active streak of {feats['consecutive_correct_streak']} correct answers")
        if feats["days_since_last_review"] <= 2.0:
            protective_factors.append("Recent active review within last 48 hours")

        if not risk_factors:
            risk_factors.append("Baseline temporal decay over time")
        if not protective_factors:
            protective_factors.append("Initial foundation accuracy")

        return {
            "student_id": student_id,
            "skill_id": skill_id,
            "subject_id": subject_id,
            "forget_probability": forget_prob,
            "forget_probability_percentage": forget_prob_pct,
            "risk_level": risk_level,
            "prediction_horizon_days": 7,
            "estimated_forgetting_window": est_window,
            "recommended_revision_date": recommended_rev_date,
            "revision_priority": priority,
            "top_risk_factors": risk_factors,
            "top_protective_factors": protective_factors,
            "feature_vector": feats,
            "model_version": self.model_version
        }

def get_prediction_service() -> KnowledgeDecayPredictionService:
    return KnowledgeDecayPredictionService()
