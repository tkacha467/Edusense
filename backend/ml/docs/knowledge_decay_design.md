# EduSense AI — Knowledge Decay Prediction Engine v1.0
## Machine Learning Design & Architecture Specification

### 1. Research Objective
The primary objective of the EduSense AI Knowledge Decay Predictor ($v1.0$) is to predict the probability $P(\text{forgotten} = 1 \mid \mathbf{x}_{i,s,t})$ that student $i$'s mastery of skill $s$ will fall below the target performance threshold ($\theta_{\text{mastery}} = 0.70$) at a specified future prediction horizon $H = 7$ days.

This binary probability score provides the foundation for automated spaced-repetition scheduling, personalized review interventions, and faculty at-risk student monitoring.

---

### 2. Prediction Unit & Temporal Integrity

- **Prediction Unit**: $(i, s, t)$ where $i$ is `student_id`, $s$ is `skill_id` (or `subject_id`), and $t$ is `prediction_time` (the cutoff timestamp).
- **Temporal Strictness**: Feature vectors $\mathbf{x}_{i,s,t}$ are computed using historical response events occurring strictly **before** timestamp $t$ ($\tau < t$).
- **Observation Window**: All attempts prior to $t$.
- **Prediction Horizon ($H$)**: $[t, t + 7\text{ days}]$.
- **Leakage Prevention**: Response data recorded at or after timestamp $t$ ($\tau \ge t$) is strictly excluded from feature calculation and used solely for target label computation during offline training.

---

### 3. Target Definition

The binary target label $y_{i,s,t} \in \{0, 1\}$ is defined deterministically based on empirical performance during the prediction horizon $[t, t + H]$:

$$
y_{i,s,t} = \begin{cases}
1 & \text{if } \text{Accuracy}_{[t, t+H]} < 0.70 \text{ (Forgotten / Knowledge Decay)} \\
0 & \text{if } \text{Accuracy}_{[t, t+H]} \ge 0.70 \text{ (Retained / Mastered)}
\end{cases}
$$

If no assessment attempts occur within $[t, t+H]$, the instance is labeled using exponential forgetting curve decay extrapolation based on Ebbinghaus memory stability parameters.

---

### 4. Feature Taxonomy & Classification

| Feature Name | Type | Classification | Rationale & Description |
| :--- | :--- | :--- | :--- |
| `days_since_last_review` | float | **ENGINEERED** | $t - \tau_{\text{last}}$ in days. Key driver of memory decay. |
| `historical_accuracy` | float | **USEFUL** | Overall fraction of correct answers prior to $t$. |
| `consecutive_correct_streak` | int | **ENGINEERED** | Count of consecutive correct responses immediately prior to $t$. |
| `avg_response_time_seconds` | float | **USEFUL** | Mean latency across prior attempts. Indicator of recall fluency. |
| `decay_vulnerability_index` | float | **ENGINEERED** | Composite index $(1 - p) \cdot (1 + 0.05 \cdot \text{days})$. |
| `practice_frequency` | float | **ENGINEERED** | Number of practice attempts per week prior to $t$. |
| `total_attempts` | int | **USEFUL** | Cumulative number of problem attempts prior to $t$. |
| `correct_attempts` | int | **USEFUL** | Count of correct problem attempts prior to $t$. |
| `future_accuracy` | float | **POTENTIAL LEAKAGE** | **EXCLUDED**. Performance after $t$ is target data only. |
| `session_id` | str | **IRRELEVANT** | Database UUID; excluded from feature vector. |

---

### 5. Temporal Dataset Splitting Strategy

To mirror real-world deployment where models predict future performance from past data, instances are split chronologically rather than randomly:

- **Train Set**: Earliest 70% of chronological instances.
- **Validation Set**: Next 15% of chronological instances (hyperparameter tuning & calibration).
- **Test Set**: Latest 15% of chronological instances (final out-of-time evaluation).

No student or skill identity overlap is permitted to pollute feature distributions across temporal boundaries.

---

### 6. Model Architecture & Evaluation Metrics

#### Baseline & Models Evaluated
1. **Logistic Regression** (Standardized L2 Regularized Baseline)
2. **Random Forest Classifier** (Non-linear Ensemble)
3. **XGBoost Classifier** (Gradient Boosted Trees)

#### Metric Prioritization
Because knowledge decay prediction exhibits class imbalance, evaluation prioritizes:
- **PR-AUC (Precision-Recall Area Under Curve)**: Primary metric for imbalanced positive class ($y=1$).
- **ROC-AUC**: Overall discrimination capability across thresholds.
- **Recall @ 70% Precision**: Ability to catch at-risk students while maintaining low false-alarm rates.
- **Brier Calibration Score**: $BS = \frac{1}{N}\sum (\hat{p}_i - y_i)^2$. Validates that a score of $0.80$ means an $80\%$ probability of forgetting.

---

### 7. Risk Bands & Decision Boundaries

- **LOW Risk**: Forget Probability $P < 0.35$ $\rightarrow$ Recommended Review: 15–30 days.
- **MEDIUM Risk**: $0.35 \le P < 0.65$ $\rightarrow$ Recommended Review: 4–7 days.
- **HIGH Risk**: $P \ge 0.65$ $\rightarrow$ Recommended Review: 1–3 days (Urgent Intervention).

---

### 8. Limitations & Scope Constraints
- **Cold-Start Handling**: Students with zero prior attempts receive default population prior estimates ($P = 0.50$, Medium Risk).
- **Model Scope**: $v1.0$ is optimized for single-topic and multi-topic MCQ skills.
- **Local Runtime**: Inference runs locally in under 15ms per student prediction without requiring GPU hardware.
