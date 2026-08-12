from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel as PydanticBase, Field
from app.schemas.base import BaseResponse
from app.core.enums import StudyPlanType, StudyPlanStatus, TaskType, TaskPriority, TaskStatus

class StudyTaskCreate(PydanticBase):
    """Schema for creating a study task."""
    study_plan_id: str
    topic_id: Optional[str] = None
    skill_id: Optional[str] = None
    title: str = Field(..., max_length=255)
    task_type: TaskType
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_minutes: Optional[int] = Field(None, gt=0)
    scheduled_date: Optional[datetime] = None
    order_index: int = 0

class StudyTaskUpdate(PydanticBase):
    """Schema for updating a study task."""
    title: Optional[str] = Field(None, max_length=255)
    task_type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    estimated_minutes: Optional[int] = Field(None, gt=0)
    scheduled_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    order_index: Optional[int] = None

class StudyTaskResponse(BaseResponse):
    """Response schema for a study task."""
    study_plan_id: str
    topic_id: Optional[str]
    skill_id: Optional[str]
    title: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    estimated_minutes: Optional[int]
    scheduled_date: Optional[datetime]
    completed_at: Optional[datetime]
    order_index: int

class StudyPlanCreate(PydanticBase):
    """Schema for creating a study plan."""
    student_id: str
    subject_id: Optional[str] = None
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    plan_type: StudyPlanType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    ai_model_used: Optional[str] = None

class StudyPlanUpdate(PydanticBase):
    """Schema for updating a study plan."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[StudyPlanStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class StudyPlanResponse(BaseResponse):
    """Response schema for a study plan."""
    student_id: str
    subject_id: Optional[str]
    title: str
    description: Optional[str]
    plan_type: StudyPlanType
    status: StudyPlanStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    ai_model_used: Optional[str]
    tasks: List[StudyTaskResponse] = []
