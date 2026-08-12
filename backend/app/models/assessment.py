"""Assessment models."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Float, Text, Boolean, DateTime, ForeignKey, Index, UniqueConstraint, CheckConstraint, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import BaseModel, GUID
from app.core.enums import AssessmentDifficulty, AssessmentStatus, GenerationMethod, QuestionType, QuestionDifficulty, ConfidenceLevel

class AssessmentSession(BaseModel):
    """Assessment session model."""
    __tablename__ = 'assessment_sessions'

    student_id: Mapped[str] = mapped_column(GUID(), ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(GUID(), ForeignKey('subjects.id', ondelete='RESTRICT'), nullable=False, index=True)
    topic_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('topics.id', ondelete='SET NULL'), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty_level: Mapped[AssessmentDifficulty] = mapped_column(SAEnum(AssessmentDifficulty), nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    total_marks: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    scored_marks: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    time_limit_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time_taken_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[AssessmentStatus] = mapped_column(SAEnum(AssessmentStatus), nullable=False, default=AssessmentStatus.PENDING, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    generation_method: Mapped[GenerationMethod] = mapped_column(SAEnum(GenerationMethod), nullable=False, default=GenerationMethod.AI)

    __table_args__ = (
        CheckConstraint('total_questions > 0', name='check_total_questions'),
        CheckConstraint('percentage >= 0 AND percentage <= 100', name='check_percentage'),
        CheckConstraint('time_limit_seconds > 0', name='check_time_limit'),
        Index('ix_assessment_student_subject', 'student_id', 'subject_id'),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="assessment_sessions")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="assessment_sessions")
    topic: Mapped[Optional["Topic"]] = relationship("Topic", back_populates="assessment_sessions")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="assessment_session", cascade="all, delete-orphan")
    responses: Mapped[List["StudentResponse"]] = relationship("StudentResponse", back_populates="assessment_session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<AssessmentSession(id={self.id}, student_id={self.student_id}, status='{self.status}')>"

class Question(BaseModel):
    """Question model."""
    __tablename__ = 'questions'

    assessment_session_id: Mapped[str] = mapped_column(GUID(), ForeignKey('assessment_sessions.id', ondelete='CASCADE'), nullable=False)
    topic_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('topics.id', ondelete='SET NULL'), nullable=True)
    skill_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('skills.id', ondelete='SET NULL'), nullable=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(SAEnum(QuestionType), nullable=False, default=QuestionType.MCQ)
    difficulty_level: Mapped[QuestionDifficulty] = mapped_column(SAEnum(QuestionDifficulty), nullable=False)
    marks: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_generation_params: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assessment_session: Mapped["AssessmentSession"] = relationship("AssessmentSession", back_populates="questions")
    topic: Mapped[Optional["Topic"]] = relationship("Topic", back_populates="questions")
    skill: Mapped[Optional["Skill"]] = relationship("Skill", back_populates="questions")
    options: Mapped[List["QuestionOption"]] = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    responses: Mapped[List["StudentResponse"]] = relationship("StudentResponse", back_populates="question")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Question(id={self.id}, assessment_session_id={self.assessment_session_id})>"

class QuestionOption(BaseModel):
    """Question option model."""
    __tablename__ = 'question_options'

    question_id: Mapped[str] = mapped_column(GUID(), ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    option_label: Mapped[str] = mapped_column(String(5), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('question_id', 'option_label', name='uq_question_option_label'),
    )

    question: Mapped["Question"] = relationship("Question", back_populates="options")
    responses: Mapped[List["StudentResponse"]] = relationship("StudentResponse", back_populates="selected_option")

    def __repr__(self) -> str:
        """String representation."""
        return f"<QuestionOption(id={self.id}, question_id={self.question_id}, label='{self.option_label}')>"

class StudentResponse(BaseModel):
    """Student response model."""
    __tablename__ = 'student_responses'

    assessment_session_id: Mapped[str] = mapped_column(GUID(), ForeignKey('assessment_sessions.id', ondelete='CASCADE'), nullable=False)
    question_id: Mapped[str] = mapped_column(GUID(), ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    student_id: Mapped[str] = mapped_column(GUID(), ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    selected_option_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey('question_options.id', ondelete='SET NULL'), nullable=True)
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    marks_awarded: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    time_taken_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence_level: Mapped[Optional[ConfidenceLevel]] = mapped_column(SAEnum(ConfidenceLevel), nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('assessment_session_id', 'question_id', name='uq_assessment_question_response'),
    )

    assessment_session: Mapped["AssessmentSession"] = relationship("AssessmentSession", back_populates="responses")
    question: Mapped["Question"] = relationship("Question", back_populates="responses")
    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="responses")
    selected_option: Mapped[Optional["QuestionOption"]] = relationship("QuestionOption", back_populates="responses")

    def __repr__(self) -> str:
        """String representation."""
        return f"<StudentResponse(id={self.id}, student_id={self.student_id}, question_id={self.question_id})>"
