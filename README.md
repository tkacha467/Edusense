# EduSense AI — AI-Powered Adaptive Learning & Knowledge Decay Predictor

[![CI/CD Pipeline](https://github.com/edusense-ai/edusense-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/edusense-ai/edusense-ai/actions)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org)
[![Pytest Coverage](https://img.shields.io/badge/Pytest_Pass_Rate-100%25-success.svg)](#)

---

## 🌟 Executive Summary

**EduSense AI** is an enterprise-grade AI-powered adaptive learning platform designed to predict student knowledge decay and deliver personalized, deterministic learning interventions.

By combining **Machine Learning (Scikit-Learn Random Forest / XGBoost Inference)**, **Deterministic Decision Engines**, **Google Gemini LLMs**, **ChromaDB RAG (Retrieval-Augmented Generation)**, and an interactive **React TypeScript Frontend**, EduSense AI dynamically prevents student knowledge decay before it occurs.

---

## 🏗 System Architecture Overview

```
                                  ┌───────────────────────────────┐
                                  │   React TypeScript Frontend   │
                                  └───────────────┬───────────────┘
                                                  │ REST APIs
                                                  ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                FastAPI Production Backend                                 │
│                                                                                           │
│  ┌───────────────────────┐   ┌────────────────────────┐   ┌────────────────────────────┐  │
│  │ Firebase Auth & RBAC  │   │  Assessment Engine &   │   │  Assessment Analytics &    │  │
│  │   JWT Verification    │   │  AI Question Generator │   │  Feature Engineering       │  │
│  └───────────────────────┘   └────────────────────────┘   └─────────────┬──────────────┘  │
│                                                                         │                 │
│                                                                         ▼                 │
│  ┌───────────────────────┐   ┌────────────────────────┐   ┌────────────────────────────┐  │
│  │   AI Platform Layer   │   │ Adaptive Decision      │   │  Knowledge Decay ML        │  │
│  │  Gemini + ChromaDB    │◀──│ Engine & Scheduler     │◀──│  Prediction Engine         │  │
│  └───────────────────────┘   └────────────────────────┘   └────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Modules & Roadmap

- [x] **Phase 0**: Vision, PRD, System Architecture & System Event Flow
- [x] **Phase 1**: Database Foundation (SQLAlchemy Models, Repositories, Services, Schemas)
- [x] **Phase 1.5**: Business Workflows, API Contracts, Sequence Diagrams
- [x] **Phase 2**: Firebase Authentication, JWT Verification, RBAC Guards & Core REST APIs
- [x] **Phase 3**: Assessment Engine, AI Question Gateway & Auto-Grading
- [x] **Phase 4**: Assessment Analytics, Stage A Feature Engineering & Stage B ML Inference Engine
- [x] **Phase 5**: Adaptive Learning Engine, Revision Planner, Scheduling & Notifications
- [x] **Phase 6**: Centralized AI Platform (`app/ai/`), Gemini LLM Provider, ChromaDB RAG & AI Assistant
- [x] **Phase 7**: Full-Stack Frontend ↔ Backend Integration (0 TypeScript Errors | 64 Pytest Passes)
- [x] **Phase 8**: Production Engineering, Docker Containerization, CI/CD, Security Middleware & Deployment

---

## 🧪 Testing & Quality Assurance

```bash
# Run backend pytest regression test suite
cd backend
python -m pytest --cov=app --cov-report=term-missing

# Run frontend production build & TypeScript verification
cd ../frontend
npm run build
```

---

## 🐳 Quick Deployment

```bash
# Launch full stack using Docker Compose
docker compose up --build
```

- Frontend App: `http://localhost:80`
- FastAPI OpenAPI Docs: `http://localhost:8000/docs`
- System Health Check: `http://localhost:8000/health`