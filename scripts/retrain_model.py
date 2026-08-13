import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, brier_score_loss, precision_recall_curve, auc
import joblib
import json
import datetime
import os
import sklearn

# Configuration
DATA_PATH = "Data/Processed/model_ready_dataset.csv"
MODEL_DIR = "Models"
FORGET_THRESHOLD = 0.60
FEATURES = [
    "interaction_order",
    "past_attempts",
    "past_correct",
    "past_accuracy",
    "rolling_accuracy",
    "mastered"
]

def load_and_prepare_data():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    
    # Drop rows with missing values in features or target
    df = df.dropna(subset=FEATURES + ["future_accuracy"])
    
    print(f"Original forget_event mean: {df['forget_event'].mean():.4f}")
    
    # Redefine target
    # Class 1 = Forgetting (future_accuracy < THRESHOLD)
    # Class 0 = Retention 
    # Remove mastered == 1 condition
    df["forget_event"] = (df["future_accuracy"] < FORGET_THRESHOLD).astype(int)
    print(f"New forget_event mean: {df['forget_event'].mean():.4f}")
    
    X = df[FEATURES]
    y = df["forget_event"]
    
    # Train / Val / Test (70 / 15 / 15)
    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.1765, random_state=42, stratify=y_train_val) # 0.1765 of 0.85 is roughly 0.15
    
    print(f"Train size: {len(X_train)}, Val size: {len(X_val)}, Test size: {len(X_test)}")
    return X_train, X_val, X_test, y_train, y_val, y_test

def evaluate_model(model, X_val, y_val, name="Model"):
    y_pred = model.predict(X_val)
    y_prob = model.predict_proba(X_val)[:, 1]
    
    precision, recall, _ = precision_recall_curve(y_val, y_prob)
    pr_auc = auc(recall, precision)
    
    metrics = {
        "Accuracy": accuracy_score(y_val, y_pred),
        "Precision": precision_score(y_val, y_pred, zero_division=0),
        "Recall": recall_score(y_val, y_pred, zero_division=0),
        "F1": f1_score(y_val, y_pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_val, y_prob),
        "PR-AUC": pr_auc,
        "Brier Score": brier_score_loss(y_val, y_prob)
    }
    
    print(f"\n--- {name} ---")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
        
    return metrics, y_prob

def run_regression_suite(model, scaler):
    print("\n--- Edge-Case Regression Suite ---")
    # Features: ["interaction_order", "past_attempts", "past_correct", "past_accuracy", "rolling_accuracy", "mastered"]
    cases = [
        {"name": "0 attempts (New)", "data": [0, 0, 0, 0.0, 0.0, 0]},
        {"name": "First attempt, 0% accuracy", "data": [1, 1, 0, 0.0, 0.0, 0]},
        {"name": "First attempt, 100% accuracy", "data": [1, 1, 1, 1.0, 1.0, 0]},
        {"name": "5 attempts, improving (50%)", "data": [5, 5, 2, 0.4, 0.5, 0]},
        {"name": "5 attempts, improving (80%)", "data": [5, 5, 4, 0.8, 0.9, 0]},
        {"name": "20 attempts, mastered", "data": [20, 20, 18, 0.9, 1.0, 1]},
    ]
    
    for case in cases:
        x_scaled = scaler.transform([case["data"]])
        prob = model.predict_proba(x_scaled)[0][1]
        print(f"{case['name']:<30} -> Forget Prob: {prob:.4f}")

def main():
    X_train, X_val, X_test, y_train, y_val, y_test = load_and_prepare_data()
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    print("\nTraining Model A (Standard)...")
    model_a = LogisticRegression(random_state=42, max_iter=1000)
    model_a.fit(X_train_scaled, y_train)
    
    print("Training Model B (Balanced)...")
    model_b = LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000)
    model_b.fit(X_train_scaled, y_train)
    
    eval_a, prob_a = evaluate_model(model_a, X_val_scaled, y_val, "Model A (Standard)")
    eval_b, prob_b = evaluate_model(model_b, X_val_scaled, y_val, "Model B (Balanced)")
    
    # Feature Importance (Model A)
    print("\n--- Feature Importance (Model A) ---")
    coefs = model_a.coef_[0]
    feat_importance = sorted(zip(FEATURES, coefs), key=lambda x: abs(x[1]), reverse=True)
    for rank, (feat, coef) in enumerate(feat_importance, 1):
        sign = "+" if coef > 0 else "-"
        print(f"{rank}. {feat:<20} {coef:>8.4f} ({sign})")
        
    print("\nIntercept (Model A):", model_a.intercept_[0])
    
    run_regression_suite(model_a, scaler)
    
    # Save Models (Version 2)
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "best_model_v2.pkl")
    scaler_path = os.path.join(MODEL_DIR, "scaler_v2.pkl")
    onnx_path = os.path.join(MODEL_DIR, "best_model.onnx")
    manifest_path = os.path.join(MODEL_DIR, "training_manifest.json")
    
    joblib.dump(model_a, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\nSaved {model_path} and {scaler_path}")
    
    # Export to ONNX
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    initial_type = [('float_input', FloatTensorType([None, len(FEATURES)]))]
    onx = convert_sklearn(model_a, initial_types=initial_type)
    
    # Embed metadata into ONNX graph
    onx.doc_string = "Knowledge Decay Predictor (Forgetting Risk)"
    onx.domain = "com.edusense.models"
    onx.model_version = 2
    
    with open(onnx_path, "wb") as f:
        f.write(onx.SerializeToString())
    print(f"Saved {onnx_path}")
    
    manifest = {
        "model_version": "2.0.0",
        "dataset": "model_ready_dataset.csv",
        "training_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "features": FEATURES,
        "threshold": FORGET_THRESHOLD,
        "random_seed": 42,
        "sklearn_version": sklearn.__version__,
        "metrics_val": eval_a,
        "coefficients": {f: float(c) for f, c in zip(FEATURES, coefs)},
        "intercept": float(model_a.intercept_[0])
    }
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved {manifest_path}")

if __name__ == "__main__":
    main()
