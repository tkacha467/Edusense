"""Firebase Authentication integration and token verification."""
import logging
from typing import Any, Dict, Optional

from app.config import get_settings
from app.core.exceptions import UnauthorizedException

logger = logging.getLogger(__name__)

_firebase_app_initialized = False


def initialize_firebase() -> bool:
    """Initialize Firebase Admin SDK if not already initialized."""
    global _firebase_app_initialized
    if _firebase_app_initialized:
        return True

    settings = get_settings()
    
    # Try importing firebase_admin
    try:
        import firebase_admin
        from firebase_admin import credentials
    except ImportError:
        logger.warning("firebase-admin package not installed. Operating in mock auth mode.")
        return False

    try:
        if not firebase_admin._apps:
            if settings.FIREBASE_CREDENTIALS_PATH and settings.FIREBASE_CREDENTIALS_PATH != "./firebase-credentials.json":
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            elif settings.FIREBASE_PROJECT_ID:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {"projectId": settings.FIREBASE_PROJECT_ID})
            else:
                logger.info("Firebase project ID / credentials not set. Firebase Auth initialized in offline/dev mode.")
                return False
        _firebase_app_initialized = True
        logger.info("Firebase Admin SDK successfully initialized.")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        return False


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verify Firebase ID token and return claims dictionary.
    
    In development mode or when firebase-admin is not initialized, supports
    mock token format: 'dev-token-{uid}' or 'mock-token-{uid}' for testing.
    """
    if not id_token:
        raise UnauthorizedException("Authorization token is missing.")

    # Remove 'Bearer ' prefix if passed directly
    if id_token.startswith("Bearer "):
        id_token = id_token.split("Bearer ")[1].strip()

    settings = get_settings()

    # Development / Mock fallback logic
    if settings.is_development and (id_token.startswith("dev-token-") or id_token.startswith("mock-token-")):
        token_parts = id_token.split("-")
        uid = "-".join(token_parts[2:]) if len(token_parts) > 2 else "dev_user_123"
        return {
            "uid": uid,
            "email": f"{uid}@edusense.ai",
            "name": f"Dev User {uid}",
            "email_verified": True,
            "is_dev": True
        }

    # Live Firebase Admin SDK verification
    initialized = initialize_firebase()
    if initialized:
        try:
            from firebase_admin import auth
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as exc:
            logger.error(f"Firebase token verification failed: {exc}")
            raise UnauthorizedException(f"Invalid or expired authentication token: {exc}")
    else:
        # Development fallback if SDK not initialized with real credentials
        if settings.is_development:
            return {
                "uid": f"dev_{id_token[:16]}",
                "email": "dev@edusense.ai",
                "name": "Dev User",
                "email_verified": True,
                "is_dev": True
            }
        raise UnauthorizedException("Authentication service is unavailable.")
