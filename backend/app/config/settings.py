"""Application configuration settings."""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class."""

    APP_NAME: str = "EduSense AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    SECRET_KEY: str
    DATABASE_URL: str = "sqlite:///./edusense.db"
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-credentials.json"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    ML_MODEL_PATH: str = "../Models/best_model_v2.pkl"
    ML_SCALER_PATH: str = "../Models/scaler_v2.pkl"
    ML_FEATURES_PATH: str = "../Models/selected_features.json"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def is_development(self) -> bool:
        """Check if environment is development."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_sqlite(self) -> bool:
        """Check if database is sqlite."""
        return self.DATABASE_URL.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
