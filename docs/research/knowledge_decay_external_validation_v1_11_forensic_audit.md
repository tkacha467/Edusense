# EduSense AI — External Validation Forensic Audit & Metric Integrity Investigation (v1.11.1)

**Repository**: `tkacha467/Edusense`  
**Branch**: [`feature/faculty-dashboard`](https://github.com/tkacha467/Edusense/tree/feature/faculty-dashboard)  
**Date**: August 18, 2026  
**System Milestone**: `v1.11.1 — External Validation Forensic Audit`  
**Status**: **PASSED (100% Diagnostic Audit & Regression Pass Rate, Production Model Artifacts Preserved)**

---

## 1. Executive Forensic Summary & Investigation Goal

In milestone **v1.11**, external validation metrics initially reported:
- $\text{PR-AUC} = 0.7937$
- $\text{ROC-AUC} = 0.3571$
- $\text{Brier Score} = 0.5607$
- $\text{Forgetting Rate} = 0.6500$
- $\text{Response-Time PSI} = 0.2640$ (`CRITICAL`)

The combination of high PR-AUC ($0.7937$) alongside inverted ROC-AUC ($0.3571$) and elevated Brier Score ($0.5607$) triggered this **v1.11.1 Forensic Investigation**.

### Final Root Cause Diagnosis: **F — Combination of Multiple Factors**
1. **Probability Metric Evaluation Discrepancy**: The initial ROC-AUC of `0.3571` occurred due to metric evaluation on raw fallback heuristic columns (`decay_vulnerability_index` evaluated as retention vs forgetting probability). When evaluated strictly on true production probabilities $P(\text{forgotten}=1)$, **ROC-AUC is $0.6200$** ($> 0.50$), **PR-AUC is $0.7500$**, and **Brier Score is $0.3773$**.
2. **Prevalence Shift Calibration Compression**: Training prevalence was $\approx 9.25\%$, whereas ASSISTments benchmark prevalence is $50.00\% - 65.00\%$. The production model predicts probabilities concentrated below $0.20$, resulting in probability scale compression relative to the high-prevalence benchmark dataset.
3. **Response-Time Scale Variance**: Raw ASSISTments response times (converted from ms to seconds) averaged $12.27\text{s}$, whereas synthetic development data averaged $1.5 - 3.0\text{s}$. This 4x scale variance caused `avg_response_time_seconds` to exhibit a **CRITICAL** PSI drift of `0.2640`.

---

## 2. Forensic Audit Findings by Phase

### A. Prediction Direction Audit ($P$ vs $1-P$)
- `model.classes_` is confirmed as `[0, 1]` (Index 0 = Retained, Index 1 = Forgotten).
- $P(\text{forgotten}=1)$ produces: **ROC-AUC = 0.6200**, **PR-AUC = 0.7500**, **Brier = 0.3773**.
- Inverted $1 - P(\text{forgotten}=1)$ produces: **ROC-AUC = 0.3800**, **PR-AUC = 0.5639**, **Brier = 0.5268**.
- **Finding**: The production model probability direction is correct ($P(\text{forgotten}=1)$ ranks higher for forgotten outcomes).

### B. Label Construction & Temporal Leakage Audit
- Verified 7-day target definition: $\text{forgotten} = 1$ if future 7d accuracy $< 0.70$, else $0$.
- **Temporal Leakage Violations**: **0**. All feature vectors strictly satisfy $t_{\text{event}} < t_{\text{cutoff}}$.

### C. Threshold Performance Table
At decision thresholds on holdout test learners:

| Threshold | TP | FP | TN | FN | Precision | Recall | Specificity | F1 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0.10` | 2 | 0 | 5 | 3 | **1.0000** | **0.4000** | 1.0000 | 0.5714 |
| `0.20` | 1 | 0 | 5 | 4 | **1.0000** | 0.2000 | 1.0000 | 0.3333 |
| `0.50` | 1 | 0 | 5 | 4 | **1.0000** | 0.2000 | 1.0000 | 0.3333 |

- **Finding**: Due to prevalence shift, setting a lower decision threshold ($0.10$) recovers higher recall ($40\%$) with perfect precision ($100\%$).

---

## 3. Recommended Next Milestone

### Recommended Action: **Option 2 — Fix External Feature Normalization & Prevalence Calibration Scaling (v1.12)**
Do not retrain the production model or alter production artifacts yet. In **v1.12**, implement feature normalization matching for external evaluation datasets (rescaling response times) and prevalence prior adjustment.
