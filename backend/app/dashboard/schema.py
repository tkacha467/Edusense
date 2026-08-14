"""Pydantic schemas for Faculty Dashboard module."""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProfileSummaryResponse(BaseModel):
    """Faculty profile summary response schema."""
    full_name: str
    email: str
    institution: Optional[str] = "EduSense University"
    department: Optional[str] = "Computer Science"
    designation: Optional[str] = "Faculty Member"
    role: str = "faculty"

    model_config = ConfigDict(from_attributes=True)


class DashboardSummaryResponse(BaseModel):
    """Summary metrics response schema."""
    total_students: int = 0
    total_skills: int = 0
    high_risk_students: int = 0
    pending_revisions: int = 0
    predictions_generated: int = 0
    active_courses: int = 0

    model_config = ConfigDict(from_attributes=True)


class KnowledgeHealthPoint(BaseModel):
    """Data point for knowledge health time series chart."""
    date_label: str
    avg_retention: float = 0.0
    avg_forget_prob: float = 0.0
    predictions_count: int = 0


class KnowledgeHealthResponse(BaseModel):
    """Knowledge health overview response schema."""
    points: List[KnowledgeHealthPoint] = Field(default_factory=list)


class RevisionQueueItem(BaseModel):
    """Single item in the student revision queue."""
    id: str
    student_id: str
    student_name: str
    skill_id: str
    skill_name: str
    forget_probability: float
    revision_priority: str  # HIGH, MEDIUM, LOW
    recommended_revision_date: Optional[str] = None
    status: str  # PENDING, IN_PROGRESS, COMPLETED


class RevisionQueueResponse(BaseModel):
    """Paginated revision queue response schema."""
    items: List[RevisionQueueItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    size: int = 10
    pages: int = 0


class WeakSkillItem(BaseModel):
    """Weak skill analytics item."""
    skill_id: str
    skill_name: str
    avg_mastery: float
    avg_forget_probability: float
    students_affected: int


class RecentActivityItem(BaseModel):
    """Recent learning activity log item."""
    id: str
    student_name: str
    activity_type: str
    description: str
    timestamp: str
