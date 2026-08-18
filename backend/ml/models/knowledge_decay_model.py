"""Knowledge Decay Model Training, Evaluation, Calibration & Serialization Pipeline."""
import os
import sys
import json
import pickle
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    roc_auc_score, 
    precision_recall_curve, 
    auc, 
    precision_score, 
    recall_score, 
    f1_score, 
    brier_score_loss,
    accuracy_score
)

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault("SECRET_KEY", "dev_secret_key_edusense_ai_2026_super_secure")
os.environ.setdefault("DATABASE_URL", "sqlite:///./edusense.db")

from app.config import get_settings
from app.database.database import get_engine
from app.database.session import get_session_factory
from ml.data.target_builder import KnowledgeDecayTargetBuilder

# Feature Schema Contract
FEATURE_NAMES = [
    "days_since_last_review",
    "total_attempts",
    "correct_attempts",
    "historical_accuracy",
    "consecutive_correct_streak",
    "avg_response_time_seconds",
    "practice_frequency",
    "decay_vulnerability_index"
]

MODEL_VERSION = "knowledge-decay-v1.0"
ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../artifacts'))
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../reports'))

def calculate_pr_auc(y_true: np.ndarray, y_probs: np.ndarray) -> float:
    """Calculates Area Under Precision-Recall Curve."""
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    return float(auc(recall, precision))

def train_and_evaluate_models() -> Dict[str, Any]:
    print("========================================================")
    print("  EduSense AI Knowledge Decay Model Training Pipeline   ")
    print("========================================================")

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    settings = get_settings()
    engine = get_engine(settings)
    SessionFactory = get_session_factory(engine)
    db = SessionFactory()

    try:
        builder = KnowledgeDecayTargetBuilder(horizon_days=7, mastery_threshold=0.70)
        dataset, dataset_meta = builder.build_dataset_from_db(db)
        print(f"[+] Dataset Loaded: {dataset_meta['total_samples']} samples (Positive Class: {dataset_meta['positive_class_count']})")

        # Sort dataset chronologically for leak-free temporal splitting
        dataset = sorted(dataset, key=lambda d: d.get("cutoff_time", ""))

        X = np.array([[d[f] for f in FEATURE_NAMES] for d in dataset])
        y = np.array([d["target_forgotten"] for d in dataset])

        n_samples = len(X)
        train_end = int(n_samples * 0.70)
        val_end = int(n_samples * 0.85)

        X_train, y_train = X[:train_end], y[:train_end]
        X_val, y_val = X[train_end:val_end], y[train_end:val_end]
        X_test, y_test = X[val_end:], y[val_end:]

        print(f"[+] Temporal Split -> Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")

        # Candidate Models
        models = {
            "Logistic Regression": Pipeline([
                ("scaler", StandardScaler()),
                ("classifier", LogisticRegression(C=1.0, max_iter=1000, random_state=42))
            ]),
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=80, learning_rate=0.1, max_depth=4, random_state=42)
        }

        # Try importing XGBoost if available
        try:
            import xgboost as xgb
            models["XGBoost"] = xgb.XGBClassifier(n_estimators=80, max_depth=4, learning_rate=0.1, random_state=42, eval_metric="logloss")
            print("[+] XGBoost available and registered in model comparison pool.")
        except ImportError:
            print("[!] XGBoost not installed. Using Gradient Boosting Classifier as ensemble tree baseline.")

        model_results = {}
        fitted_models = {}

        for name, model in models.items():
            start_time = datetime.now(timezone.utc)
            model.fit(X_train, y_train)
            train_time_ms = round((datetime.now(timezone.utc) - start_time).total_seconds() * 1000, 2)

            start_inf = datetime.now(timezone.utc)
            y_probs = model.predict_proba(X_test)[:, 1]
            inf_time_ms = round((datetime.now(timezone.utc) - start_inf).total_seconds() * 1000 / max(1, len(X_test)), 3)

            y_pred = (y_probs >= 0.50).astype(int)

            roc_auc = float(roc_auc_score(y_test, y_probs))
            pr_auc = calculate_pr_auc(y_test, y_probs)
            prec = float(precision_score(y_test, y_pred, zero_division=0))
            rec = float(recall_score(y_test, y_pred, zero_division=0))
            f1 = float(f1_score(y_test, y_pred, zero_division=0))
            brier = float(brier_score_loss(y_test, y_probs))
            acc = float(accuracy_score(y_test, y_pred))

            model_results[name] = {
                "roc_auc": round(roc_auc, 4),
                "pr_auc": round(pr_auc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "accuracy": round(acc, 4),
                "brier_score": round(brier, 4),
                "training_time_ms": train_time_ms,
                "inference_time_ms": inf_time_ms
            }
            fitted_models[name] = model

            print(f"[+] Model '{name}' Evaluated -> PR-AUC: {pr_auc:.4f} | ROC-AUC: {roc_auc:.4f} | Recall: {rec:.4f} | Brier: {brier:.4f}")

        # Model Selection: Selected based on PR-AUC & Brier Score
        best_name = max(model_results.keys(), key=lambda k: model_results[k]["pr_auc"] - model_results[k]["brier_score"])
        best_model = fitted_models[best_name]
        print(f"[SELECTED] Selected Best Model: '{best_name}' (PR-AUC: {model_results[best_name]['pr_auc']})")

        # Calibrate Selected Model using Platt Scaling (CalibratedClassifierCV)
        calibrated_model = CalibratedClassifierCV(best_model, method="sigmoid", cv=3)
        calibrated_model.fit(X_train, y_train)

        calib_probs = calibrated_model.predict_proba(X_test)[:, 1]
        calib_brier = float(brier_score_loss(y_test, calib_probs))
        calib_pr_auc = calculate_pr_auc(y_test, calib_probs)
        calib_roc_auc = float(roc_auc_score(y_test, calib_probs))

        print(f"[+] Probability Calibration Applied -> Post-Calibration Brier Score: {calib_brier:.4f}")

        # ----------------------------------------------------
        # SERIALIZE ARTIFACTS
        # ----------------------------------------------------
        model_path = os.path.join(ARTIFACTS_DIR, "knowledge_decay_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(calibrated_model, f)

        feature_schema = {
            "model_version": MODEL_VERSION,
            "feature_names": FEATURE_NAMES,
            "num_features": len(FEATURE_NAMES),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        with open(os.path.join(ARTIFACTS_DIR, "feature_schema.json"), "w") as f:
            json.dump(feature_schema, f, indent=2)

        model_metrics = {
            "model_version": MODEL_VERSION,
            "selected_model": best_name,
            "metrics": {
                "pr_auc": round(calib_pr_auc, 4),
                "roc_auc": round(calib_roc_auc, 4),
                "brier_score": round(calib_brier, 4),
                "precision": model_results[best_name]["precision"],
                "recall": model_results[best_name]["recall"],
                "f1_score": model_results[best_name]["f1_score"]
            },
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "training_timestamp": datetime.now(timezone.utc).isoformat()
        }
        with open(os.path.join(ARTIFACTS_DIR, "model_metrics.json"), "w") as f:
            json.dump(model_metrics, f, indent=2)

        with open(os.path.join(ARTIFACTS_DIR, "model_version.json"), "w") as f:
            json.dump({"version": MODEL_VERSION, "status": "active"}, f, indent=2)

        with open(os.path.join(ARTIFACTS_DIR, "calibration.json"), "w") as f:
            json.dump({"method": "Platt Scaling (Sigmoid)", "brier_score": round(calib_brier, 4)}, f, indent=2)

        # ----------------------------------------------------
        # GENERATE REPORTS
        # ----------------------------------------------------
        comparison_report = {
            "model_version": MODEL_VERSION,
            "selected_model": best_name,
            "evaluation_metric_primary": "PR-AUC",
            "results": model_results
        }
        with open(os.path.join(REPORTS_DIR, "model_comparison.json"), "w") as f:
            json.dump(comparison_report, f, indent=2)

        # Write Markdown Report
        md_report = f"""# EduSense AI — Knowledge Decay Model Comparison Report ($v1.0$)

**Model Version**: `{MODEL_VERSION}`  
**Selected Champion Model**: `{best_name}`  
**Evaluation Timestamp**: `{datetime.now(timezone.utc).isoformat()}`  
**Dataset Size**: `{len(dataset)} samples` (`Train: {len(X_train)}`, `Val: {len(X_val)}`, `Test: {len(X_test)}`)

## Model Performance Metrics Matrix

| Model Candidate | PR-AUC | ROC-AUC | Precision | Recall | F1 Score | Brier Score | Training Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
        for m_name, res in model_results.items():
            sel_flag = " (Selected)" if m_name == best_name else ""
            md_report += f"| **{m_name}{sel_flag}** | **{res['pr_auc']}** | {res['roc_auc']} | {res['precision']} | {res['recall']} | {res['f1_score']} | **{res['brier_score']}** | {res['training_time_ms']} |\n"

        md_report += f"""
## Calibration & Selection Rationale
- **Selection Rule**: Champion model selected by maximizing `PR-AUC - Brier_Score` to ensure high recall on at-risk students while maintaining well-calibrated probabilities.
- **Calibrated Brier Score**: `{calib_brier:.4f}` using Platt Sigmoid Scaling.
"""
        with open(os.path.join(REPORTS_DIR, "model_comparison.md"), "w") as f:
            f.write(md_report)

        print("========================================================")
        print(f"[SUCCESS] MODEL TRAINING & SERIALIZATION COMPLETED! ({MODEL_VERSION})")
        print("========================================================")

        return model_metrics

    finally:
        db.close()

if __name__ == "__main__":
    train_and_evaluate_models()
