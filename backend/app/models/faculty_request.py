"""Faculty Request model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey, Integer, Text, Enum as SAEnum, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, GUID
from app.core.enums import FacultyRequestStatus

class FacultyRequest(BaseModel):
    """Faculty request model for tracking approval workflows."""
    __tablename__ = 'faculty_requests'

    user_id: Mapped[str] = mapped_column(GUID(), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    request_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[FacultyRequestStatus] = mapped_column(SAEnum(FacultyRequestStatus), nullable=False, default=FacultyRequestStatus.PENDING, index=True)
    
    institution_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index('ix_faculty_requests_user_status', 'user_id', 'status'),
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self) -> str:
        """String representation."""
        return f"<FacultyRequest(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
