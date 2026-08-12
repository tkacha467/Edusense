from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBase, Field
from app.schemas.base import BaseResponse
from app.core.enums import DifficultyLevel, LearningStyle

class SubjectCreate(PydanticBase):
    """Schema for creating a subject."""
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=20)
    description: str
    category: str = Field(..., max_length=100)
    semester: int

class SubjectUpdate(PydanticBase):
    """Schema for updating a subject."""
    name: Optional[str] = Field(None, max_length=200)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    semester: Optional[int] = None

class SubjectResponse(BaseResponse):
    """Response schema for a subject."""
    name: str
    code: str
    description: str
    category: str
    semester: int
    is_active: bool
    topic_count: int = 0

class TopicCreate(PydanticBase):
    """Schema for creating a topic."""
    subject_id: str
    name: str = Field(..., max_length=200)
    description: str
    difficulty_level: DifficultyLevel
    order_index: int = 0

class TopicUpdate(PydanticBase):
    """Schema for updating a topic."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None

class TopicResponse(BaseResponse):
    """Response schema for a topic."""
    subject_id: str
    name: str
    description: str
    difficulty_level: DifficultyLevel
    order_index: int
    is_active: bool
    subject_name: Optional[str] = None

class SkillCreate(PydanticBase):
    """Schema for creating a skill."""
    name: str = Field(..., max_length=200)
    description: str
    category: str = Field(..., max_length=100)

class SkillUpdate(PydanticBase):
    """Schema for updating a skill."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)

class SkillResponse(BaseResponse):
    """Response schema for a skill."""
    name: str
    description: str
    category: str

class TopicSkillCreate(PydanticBase):
    """Schema for creating a topic-skill relation."""
    topic_id: str
    skill_id: str
    relevance_weight: float = Field(1.0, ge=0.0, le=1.0)

class TopicSkillResponse(BaseResponse):
    """Response schema for a topic-skill relation."""
    topic_id: str
    skill_id: str
    relevance_weight: float

class StudentSubjectCreate(PydanticBase):
    """Schema for creating a student-subject relation."""
    student_id: str
    subject_id: str

class StudentSubjectResponse(BaseResponse):
    """Response schema for a student-subject relation."""
    student_id: str
    subject_id: str
    enrolled_at: datetime
    is_active: bool

class FacultySubjectCreate(PydanticBase):
    """Schema for creating a faculty-subject relation."""
    faculty_id: str
    subject_id: str

class FacultySubjectResponse(BaseResponse):
    """Response schema for a faculty-subject relation."""
    faculty_id: str
    subject_id: str
    assigned_at: datetime

class StudentSkillCreate(PydanticBase):
    """Schema for creating a student-skill record."""
    student_id: str
    skill_id: str

class StudentSkillUpdate(PydanticBase):
    """Schema for updating a student-skill record."""
    proficiency_level: Optional[float] = None
    total_attempts: Optional[int] = None
    correct_attempts: Optional[int] = None

class StudentSkillResponse(BaseResponse):
    """Response schema for a student-skill record."""
    student_id: str
    skill_id: str
    proficiency_level: float
    total_attempts: int
    correct_attempts: int
    last_practiced_at: Optional[datetime]

class LearningPreferenceCreate(PydanticBase):
    """Schema for creating a learning preference."""
    student_id: str
    learning_style: Optional[LearningStyle] = None
    weekly_study_hours: float = Field(..., ge=0)
    preferred_difficulty: Optional[DifficultyLevel] = None
    preferred_session_length: int = Field(..., gt=0)
    target_score: float = Field(..., ge=0, le=100)

class LearningPreferenceUpdate(PydanticBase):
    """Schema for updating a learning preference."""
    learning_style: Optional[LearningStyle] = None
    weekly_study_hours: Optional[float] = Field(None, ge=0)
    preferred_difficulty: Optional[DifficultyLevel] = None
    preferred_session_length: Optional[int] = Field(None, gt=0)
    target_score: Optional[float] = Field(None, ge=0, le=100)

class LearningPreferenceResponse(BaseResponse):
    """Response schema for a learning preference."""
    student_id: str
    learning_style: Optional[LearningStyle]
    weekly_study_hours: float
    preferred_difficulty: Optional[DifficultyLevel]
    preferred_session_length: int
    target_score: float
