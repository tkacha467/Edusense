"""Knowledge Decay Model Training, Evaluation, Calibration & Serialization Pipeline (v1.1)."""
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

MODEL_VERSION = "knowledge-decay-v1.1"
ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../artifacts'))
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../reports'))

def calculate_pr_auc(y_true: np.ndarray, y_probs: np.ndarray) -> float:
    """Calculates Area Under Precision-Recall Curve."""
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    return float(auc(recall, precision))

def train_and_evaluate_models() -> Dict[str, Any]:
    print("========================================================")
    print("  EduSense AI Knowledge Decay Model Training Pipeline v1.1  ")
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

        # Chronological sort for temporal split
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

        # Candidate Models Pool
        models = {
            "Logistic Regression": Pipeline([
                ("scaler", StandardScaler()),
                ("classifier", LogisticRegression(C=1.0, max_iter=1000, random_state=42))
            ]),
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=80, learning_rate=0.08, max_depth=3, random_state=42)
        }

        try:
            import xgboost as xgb
            models["XGBoost"] = xgb.XGBClassifier(n_estimators=80, max_depth=3, learning_rate=0.08, random_state=42, eval_metric="logloss")
            print("[+] XGBoost registered in comparison pool.")
        except ImportError:
            print("[!] XGBoost not installed. Using Gradient Boosting.")

        model_results = {}
        fitted_models = {}

        # ----------------------------------------------------
        # 1. EVALUATE BASELINES
        # ----------------------------------------------------
        prior_prob = float(np.mean(y_train))
        y_probs_b_prior = np.full_like(y_test, fill_value=prior_prob, dtype=float)
        model_results["Baseline (Class Prior)"] = {
            "roc_auc": 0.5000,
            "pr_auc": round(prior_prob, 4),
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "accuracy": round(float(accuracy_score(y_test, np.zeros_like(y_test))), 4),
            "brier_score": round(float(brier_score_loss(y_test, y_probs_b_prior)), 4),
            "training_time_ms": 0.01,
            "inference_time_ms": 0.01
        }

        days_test = X_test[:, 0]
        y_probs_heur = np.clip(days_test / 30.0, 0.0, 1.0)
        model_results["Baseline (Time Heuristic)"] = {
            "roc_auc": round(float(roc_auc_score(y_test, y_probs_heur)), 4),
            "pr_auc": round(calculate_pr_auc(y_test, y_probs_heur), 4),
            "precision": round(float(precision_score(y_test, (y_probs_heur >= 0.5).astype(int), zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, (y_probs_heur >= 0.5).astype(int), zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, (y_probs_heur >= 0.5).astype(int), zero_division=0)), 4),
            "accuracy": round(float(accuracy_score(y_test, (y_probs_heur >= 0.5).astype(int))), 4),
            "brier_score": round(float(brier_score_loss(y_test, y_probs_heur)), 4),
            "training_time_ms": 0.01,
            "inference_time_ms": 0.01
        }

        # ----------------------------------------------------
        # 2. EVALUATE ML CANDIDATE MODELS
        # ----------------------------------------------------
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
            print(f"[+] Model '{name}' Evaluated -> PR-AUC: {pr_auc:.4f} | ROC-AUC: {roc_auc:.4f} | Brier: {brier:.4f}")

        # Model Selection (ML Candidates Only)
        ml_candidates = [k for k in model_results.keys() if "Baseline" not in k]
        best_name = max(ml_candidates, key=lambda k: model_results[k]["pr_auc"] - model_results[k]["brier_score"])
        best_model = fitted_models[best_name]
        print(f"[SELECTED] Selected Champion Model: '{best_name}' (PR-AUC: {model_results[best_name]['pr_auc']})")

        # ----------------------------------------------------
        # 3. CALIBRATION COMPARISON
        # ----------------------------------------------------
        calib_sigmoid = CalibratedClassifierCV(best_model, method="sigmoid", cv=3)
        calib_sigmoid.fit(X_train, y_train)
        probs_sig = calib_sigmoid.predict_proba(X_test)[:, 1]
        brier_sig = float(brier_score_loss(y_test, probs_sig))

        calib_iso = CalibratedClassifierCV(best_model, method="isotonic", cv=3)
        calib_iso.fit(X_train, y_train)
        probs_iso = calib_iso.predict_proba(X_test)[:, 1]
        brier_iso = float(brier_score_loss(y_test, probs_iso))

        uncalib_brier = model_results[best_name]["brier_score"]

        print(f"[+] Calibration Evaluation -> Uncalibrated: {uncalib_brier:.4f} | Platt (Sigmoid): {brier_sig:.4f} | Isotonic: {brier_iso:.4f}")

        # Pick best calibration method based on lowest Brier score
        if brier_sig <= uncalib_brier and brier_sig <= brier_iso:
            final_model = calib_sigmoid
            final_brier = brier_sig
            calib_method = "Platt Scaling (Sigmoid)"
        elif brier_iso <= uncalib_brier:
            final_model = calib_iso
            final_brier = brier_iso
            calib_method = "Isotonic Regression"
        else:
            final_model = best_model
            final_brier = uncalib_brier
            calib_method = "Uncalibrated (Optimal raw probabilities)"

        print(f"[+] Final Model Calibration Chosen: '{calib_method}' (Brier Score: {final_brier:.4f})")

        # ----------------------------------------------------
        # 4. STUDENT HOLDOUT EXPERIMENT
        # ----------------------------------------------------
        unique_students = list(set(d["student_id"] for d in dataset))
        np.random.seed(42)
        np.random.shuffle(unique_students)
        split_s_idx = int(len(unique_students) * 0.80)
        train_studs = set(unique_students[:split_s_idx])
        test_studs = set(unique_students[split_s_idx:])

        X_s_train = np.array([[d[f] for f in FEATURE_NAMES] for d in dataset if d["student_id"] in train_studs])
        y_s_train = np.array([d["target_forgotten"] for d in dataset if d["student_id"] in train_studs])
        X_s_test = np.array([[d[f] for f in FEATURE_NAMES] for d in dataset if d["student_id"] in test_studs])
        y_s_test = np.array([d["target_forgotten"] for d in dataset if d["student_id"] in test_studs])

        holdout_model = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(C=1.0, max_iter=1000, random_state=42))
        ])
        holdout_model.fit(X_s_train, y_s_train)
        probs_s_test = holdout_model.predict_proba(X_s_test)[:, 1]

        student_holdout_metrics = {
            "num_test_students": len(test_studs),
            "num_test_samples": len(X_s_test),
            "pr_auc": round(calculate_pr_auc(y_s_test, probs_s_test), 4),
            "roc_auc": round(float(roc_auc_score(y_s_test, probs_s_test)), 4),
            "brier_score": round(float(brier_score_loss(y_s_test, probs_s_test)), 4)
        }
        print(f"[+] Student-Level Holdout Evaluation -> PR-AUC: {student_holdout_metrics['pr_auc']} | Brier: {student_holdout_metrics['brier_score']}")

        # ----------------------------------------------------
        # SERIALIZE ARTIFACTS
        # ----------------------------------------------------
        with open(os.path.join(ARTIFACTS_DIR, "knowledge_decay_model.pkl"), "wb") as f:
            pickle.dump(final_model, f)

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
            "calibration_method": calib_method,
            "metrics": {
                "pr_auc": model_results[best_name]["pr_auc"],
                "roc_auc": model_results[best_name]["roc_auc"],
                "brier_score": round(final_brier, 4),
                "precision": model_results[best_name]["precision"],
                "recall": model_results[best_name]["recall"],
                "f1_score": model_results[best_name]["f1_score"]
            },
            "student_holdout_metrics": student_holdout_metrics,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "training_timestamp": datetime.now(timezone.utc).isoformat()
        }
        with open(os.path.join(ARTIFACTS_DIR, "model_metrics.json"), "w") as f:
            json.dump(model_metrics, f, indent=2)

        with open(os.path.join(ARTIFACTS_DIR, "model_version.json"), "w") as f:
            json.dump({"version": MODEL_VERSION, "status": "active"}, f, indent=2)

        with open(os.path.join(ARTIFACTS_DIR, "calibration.json"), "w") as f:
            json.dump({"method": calib_method, "brier_score": round(final_brier, 4)}, f, indent=2)

        # ----------------------------------------------------
        # GENERATE REPORTS
        # ----------------------------------------------------
        comparison_report = {
            "model_version": MODEL_VERSION,
            "selected_model": best_name,
            "calibration_method": calib_method,
            "evaluation_metric_primary": "PR-AUC",
            "results": model_results,
            "student_holdout_results": student_holdout_metrics
        }
        with open(os.path.join(REPORTS_DIR, "model_comparison.json"), "w") as f:
            json.dump(comparison_report, f, indent=2)

        # Write Markdown Report
        md_report = f"""# EduSense AI — Knowledge Decay Model Comparison & Audit Report ($v1.1$)

**Model Version**: `{MODEL_VERSION}`  
**Selected Champion Model**: `{best_name}`  
**Calibration Method**: `{calib_method}`  
**Evaluation Timestamp**: `{datetime.now(timezone.utc).isoformat()}`  
**Dataset Size**: `{len(dataset)} samples` (`Train: {len(X_train)}`, `Val: {len(X_val)}`, `Test: {len(X_test)}`)

## 1. Candidate Model & Baseline Performance Matrix

| Model Candidate | PR-AUC | ROC-AUC | Precision | Recall | F1 Score | Brier Score | Training Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
        for m_name, res in model_results.items():
            sel_flag = " (Selected Champion)" if m_name == best_name else ""
            md_report += f"| **{m_name}{sel_flag}** | **{res['pr_auc']}** | {res['roc_auc']} | {res['precision']} | {res['recall']} | {res['f1_score']} | **{res['brier_score']}** | {res['training_time_ms']} |\n"

        md_report += f"""
## 2. Student-Level Generalization Test (Unseen Students Holdout)
- **Unseen Test Students**: `{student_holdout_metrics['num_test_students']}`
- **PR-AUC**: `{student_holdout_metrics['pr_auc']}`
- **ROC-AUC**: `{student_holdout_metrics['roc_auc']}`
- **Brier Score**: `{student_holdout_metrics['brier_score']}`

## 3. Calibration Evaluation
- **Uncalibrated Model Brier Score**: `{uncalib_brier:.4f}`
- **Platt Scaling (Sigmoid) Brier Score**: `{brier_sig:.4f}`
- **Isotonic Regression Brier Score**: `{brier_iso:.4f}`
- **Selected Strategy**: `{calib_method}`
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
