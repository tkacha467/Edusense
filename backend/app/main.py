"""FastAPI application entry point."""
from typing import Any, Dict

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.exceptions import EduSenseException
from app.routers import include_routers
from app.dependencies.database import get_db
from sqlalchemy.orm import Session

from app.middleware.security import ProductionSecurityMiddleware


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered adaptive learning platform API"
    )

    app.add_middleware(ProductionSecurityMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(EduSenseException)
    async def edusense_exception_handler(request: Request, exc: EduSenseException) -> JSONResponse:
        """Handle custom EduSense exceptions with standardized error payload."""
        content: Dict[str, Any] = {
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.message,
                "status_code": exc.status_code,
                "details": exc.detail
            }
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

    # Register API v1 module routers
    include_routers(app, prefix="/api/v1")

    @app.get("/health", tags=["Health"])
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "version": settings.APP_VERSION}

    @app.get("/ready", tags=["Health"])
    async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, str]:
        """Readiness check endpoint."""
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            return {"status": "ready", "database": "connected", "ai_engine": "operational"}
        except Exception:
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Database not ready")

    @app.get("/live", tags=["Health"])
    async def liveness_check() -> Dict[str, str]:
        """Liveness check endpoint."""
        return {"status": "alive"}

    @app.get("/", tags=["Root"])
    async def root() -> Dict[str, str]:
        """Root endpoint."""
        return {"app": settings.APP_NAME, "version": settings.APP_VERSION}

    return app


app = create_app()
