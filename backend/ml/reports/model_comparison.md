# EduSense AI — Knowledge Decay Model Comparison Report ($v1.0$)

**Model Version**: `knowledge-decay-v1.0`  
**Selected Champion Model**: `Logistic Regression`  
**Evaluation Timestamp**: `2026-08-18T06:25:58.774248+00:00`  
**Dataset Size**: `400 samples` (`Train: 280`, `Val: 60`, `Test: 60`)

## Model Performance Metrics Matrix

| Model Candidate | PR-AUC | ROC-AUC | Precision | Recall | F1 Score | Brier Score | Training Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression (Selected)** | **1.0** | 1.0 | 1.0 | 1.0 | 1.0 | **0.0193** | 6.6 |
| **Random Forest** | **0.8122** | 0.965 | 0.6667 | 0.5714 | 0.6154 | **0.0478** | 102.81 |
| **Gradient Boosting** | **0.8386** | 0.9677 | 0.7143 | 0.7143 | 0.7143 | **0.0599** | 102.6 |
| **XGBoost** | **0.7572** | 0.9623 | 0.6667 | 0.5714 | 0.6154 | **0.0628** | 123.5 |

## Calibration & Selection Rationale
- **Selection Rule**: Champion model selected by maximizing `PR-AUC - Brier_Score` to ensure high recall on at-risk students while maintaining well-calibrated probabilities.
- **Calibrated Brier Score**: `0.0289` using Platt Sigmoid Scaling.
