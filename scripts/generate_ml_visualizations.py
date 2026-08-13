import os
import sys
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, precision_recall_curve, f1_score, accuracy_score, brier_score_loss
from sklearn.calibration import calibration_curve
from sklearn.model_selection import train_test_split
import shap

def generate_visualizations():
    print("Loading artifacts...")
    model = joblib.load("Models/best_model_v2.pkl")
    scaler = joblib.load("Models/scaler_v2.pkl")
    
    # Load dataset. Taking a sample for speed since it's >400MB
    print("Loading dataset sample...")
    df = pd.read_csv("Data/Processed/model_ready_dataset.csv", nrows=100000)
    
    # Same engineering as training
    FORGET_THRESHOLD = 0.60
    df["forget_event"] = (df["future_accuracy"] < FORGET_THRESHOLD).astype(int)
    
    features = [
        "interaction_order", "past_attempts", "past_correct", 
        "past_accuracy", "rolling_accuracy", "mastered"
    ]
    
    df = df.dropna(subset=features + ["forget_event"])
    X = df[features]
    y = df["forget_event"]
    
    # Train/Test Split (Use same seed as training for consistency)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    X_test_scaled = scaler.transform(X_test)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    # Output Directory
    os.makedirs("reports/figures", exist_ok=True)
    
    print("Generating Calibration Plot...")
    prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)
    plt.figure(figsize=(8, 6))
    plt.plot(prob_pred, prob_true, marker='o', label="Logistic Regression v2")
    plt.plot([0, 1], [0, 1], linestyle='--', label="Perfectly Calibrated")
    plt.xlabel("Predicted Probability")
    plt.ylabel("Observed Frequency")
    plt.title("Reliability Diagram (Calibration Plot)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("reports/figures/calibration_plot.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("Optimizing Decision Threshold...")
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_prob)
    
    # Maximize F1
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    opt_idx = np.argmax(f1_scores)
    opt_threshold = thresholds[opt_idx]
    
    print(f"Optimal Threshold (Max F1): {opt_threshold:.3f}")
    
    plt.figure(figsize=(8, 6))
    plt.plot(thresholds, f1_scores[:-1], label="F1 Score")
    plt.plot(thresholds, precisions[:-1], label="Precision")
    plt.plot(thresholds, recalls[:-1], label="Recall")
    plt.axvline(opt_threshold, color='red', linestyle='--', label=f'Optimal Thresh: {opt_threshold:.2f}')
    plt.xlabel("Threshold")
    plt.ylabel("Score")
    plt.title("Threshold Optimization")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("reports/figures/threshold_optimization.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generating ROC and PR Curves...")
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    from sklearn.metrics import auc
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC)')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.savefig("reports/figures/roc_curve.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    pr_auc = auc(recalls, precisions)
    plt.figure(figsize=(8, 6))
    plt.plot(recalls, precisions, color='blue', lw=2, label=f'PR curve (AUC = {pr_auc:.3f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc="lower left")
    plt.grid(True, alpha=0.3)
    plt.savefig("reports/figures/pr_curve.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("Generating Confusion Matrix...")
    y_pred_opt = (y_prob >= opt_threshold).astype(int)
    cm = confusion_matrix(y_test, y_pred_opt)
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Retention (0)', 'Forgetting (1)'],
                yticklabels=['Retention (0)', 'Forgetting (1)'])
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title(f"Confusion Matrix (Threshold = {opt_threshold:.2f})")
    plt.savefig("reports/figures/confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generating SHAP Summary Plot...")
    # SHAP explainer for Logistic Regression (LinearExplainer)
    # Using a smaller background dataset for speed
    explainer = shap.LinearExplainer(model, X_train[:1000])
    shap_values = explainer.shap_values(X_test_scaled[:1000])
    
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test[:1000], feature_names=features, show=False)
    plt.title("SHAP Summary Plot")
    plt.savefig("reports/figures/shap_summary.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Done. Optimal F1 Threshold is {opt_threshold:.3f}")
    
    # Save optimal threshold info for report
    with open("reports/figures/optimal_metrics.txt", "w") as f:
        f.write(f"Optimal Threshold: {opt_threshold:.3f}\n")
        f.write(f"Confusion Matrix:\nTN={cm[0,0]}, FP={cm[0,1]}\nFN={cm[1,0]}, TP={cm[1,1]}\n")

if __name__ == "__main__":
    generate_visualizations()
