import os
import sys
import numpy as np
import joblib

# Add the parent directory to the path so we can import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config.settings import get_settings

def run_forensics():
    print("# ML Forensics Report\n")
    
    settings = get_settings()
    model_path = os.path.abspath(settings.ML_MODEL_PATH)
    scaler_path = os.path.abspath(settings.ML_SCALER_PATH)
    
    print("## 1. Artifact Validation\n")
    print(f"- **Model Path:** `{model_path}`")
    print(f"- **Scaler Path:** `{scaler_path}`")
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print("[FAIL] Model artifacts missing. Cannot proceed with forensics.")
        return

    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
    except Exception as e:
        print(f"[FAIL] Failed to load artifacts: {e}")
        return

    print("### Model Metadata")
    print(f"- **Model Type:** `{type(model).__name__}`")
    if hasattr(model, "classes_"):
        print(f"- **Classes:** `{model.classes_}`")
    if hasattr(model, "intercept_"):
        print(f"- **Intercept:** `{model.intercept_}`")
    if hasattr(model, "coef_"):
        print(f"- **Coefficient Shape:** `{model.coef_.shape}`")
    if hasattr(model, "n_features_in_"):
        print(f"- **Features In:** `{model.n_features_in_}`")

    print("\n### Scaler Metadata")
    print(f"- **Scaler Type:** `{type(scaler).__name__}`")
    if hasattr(scaler, "mean_"):
        print(f"- **Means:** `{scaler.mean_}`")
    if hasattr(scaler, "scale_"):
        print(f"- **Scale (Std Dev):** `{scaler.scale_}`")
        print(f"- **Variances:** `{scaler.var_}`")
    if hasattr(scaler, "n_features_in_"):
        print(f"- **Features In:** `{scaler.n_features_in_}`")

    print("\n## 2. Feature Order Verification\n")
    # In 'selected_features.json', we saw the expected training features
    expected_features = [
        "interaction_order",
        "past_attempts",
        "past_correct",
        "past_accuracy",
        "rolling_accuracy",
        "mastered"
    ]
    print("### Expected Training Order")
    for i, f in enumerate(expected_features):
        print(f"{i}: {f}")

    print("\n## 3. Coefficient Inspection\n")
    print("| Feature | Expected Sign | Actual Sign | Weight | Suspicious? |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    
    expected_signs = {
        "interaction_order": "Negative",
        "past_attempts": "Pos/Neg",
        "past_correct": "Negative",
        "past_accuracy": "Negative",
        "rolling_accuracy": "Negative",
        "mastered": "Negative"
    }

    if hasattr(model, "coef_") and model.coef_.shape[1] == len(expected_features):
        coeffs = model.coef_[0]
        for i, feature in enumerate(expected_features):
            weight = coeffs[i]
            actual_sign = "Positive" if weight > 0 else "Negative"
            exp_sign = expected_signs[feature]
            
            suspicious = "[FAIL]"
            if exp_sign == "Pos/Neg" or exp_sign == actual_sign:
                suspicious = "[PASS]"
                
            print(f"| {feature} | {exp_sign} | {actual_sign} | {weight:.4f} | {suspicious} |")
    else:
        print("Cannot extract coefficients matching feature length.")

    print("\n## 4. Inference Pipeline Reconstruction (Trace)\n")
    print("Tracing a single benchmark sample:\n")
    
    # Let's trace a student who has 5 attempts, 4 correct, 0.8 accuracy, 0.7 rolling, not mastered
    # (interaction_order, past_attempts, past_correct, past_accuracy, rolling_accuracy, mastered)
    raw_inputs = (5, 5, 4, 0.8, 0.7, 0.0)
    print("### Raw Inputs")
    for i, feature in enumerate(expected_features):
        print(f"- **{feature}**: {raw_inputs[i]}")

    feature_vector = np.array([list(raw_inputs)])
    
    print("\n### Preprocessing (StandardScaler)")
    scaled_features = scaler.transform(feature_vector)
    for i, feature in enumerate(expected_features):
        print(f"- **Scaled {feature}**: {scaled_features[0][i]:.4f}")

    print("\n### Inference (LogisticRegression)")
    if hasattr(model, "decision_function"):
        logit = model.decision_function(scaled_features)[0]
        print(f"- **Decision Function (Logit)**: {logit:.4f}")
        
        # Sigmoid probability
        prob_manual = 1.0 / (1.0 + np.exp(-logit))
        print(f"- **Manual Sigmoid (Class 1 Prob)**: {prob_manual:.4f}")
    
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(scaled_features)[0]
        print(f"- **Predict Proba (Classes)**: {probabilities}")
        
    print("\n## 5. Baseline Sanity Model Comparison\n")
    # Baseline logic
    baseline_logit = 1.2 - (0.15 * raw_inputs[0]) - (2.5 * raw_inputs[4]) - (1.0 if raw_inputs[5] else 0.0)
    baseline_prob = 1.0 / (1.0 + np.exp(-baseline_logit))
    print(f"- **Baseline Logit**: {baseline_logit:.4f}")
    print(f"- **Baseline Probability**: {baseline_prob:.4f}")

    print("\n## 6. Response Curves\n")
    # Vary rolling_accuracy from 0.0 to 1.0
    print("### Sweeping: Rolling Accuracy (0.0 -> 1.0)")
    print("| Rolling Acc | Scaled Acc | Logit | Probability |")
    print("| :--- | :--- | :--- | :--- |")
    for acc in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        test_inputs = list(raw_inputs)
        test_inputs[4] = acc
        f_vec = np.array([test_inputs])
        s_vec = scaler.transform(f_vec)
        log_val = model.decision_function(s_vec)[0]
        prb = model.predict_proba(s_vec)[0][1] if len(model.classes_) > 1 else model.predict_proba(s_vec)[0][0]
        print(f"| {acc:.1f} | {s_vec[0][4]:.4f} | {log_val:.4f} | {prb:.4f} |")

if __name__ == "__main__":
    run_forensics()
