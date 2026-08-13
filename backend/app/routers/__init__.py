"""API Routers Package for EduSense AI."""
from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.onboarding import router as onboarding_router
from app.routers.student import router as student_router
from app.routers.faculty import router as faculty_router
from app.routers.learning import router as learning_router
from app.routers.assessment import router as assessment_router
from app.routers.knowledge import router as knowledge_router
from app.routers.recommendation import router as recommendation_router
from app.routers.notification import router as notification_router
from app.routers.ai import router as ai_router
from app.routers.rag import router as rag_router
from app.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "onboarding_router",
    "student_router",
    "faculty_router",
    "learning_router",
    "assessment_router",
    "knowledge_router",
    "recommendation_router",
    "notification_router",
    "ai_router",
    "rag_router",
    "admin_router",
    "include_routers",
]


def include_routers(app: FastAPI, prefix: str = "/api/v1") -> None:
    """Register all API v1 module routers with the FastAPI application."""
    app.include_router(auth_router, prefix=prefix)
    app.include_router(onboarding_router, prefix=prefix)
    app.include_router(student_router, prefix=prefix)
    app.include_router(faculty_router, prefix=prefix)
    app.include_router(learning_router, prefix=prefix)
    app.include_router(assessment_router, prefix=prefix)
    app.include_router(knowledge_router, prefix=prefix)
    app.include_router(recommendation_router, prefix=prefix)
    app.include_router(notification_router, prefix=prefix)
    app.include_router(ai_router, prefix=prefix)
    app.include_router(rag_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)
