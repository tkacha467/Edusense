"""User repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from app.repositories.base import BaseRepository
from app.models import User
from app.core.enums import UserRole

class UserRepository(BaseRepository[User]):
    """Repository for User model."""
    
    def __init__(self) -> None:
        """Initialize with User model."""
        super().__init__(User)

    def get_by_firebase_uid(self, db: Session, firebase_uid: str) -> User | None:
        """Get user by Firebase UID."""
        stmt = select(User).where(User.firebase_uid == firebase_uid)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, db: Session, email: str) -> User | None:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalar_one_or_none()

    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """Get active users (not deleted)."""
        stmt = select(User).where(User.deleted_at.is_(None)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())



    def update_last_login(self, db: Session, user_id: str) -> User | None:
        """Update last login timestamp."""
        user = self.get_by_id(db, user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            db.flush()
        return user

    def deactivate(self, db: Session, user_id: str) -> User | None:
        """Deactivate user (soft delete)."""
        return self.soft_delete(db, user_id)
