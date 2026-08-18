# Adaptive Revision Scheduling & Closed-Loop Personalization ($v1.5$)
## Architecture & Policy Design Document

**Author**: Senior ML Architect & Lead Research Engineer  
**Project**: EduSense Personal Knowledge Decay Predictor  
**System Milestone**: `Knowledge Decay Predictor v1.5`  
**Date**: August 18, 2026  

---

## 1. Research & System Objective

The objective of EduSense $v1.5$ is to transition from an observational prediction dashboard into a **closed-loop adaptive learning system**.

### System Cycle
$$\text{Assessment} \longrightarrow \text{Feature Store} \longrightarrow \text{ML Prediction } P(\text{forget}) \longrightarrow \text{Risk Assessment} \longrightarrow \text{Adaptive Scheduler} \longrightarrow \text{Revision} \longrightarrow \text{Outcome} \longrightarrow \text{State Update}$$

### Key Scientific Invariants
1. **Model Independence**: The ML probability $P(\text{forgetting within 7 days})$ remains strictly untouched. Model predictions originate exclusively from the calibrated $v1.1$ ML engine (`Logistic Regression` with `Isotonic Regression`).
2. **Deterministic Adaptation Layer**: The adaptive scheduler operates **above** the ML model. It uses historical revision outcomes and recent accuracy trends to dynamically shorten or extend future revision intervals.
3. **Bounded Spaced Repetition**: Revision intervals are strictly bounded between $1\text{ day}$ (minimum) and $30\text{ days}$ (maximum) to prevent interval explosion or collapse.
4. **Point-in-Time & Historical Preservation**: Historical prediction records, recommendation creation timestamps, and outcome events are never overwritten.

---

## 2. Adaptive Student/Skill State Taxonomy

For each tuple $(i, s) = (\text{student\_id}, \text{skill\_id})$, the adaptive layer maintains state variables derived from persisted assessment responses and recommendation events:

| State Variable | Type | Description |
| :--- | :--- | :--- |
| `current_forget_probability` | `float` | Latest ML predicted probability $P(\text{forgetting}) \in [0.0, 1.0]$. |
| `current_risk_level` | `str` | Risk classification (`LOW`, `MEDIUM`, `HIGH`). |
| `previous_interval_days` | `int` | Previously recommended revision interval in days. |
| `new_interval_days` | `int` | Adaptively calculated next revision interval in days. |
| `adaptation_direction` | `str` | Policy adjustment direction (`EXTEND`, `SHORTEN`, `MAINTAIN`). |
| `adaptation_reason` | `str` | Human-readable pedagogical explanation for interval adjustment. |
| `successful_revision_count` | `int` | Number of completed revisions followed by above-threshold performance. |
| `consecutive_successes` | `int` | Consecutive successful revision cycles. |

---

## 3. Bounded Adaptive Scheduling Policy

### Step 1: Base Risk Interval Assignment
- **HIGH Risk ($P \ge 0.65$)**: Base Interval = $2\text{ days}$
- **MEDIUM Risk ($0.35 \le P < 0.65$)**: Base Interval = $5\text{ days}$
- **LOW Risk ($P < 0.35$)**: Base Interval = $14\text{ days}$

### Step 2: Outcome & Performance Adjustment
- **Recent Post-Revision Mastery ($\text{Accuracy} \ge 0.85$)**:
  - Extend interval: $\text{New Interval} = \lfloor \text{Base Interval} \times 1.4 \rfloor + \text{Bonus Days}$
  - Direction: `EXTEND`
  - Reason: *"Strong post-revision mastery achieved ($\ge 85\%$). Extending revision interval."*
- **Sub-Threshold Performance ($\text{Accuracy} < 0.70$)**:
  - Shorten interval: $\text{New Interval} = \max(1, \lfloor \text{Base Interval} \times 0.6 \rfloor)$
  - Direction: `SHORTEN`
  - Reason: *"Post-revision accuracy remained below mastery threshold. Shortening revision interval."*
- **Repeated Success Bonus**: $+2\text{ days}$ for every 2 consecutive successful revisions.

### Step 3: Boundary Clamping
$$\text{Final Interval} = \min(30, \max(1, \text{Calculated Interval}))$$

---

## 4. Cold-Start & Safety Controls

1. **Cold-Start Students**: Students with fewer than 3 attempts receive default prior estimates ($P = 0.50$, Base Interval = $5\text{ days}$, `adaptation_reason` = *"Default initial interval assigned for cold-start student"*).
2. **Student Isolation**: RBAC rules prevent Student A from querying or mutating Student B's adaptive state.
3. **No Reinforcement Learning / No Black Boxes**: Policy adjustments are 100% rule-based, deterministic, and explainable to students and faculty.
