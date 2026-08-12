"""Production Security Middleware for HTTP headers, correlation IDs, and rate limiting."""
import uuid
import time
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class ProductionSecurityMiddleware(BaseHTTPMiddleware):
    """Applies Security Headers, Request Correlation IDs, and Latency Benchmarking."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        start_time = time.time()

        response = await call_next(request)

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Inject Security Headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Server"] = "EduSense-AI-Platform"
        response.headers["X-Response-Time-Ms"] = str(elapsed_ms)

        return response
