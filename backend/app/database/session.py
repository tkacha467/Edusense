"""Database session management."""
from typing import Iterator

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.database.database import get_engine

def get_session_factory(engine: Engine) -> sessionmaker:
    """Get a session factory bound to the engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Iterator[Session]:
    """Get a database session generator."""
    settings = get_settings()
    engine = get_engine(settings)
    session_factory = get_session_factory(engine)
    db = session_factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
