# EduSense AI — Production Deployment & DevOps Guide

> **Version**: 1.0.0  
> **Status**: Production Grade  

---

## 1. Quickstart Deployment (Docker Compose)

### Development Environment
```bash
docker compose up --build
```
- Frontend: `http://localhost:80`
- FastAPI Swagger UI: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### Production Environment
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 2. Architecture & Container Layout

```
                        ┌────────────────────────┐
                        │      Client Browser    │
                        └───────────┬────────────┘
                                    │ HTTP / HTTPS (Port 80/443)
                                    ▼
                        ┌────────────────────────┐
                        │   Nginx Reverse Proxy  │
                        └───────────┬────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │ /                                 │ /api/v1
                  ▼                                   ▼
        ┌──────────────────┐                ┌──────────────────┐
        │ React Frontend   │                │ FastAPI Backend  │
        │ (Static Bundle)  │                │ (Uvicorn 4 Work) │
        └──────────────────┘                └─────────┬────────┘
                                                      │
                                      ┌───────────────┴───────────────┐
                                      ▼                               ▼
                            ┌──────────────────┐            ┌──────────────────┐
                            │ SQLite / Postgres│            │ ChromaDB Vector  │
                            │   Database DB    │            │    Repository    │
                            └──────────────────┘            └──────────────────┘
```

---

## 3. Environment Variables Reference

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Deployment mode (`development`, `production`) |
| `DATABASE_URL` | `sqlite:///./edusense.db` | SQLAlchemy connection string (SQLite / Postgres) |
| `GEMINI_API_KEY` | `""` | Google Gemini LLM API credentials key |
| `FIREBASE_PROJECT_ID` | `edusense-ai` | Firebase Auth tenant project identifier |
| `CHROMADB_COLLECTION` | `edusense_documents` | ChromaDB collection namespace |

---

## 4. CI/CD Pipeline Summary

Our GitHub Actions workflow ([`.github/workflows/ci.yml`](file:///d:/Personal%20Knowledge%20Decay%20Predictor/.github/workflows/ci.yml)) automatically triggers on every push to `main`:
1. **Backend Testing**: Runs `pytest --cov=app` across 64 unit and integration tests.
2. **Frontend Verification**: Executes `tsc -b` and `vite build` verifying zero TypeScript errors.
3. **Docker Build**: Validates `docker compose build` buildability.
