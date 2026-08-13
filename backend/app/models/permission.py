"""Permission models for RBAC."""
from typing import Optional

from sqlalchemy import String, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, GUID
from app.core.enums import UserRole

class Permission(BaseModel):
    """Permission model defining distinct API capabilities."""
    __tablename__ = 'permissions'

    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Permission(id={self.id}, code='{self.code}')>"


class RolePermission(BaseModel):
    """Association table mapping roles to permissions."""
    __tablename__ = 'role_permissions'

    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False, index=True)
    permission_id: Mapped[str] = mapped_column(GUID(), ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False, index=True)

    permission: Mapped["Permission"] = relationship("Permission")

    __table_args__ = (
        Index('ix_role_permissions_role_perm', 'role', 'permission_id', unique=True),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<RolePermission(role='{self.role}', permission_id={self.permission_id})>"
