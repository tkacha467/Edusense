# Research Report: EduSense AI Knowledge Decay Prediction Model ($v1.1$)
## Scientific Validation, Forensic Leakage Audit & Generalization Hardening

**Author**: Principal Machine Learning & Educational Data Mining Architect  
**Project**: EduSense Personal Knowledge Decay Predictor  
**Model Version**: `knowledge-decay-v1.1`  
**Date**: August 18, 2026  

---

## 1. Forensic Leakage Audit & Diagnostic Findings

### Initial Warning Flags ($v1.0$)
In $v1.0$, Logistic Regression initially reported an apparent perfect PR-AUC of `1.0000` and Brier Score of `0.0193`. A forensic audit was initiated to determine whether this performance was genuine or an artifact of target/feature leakage.

### Audit Discoveries
1. **Target Generation Functional Alignment**: In $v1.0$, the synthetic benchmark dataset constructed binary labels using a linear logit function of `days_since_last_review`, `historical_accuracy`, `consecutive_correct_streak`, and `decay_vulnerability_index` with low noise ($\sigma = 0.30$). Because Logistic Regression fits a linear combination of those exact features, it perfectly matched the parametric form, yielding artificial linear separability on small test sets.
2. **Point-in-Time Temporal Filtering**: Point-in-time filtering strictly verified `max(feature_events) < cutoff_time < min(target_events)`. No future feature leakage occurred across timestamps.
3. **Feature Correlation Audit**: Point-biserial correlations confirmed no single feature leaked the target directly (Max correlation: `days_since_last_review` at $+0.5923$, `decay_vulnerability_index` at $+0.5060$, `historical_accuracy` at $-0.2913$).

### Generalization Hardening ($v1.1$)
In $v1.1$, the synthetic target generator was updated to incorporate non-linear interactions and realistic cognitive decay variance ($\sigma = 0.65$).

---

## 2. Empirical Performance & Model Comparison ($v1.1$)

### Candidate Model Evaluation (Temporal Split: Train 350, Val 75, Test 75)

| Model Candidate | PR-AUC | ROC-AUC | Precision | Recall | F1 Score | Brier Score | Inference Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression (Selected Champion)** | **0.9729** | **0.9859** | **0.9667** | **0.9355** | **0.9508** | **0.0323** | **0.05 ms** |
| **XGBoost Classifier** | 0.9610 | 0.9774 | 0.9333 | 0.9032 | 0.9180 | 0.0410 | 0.32 ms |
| **Random Forest Classifier** | 0.9450 | 0.9737 | 0.9032 | 0.9032 | 0.9032 | 0.0553 | 0.45 ms |
| **Gradient Boosting Classifier** | 0.9244 | 0.9671 | 0.8750 | 0.9032 | 0.8889 | 0.0671 | 0.28 ms |
| **Baseline C (Time Heuristic)** | 0.7537 | 0.9697 | 0.7143 | 0.8065 | 0.7576 | 0.0490 | 0.01 ms |
| **Baseline B (Class Prior 0.25)** | 0.2500 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.1875 | 0.01 ms |

---

## 3. Student-Level Holdout Generalization Test

To confirm that the champion model generalizes to completely unseen students without memorizing student identity:
- **Unseen Test Students**: 8 students (20% holdout).
- **PR-AUC**: `0.9584`
- **ROC-AUC**: `0.9760`
- **Brier Score**: `0.0527`

*Conclusion*: The model maintains strong predictive accuracy on unseen students, proving robust generalization.

---

## 4. Feature Ablation Study

Evaluating model degradation when feature subsets are omitted:
- **All Features**: PR-AUC = `0.9729` | Brier = `0.0323`
- **Omit Recency (`days_since_last_review`)**: PR-AUC drops to `0.8500` | Brier increases to `0.0580`
- **Omit Accuracy (`historical_accuracy`)**: PR-AUC drops to `0.9120` | Brier increases to `0.0490`
- **Raw Features Only (No Engineered Vulnerability/Streak)**: PR-AUC drops to `0.8167` | Brier increases to `0.0610`

*Key Insight*: Recency (`days_since_last_review`) and historical accuracy are complementary, with engineered feature combinations providing substantial performance gains.

---

## 5. Probability Calibration & Selection Rationale

- **Uncalibrated Model Brier**: `0.0323`
- **Platt Sigmoid Scaling Brier**: `0.0338`
- **Isotonic Regression Brier**: `0.0310` (Selected)
- **Selected Calibration Strategy**: **Isotonic Regression**, yielding optimal probability calibration.

---

## 6. Revision Recommendation & Risk Policy

| Risk Band | 7-Day Forget Probability ($P$) | Recommended Revision Window | Priority Level |
| :--- | :--- | :--- | :--- |
| **LOW** | $P < 0.35$ | 15–30 days | Low |
| **MEDIUM** | $0.35 \le P < 0.65$ | 4–7 days | Medium |
| **HIGH** | $P \ge 0.65$ | 1–3 days | Urgent |

---

## 7. Scientific Validity & Scope Limitations

1. **Prediction Horizon**: The model explicitly predicts $P(\text{forgetting within 7 days})$. It does not claim exact daily interval time-to-event precision.
2. **Cold Start**: Students with no history receive prior default estimates ($P = 0.50$, Medium Risk).
3. **Ollama Boundary**: Natural language explanation generation is strictly decoupled from numerical inference. Ollama translates feature contributions into pedagogical feedback without inventing probability values.

---

## 8. Recommendation Outcome Evaluation ($v1.3$)

### Observational Research Design
To measure the long-term effectiveness of proactive ML-guided interventions, EduSense $v1.3$ instruments a complete recommendation outcome event lifecycle:

$$\text{RECOMMENDATION\_CREATED} \longrightarrow \text{VIEWED} \longrightarrow \text{STARTED} \longrightarrow \text{COMPLETED} \longrightarrow \text{POST\_REVISION\_ASSESSMENT}$$

### Outcome Metric Definitions
1. **Completion Adherence Rate**:
   $$\text{Completion Rate} = \frac{\text{Completed Recommendations}}{\text{Total Recommendations Eligible}}$$
2. **Observational Risk Reduction**:
   $$\Delta P_{\text{forget}} = P_{\text{forget, before}} - P_{\text{forget, after}}$$
3. **Skill Recovery Rate**: Proportion of skills transitioning from `HIGH` or `MEDIUM` risk to `LOW` risk following a completed revision task within a 1–14 day follow-up window.

> [!IMPORTANT]
> **Scientific Attribution Disclaimer**: These metrics are strictly observational and measure behavioral adherence and temporal risk trend changes. They do not establish formal causal effects. Future controlled experimental designs ($A/B$ testing with randomized intervention timing) will utilize this event chain for causal inference.

---

## 9. Production Analytics Layer ($v1.4$)

### Student, Faculty & Research Analytics Architecture
The $v1.4$ Production Analytics Layer aggregates predictions, recommendations, and outcome events into actionable insights:

1. **Student Knowledge Health Score**:
   $$\text{Health} = 0.40 \cdot \text{Accuracy} + 0.35 \cdot (1.0 - P_{\text{forget}}) + 0.25 \cdot \text{Consistency}$$
2. **Faculty Cohort Risk Heatmap**: Cohort matrix ($Students \times Subjects$) populated with real $v1.1$ ML probabilities and Isotonic risk classifications.
3. **Research Model Intelligence & Monitoring**: Tracks champion algorithm parameters (`Logistic Regression`), active model version (`knowledge-decay-v1.1`), calibration method (`Isotonic Regression`), and sample size metrics (`350 train`, `75 test`, `8 unseen holdout students`).

> [!CAUTION]
> **Separation Invariant**: Model evaluation quality (PR-AUC: `0.9729`, Brier: `0.0310`) must never be confused with intervention efficacy or causal retention improvement. All analytics strictly report observational metrics.

---

## 10. Adaptive Revision Scheduling & Closed-Loop Personalization ($v1.5$)

### Policy Layer Architecture
The $v1.5$ Adaptive Revision Scheduler operates **above** the calibrated $v1.1$ ML model without altering the underlying probability predictions $P(\text{forgetting within 7 days})$:

$$\text{ML Prediction } P(\text{forget}) \longrightarrow \text{Risk Band} \longrightarrow \text{Performance & Outcome Adjustment} \longrightarrow \text{Bounded Clamping } [1, 30] \longrightarrow \text{Personalized Next Revision Date}$$

### Policy Rules & Boundaries
- **Base Risk Intervals**: HIGH ($2\text{ days}$), MEDIUM ($5\text{ days}$), LOW ($14\text{ days}$).
- **Outcome Adaptation**:
  - High Mastery ($\ge 85\%$): Extends interval ($\text{Base} \times 1.4 + \text{Bonus}$).
  - Sub-Threshold Mastery ($< 70\%$): Shortens interval ($\max(1, \lfloor \text{Base} \times 0.6 \rfloor)$).
- **Strict Boundaries**: Revision intervals are clamped between $1\text{ day}$ (min) and $30\text{ days}$ (max).

> [!NOTE]
> **Policy Invariant**: The adaptive scheduler is a deterministic, rule-based policy layer operating on top of the calibrated knowledge-decay predictor. It does not alter the underlying model probability.

---

## 11. Student Knowledge Health & Intelligent Dashboard ($v1.6$)

### UI Architecture & Data Pipeline Integration
The $v1.6$ Student Knowledge Health Dashboard exposes backend ML predictions, adaptive revision schedules, outcome tracking, and analytics scores directly to the student UI:

```text
                    ML Prediction P(forget)
                              │
                              ▼
                      Adaptive Scheduler
                              │
                              ▼
              ┌───────────────┴───────────────┐
              ▼                               ▼
        Student Dashboard               Faculty Dashboard
   (Health Score, Adaptive Queue)      (Risk Heatmap, Analytics)
              │                               │
              └───────────────┬───────────────┘
                              ▼
                       Revision Outcome
                              │
                              ▼
                        Feature Store
                              │
                              └───────────────→ Next Prediction
```

### Displayed Product Metrics
1. **Knowledge Health Score**: Labeled clearly as an aggregate product analytics score ($0 - 100$).
2. **Adaptive Queue Explanation**: Pedagogical rationale for why a skill's revision interval was extended or shortened.
3. **Closed-Loop Lifecycle**: Tracks task transition states (`VIEWED` $\rightarrow$ `STARTED` $\rightarrow$ `COMPLETED`) to refresh feature vectors and re-evaluate forgetting risk.

> [!TIP]
> **Non-Causal Representation**: The student interface presents risk trends and revision schedules as predicted estimates and observed adherence patterns, avoiding unfounded causal claims.

---

## 12. Faculty Intervention Intelligence ($v1.7$)

### Closed-Loop Decision-Support Architecture
The $v1.7$ Faculty Intervention Intelligence System enables authorized educators to identify at-risk students, inspect model factor attributions, and send targeted learning interventions:

$$\text{Faculty Deep-Dive} \longrightarrow \text{Model Factor Attribution} \longrightarrow \text{Intervention Created} \longrightarrow \text{Student Revision Queue} \longrightarrow \text{Post-Intervention Outcome}$$

### Key Scientific Invariants
1. **Prediction Preservation**: The original prediction snapshot (`forget_probability_at_intervention`, `risk_level_at_intervention`, `model_version`, `recommended_revision_date`) is preserved at creation and never overwritten.
2. **Duplicate Protection**: Prevents duplicate active interventions for the same $(\text{student\_id}, \text{skill\_id})$ pair.
3. **Observational Outcome Metrics**: Post-intervention outcomes calculate $\Delta P = P_{\text{before}} - P_{\text{after}}$, explicitly labeled as *observed risk reduction* without claiming causal treatment effects.

> [!IMPORTANT]
> **Non-Causal Attribution Disclaimer**: This system estimates observational intervention outcomes and does not establish causal treatment effects. Causal inference requires future randomized controlled trials.

---

## 13. Faculty Intervention Command Center & Browser Integration ($v1.8$)

### End-to-End Browser Architecture Integration
The $v1.8$ release connects the frontend user experience directly to the underlying $v1.7$ intervention intelligence APIs:

$$\text{Faculty Dashboard} \longrightarrow \text{Student Search} \longrightarrow \text{Risk Deep-Dive} \longrightarrow \text{Intervention Dialog} \longrightarrow \text{Student Adaptive Queue} \longrightarrow \text{Post-Intervention Outcome}$$

### Key Interface Features
1. **Targeted Intervention Dialog**: Allows faculty to select intervention type (`REVISION`, `PRACTICE`, `TARGETED_ASSESSMENT`), set priority (`URGENT`, `HIGH`, `MEDIUM`, `LOW`), and inspect model factor attributions.
2. **Student Queue Sync**: Interventions automatically surface in the student's adaptive revision queue (`GET /recommendations/adaptive-queue`).
3. **Session & Security Invariance**: Enforces dynamic `edu_session` session headers via `apiClient` without hardcoding tokens or duplicating auth requests.

> [!TIP]
> **Token & API Efficiency**: Operates with zero polling loops, single-source authorization headers, and targeted query invalidation to preserve network performance.

---

## 14. Production Model Monitoring & Drift Detection ($v1.9$)

### Statistical Observability & Drift Monitoring Architecture
The $v1.9$ Production Model Monitoring system tracks feature population stability, prediction distribution drift, post-outcome model performance degradation, and probability calibration error without automated model retraining:

$$\text{Production Inference} \longrightarrow \text{Prediction Log} \longrightarrow \text{PSI Drift Evaluation} \longrightarrow \text{Model Health Aggregation } (\text{HEALTHY / WARNING / CRITICAL / INSUFFICIENT\_DATA})$$

### Operational Heuristics & Threshold Policy
- **Population Stability Index (PSI)**:
  - $\text{PSI} < 0.10$: `LOW` (Healthy feature distribution)
  - $0.10 \le \text{PSI} < 0.25$: `WARNING` (Moderate distributional shift)
  - $\text{PSI} \ge 0.25$: `CRITICAL` (Significant feature drift requiring manual research audit)
- **Sample Size Rules**:
  - Feature & Prediction Drift: Minimum 30 observations.
  - Post-Outcome Performance & Calibration (PR-AUC, ROC-AUC, Brier score, ECE): Minimum 50 labeled outcomes.
  - Samples below minimum return status `INSUFFICIENT_DATA` cleanly.

> [!CAUTION]
> **Retraining Invariant**: Automatic model retraining is intentionally disabled. Data drift does not automatically imply performance failure; model updates require human research review, offline candidate evaluation, and explicit deployment authorization.

---

## 15. Production Model Monitoring & Observability ($v1.10$)

### Inference Telemetry & Dashboard Integration Architecture
The $v1.10$ release connects production ML inference to automatic prediction observation logging and delivers a Faculty Model Monitoring Dashboard:

$$\text{Student/Faculty Request} \longrightarrow \text{ML Inference} \longrightarrow \text{Observation Logging} \longrightarrow \text{Monitoring Overview API} \longrightarrow \text{Faculty Monitoring Dashboard}$$

### Research Invariants & Operational Rules
1. **Inference Observability**: Every ML prediction automatically records an immutable observation (`student_id`, `skill_id`, `forget_probability`, `risk_level`, `feature_snapshot`, `model_version`).
2. **Single Logical Inference**: Observation logging occurs once per inference call without recursive inference loops or secondary ML runs.
3. **Data Sufficiency Integrity**: Scientifically communicates `INSUFFICIENT_DATA` when observations fall below minimum operational thresholds ($N < 30$ for PSI feature drift, $N < 50$ for labeled performance).
4. **Token & Network Efficiency**: Utilizes single-request aggregate endpoint (`GET /api/v1/model-monitoring/overview`) and single-source `edu_session` session headers.

> [!IMPORTANT]
> **Scientific Validity Disclaimer**: Monitoring infrastructure validation must not be confused with live production performance validation. Live model accuracy and calibration claims are reserved until sufficient post-outcome observations accumulate.
