"""Database engine and table management."""
from typing import Any

from sqlalchemy import Engine, create_engine

from app.config import get_settings
from app.database.base import Base


def get_engine(settings: Any = None) -> Engine:
    """Create and configure database engine."""
    if settings is None:
        settings = get_settings()

    kwargs: dict[str, Any] = {}

    if settings.is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_size"] = 10
        kwargs["max_overflow"] = 20

    if settings.DEBUG:
        kwargs["echo"] = True

    return create_engine(settings.DATABASE_URL, **kwargs)


def create_all_tables(engine: Engine) -> None:
    """Create all database tables."""
    Base.metadata.create_all(engine)


def drop_all_tables(engine: Engine) -> None:
    """Drop all database tables."""
    Base.metadata.drop_all(engine)
