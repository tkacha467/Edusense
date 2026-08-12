"""Audit models."""
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, GUID

class AuditLog(BaseModel):
    """Audit log model for tracking system actions."""
    __tablename__ = 'audit_logs'

    user_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(GUID(), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        """String representation."""
        return f"<AuditLog(id={self.id}, action='{self.action}', resource_type='{self.resource_type}')>"
