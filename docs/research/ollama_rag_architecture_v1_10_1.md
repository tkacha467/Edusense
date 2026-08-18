# EduSense AI — Existing Ollama & RAG Architecture Audit (v1.10.1)

**Repository**: `tkacha467/Edusense`  
**Branch**: [`feature/faculty-dashboard`](https://github.com/tkacha467/Edusense/tree/feature/faculty-dashboard)  
**Date**: August 18, 2026  
**System Milestone**: `v1.10.1 — Ollama + RAG Grounding & Production Validation`

---

## 1. Audit Summary of Existing LLM Implementation

### A. Ollama Service (`backend/app/services/ollama_service.py`)
- **Local Endpoint**: `http://localhost:11434/api/generate`
- **Default Model**: `llama3.2`
- **Connection Protocol**: `httpx` with `urllib.request` fallback.
- **Current Usage**:
  - Context-injected free-form query (`query_local_ollama`)
  - Dynamic MCQ question generation (`generate_questions_with_ollama`)
- **Identified Limitations**:
  - Unstructured free-form text responses without strict JSON schema validation.
  - Basic context injection rather than RBAC-enforced retrieval.
  - Lack of explicit grounding guards to prevent numerical metric hallucination.

---

## 2. Target Production RAG & AI Architecture

```text
┌─────────────────────────┐
│ Knowledge Decay ML Model │ (Deterministic Champion: Logistic + Isotonic Calibration)
└────────────┬────────────┘
             │
       Numerical Risk (Sole Source of Truth: forget_probability, risk_level, revision_date)
             │
             ▼
┌─────────────────────────┐
│ Deterministic Scheduler │ (Adaptive Scheduler: Bounded [1, 30 days] Intervals)
└────────────┬────────────┘
             │
   Recommendation Data
             │
             ▼
┌─────────────────────────┐
│   RBAC RAG Service      │ (Database-backed Student Context & Academic Knowledge Retrieval)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     Ollama llama3.2     │ (Local LLM Explanation & MCQ Generation Layer)
└────────────┬────────────┘
             │
             ▼
   Structured Response / Teaching Guidance
```

### Key Invariants
1. **Source of Truth**: Deterministic ML backend is the **sole source of truth** for `forget_probability`, `risk_level`, and `recommended_revision_date`.
2. **LLM Boundary**: Ollama is strictly an **explanation and generation layer**. It MUST NOT calculate or alter numerical ML probabilities.
3. **Data Isolation**: Student context is strictly isolated by authenticated user identity and RBAC role. Cross-student data leakage returns HTTP `403 Forbidden`.
