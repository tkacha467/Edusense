# EduSense AI — Knowledge Decay Model Comparison & Audit Report ($v1.1$)

**Model Version**: `knowledge-decay-v1.1`  
**Selected Champion Model**: `Logistic Regression`  
**Calibration Method**: `Isotonic Regression`  
**Evaluation Timestamp**: `2026-08-18T06:56:40.345484+00:00`  
**Dataset Size**: `500 samples` (`Train: 350`, `Val: 75`, `Test: 75`)

## 1. Candidate Model & Baseline Performance Matrix

| Model Candidate | PR-AUC | ROC-AUC | Precision | Recall | F1 Score | Brier Score | Training Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline (Class Prior)** | **0.2486** | 0.5 | 0.0 | 0.0 | 0.0 | **0.1892** | 0.01 |
| **Baseline (Time Heuristic)** | **0.9126** | 0.9596 | 1.0 | 0.4737 | 0.6429 | **0.0869** | 0.01 |
| **Logistic Regression (Selected Champion)** | **0.9729** | 0.9859 | 1.0 | 0.8421 | 0.9143 | **0.0323** | 9.44 |
| **Random Forest** | **0.945** | 0.9737 | 0.9375 | 0.7895 | 0.8571 | **0.0553** | 108.18 |
| **Gradient Boosting** | **0.9244** | 0.9671 | 0.875 | 0.7368 | 0.8 | **0.0671** | 83.88 |
| **XGBoost** | **0.961** | 0.9774 | 0.9375 | 0.7895 | 0.8571 | **0.041** | 235.67 |

## 2. Student-Level Generalization Test (Unseen Students Holdout)
- **Unseen Test Students**: `8`
- **PR-AUC**: `0.9396`
- **ROC-AUC**: `0.9766`
- **Brier Score**: `0.0504`

## 3. Calibration Evaluation
- **Uncalibrated Model Brier Score**: `0.0323`
- **Platt Scaling (Sigmoid) Brier Score**: `0.0338`
- **Isotonic Regression Brier Score**: `0.0310`
- **Selected Strategy**: `Isotonic Regression`
