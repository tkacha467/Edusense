"""User models."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, Text, Enum as SAEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, SoftDeleteMixin
from app.core.enums import UserRole, UserStatus

class User(BaseModel, SoftDeleteMixin):
    """User model representing a system user."""
    __tablename__ = 'users'

    firebase_uid: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False, index=True)
    status: Mapped[UserStatus] = mapped_column(SAEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE, index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    student_profile: Mapped[Optional["StudentProfile"]] = relationship(
        "StudentProfile", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )
    faculty_profile: Mapped[Optional["FacultyProfile"]] = relationship(
        "FacultyProfile", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user"
    )

    def __repr__(self) -> str:
        """String representation of the User."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
