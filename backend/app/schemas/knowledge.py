from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBase, Field
from app.schemas.base import BaseResponse
from app.core.enums import PredictionTrigger

class KnowledgeProfileCreate(PydanticBase):
    """Schema for creating a knowledge profile."""
    student_id: str
    skill_id: str

class KnowledgeProfileUpdate(PydanticBase):
    """Schema for updating a knowledge profile."""
    interaction_order: Optional[int] = None
    past_attempts: Optional[int] = None
    past_correct: Optional[int] = None
    past_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    rolling_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    mastered: Optional[bool] = None
    forget_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    retention_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    last_predicted_at: Optional[datetime] = None
    last_interaction_at: Optional[datetime] = None

class KnowledgeProfileResponse(BaseResponse):
    """Response schema for a knowledge profile."""
    student_id: str
    skill_id: str
    interaction_order: int
    past_attempts: int
    past_correct: int
    past_accuracy: float
    rolling_accuracy: float
    mastered: bool
    forget_probability: Optional[float]
    retention_score: Optional[float]
    confidence_score: Optional[float]
    last_predicted_at: Optional[datetime]
    last_interaction_at: Optional[datetime]

class MLFeatureVector(PydanticBase):
    """Schema representing features sent to the ML model."""
    interaction_order: int
    past_attempts: int
    past_correct: int
    past_accuracy: float = Field(..., ge=0.0, le=1.0)
    rolling_accuracy: float = Field(..., ge=0.0, le=1.0)
    mastered: bool

class PredictionResult(PydanticBase):
    """Schema representing prediction result from the ML model."""
    forget_probability: float = Field(..., ge=0.0, le=1.0)
    retention_score: float = Field(..., ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    model_version: str

class PredictionHistoryCreate(PydanticBase):
    """Schema for recording a prediction history entry."""
    knowledge_profile_id: str
    student_id: str
    skill_id: str
    interaction_order: int
    past_attempts: int
    past_correct: int
    past_accuracy: float
    rolling_accuracy: float
    mastered: bool
    forget_probability: float
    retention_score: float
    confidence_score: Optional[float] = None
    model_version: str
    triggered_by: PredictionTrigger

class PredictionHistoryResponse(BaseResponse):
    """Response schema for a prediction history entry."""
    knowledge_profile_id: str
    student_id: str
    skill_id: str
    interaction_order: int
    past_attempts: int
    past_correct: int
    past_accuracy: float
    rolling_accuracy: float
    mastered: bool
    forget_probability: float
    retention_score: float
    confidence_score: Optional[float]
    model_version: str
    triggered_by: PredictionTrigger
    predicted_at: datetime
