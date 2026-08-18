from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel as PydanticBase, Field, ConfigDict
from app.schemas.base import BaseResponse
from app.core.enums import AssessmentDifficulty, GenerationMethod, AssessmentStatus, QuestionType, QuestionDifficulty, ConfidenceLevel

class QuestionOptionCreate(PydanticBase):
    """Schema for creating a question option."""
    question_id: str
    option_label: str = Field(..., max_length=5)
    option_text: str
    is_correct: bool = False
    order_index: int = 0

class QuestionOptionPublic(PydanticBase):
    """Public schema for a question option, excluding the correct answer."""
    id: str
    option_label: str
    option_text: str
    order_index: int
    
    model_config = ConfigDict(from_attributes=True)

class QuestionOptionResponse(BaseResponse):
    """Full response schema for a question option."""
    question_id: str
    option_label: str
    option_text: str
    is_correct: bool
    order_index: int

class QuestionCreate(PydanticBase):
    """Schema for creating a question."""
    assessment_session_id: str
    topic_id: Optional[str] = None
    skill_id: Optional[str] = None
    question_text: str
    question_type: QuestionType = QuestionType.MCQ
    difficulty_level: QuestionDifficulty
    marks: float = 1.0
    correct_answer: str
    explanation: Optional[str] = None
    hint: Optional[str] = None
    order_index: int = 0
    ai_model_used: Optional[str] = None
    ai_generation_params: Optional[Union[dict, str]] = None

class QuestionResponse(BaseResponse):
    """Response schema for a question."""
    assessment_session_id: str
    topic_id: Optional[str]
    skill_id: Optional[str]
    question_text: str
    question_type: QuestionType
    difficulty_level: QuestionDifficulty
    marks: float
    correct_answer: str
    explanation: Optional[str]
    hint: Optional[str]
    order_index: int
    ai_model_used: Optional[str]
    ai_generation_params: Optional[Union[dict, str]]
    options: List[QuestionOptionResponse] = []

class AssessmentSessionCreate(PydanticBase):
    """Schema for creating an assessment session."""
    student_id: Optional[str] = None
    subject_id: str
    topic_id: Optional[str] = None
    title: str = Field(..., max_length=255)
    difficulty_level: AssessmentDifficulty
    total_questions: int = Field(..., gt=0)
    time_limit_seconds: Optional[int] = Field(None, gt=0)
    generation_method: GenerationMethod = GenerationMethod.AI

class AdaptiveStartInput(PydanticBase):
    subject_id: str
    total_questions: int = 5
    title: str = "Adaptive AI Assessment"

class SubmitSingleAnswerInput(PydanticBase):
    question_id: str
    selected_option_id: str
    time_taken_seconds: int = 15

class AssessmentSessionUpdate(PydanticBase):
    """Schema for updating an assessment session."""
    status: Optional[AssessmentStatus] = None
    scored_marks: Optional[float] = None
    percentage: Optional[float] = None
    time_taken_seconds: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class AssessmentSessionResponse(BaseResponse):
    """Response schema for an assessment session."""
    student_id: str
    subject_id: str
    topic_id: Optional[str]
    title: str
    difficulty_level: AssessmentDifficulty
    total_questions: int
    time_limit_seconds: Optional[int]
    generation_method: GenerationMethod
    status: AssessmentStatus
    scored_marks: Optional[float]
    percentage: Optional[float]
    time_taken_seconds: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    questions: List[QuestionResponse] = []

class StudentResponseCreate(PydanticBase):
    """Schema for submitting a single answer."""
    assessment_session_id: str
    question_id: str
    student_id: str
    selected_option_id: Optional[str] = None
    answer_text: Optional[str] = None
    is_correct: bool
    marks_awarded: float = 0.0
    time_taken_seconds: Optional[int] = None
    confidence_level: Optional[ConfidenceLevel] = None

class StudentResponseResponse(BaseResponse):
    """Response schema for a submitted answer."""
    assessment_session_id: str
    question_id: str
    student_id: str
    selected_option_id: Optional[str]
    answer_text: Optional[str]
    is_correct: bool
    marks_awarded: float
    time_taken_seconds: Optional[int]
    confidence_level: Optional[ConfidenceLevel]
    answered_at: datetime

class AnswerSubmission(PydanticBase):
    """Schema for submitting a single question answer in a batch."""
    question_id: str
    selected_option_id: Optional[str] = None
    answer_text: Optional[str] = None
    time_taken_seconds: Optional[int] = None
    confidence_level: Optional[ConfidenceLevel] = None

class AssessmentSubmission(PydanticBase):
    """Schema for submitting an entire assessment."""
    responses: List[AnswerSubmission]

class AssessmentResult(PydanticBase):
    """Schema for summarizing assessment result."""
    assessment_session_id: str
    total_questions: int
    correct_answers: int
    scored_marks: float
    total_marks: float
    percentage: float
    time_taken_seconds: int
