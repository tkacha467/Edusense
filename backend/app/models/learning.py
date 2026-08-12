"""Learning models."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Float, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import BaseModel, GUID
from app.core.enums import DifficultyLevel, LearningStyle

class Subject(BaseModel):
    """Subject model."""
    __tablename__ = 'subjects'

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    semester: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    topics: Mapped[List["Topic"]] = relationship("Topic", back_populates="subject")
    student_subjects: Mapped[List["StudentSubject"]] = relationship("StudentSubject", back_populates="subject")
    faculty_subjects: Mapped[List["FacultySubject"]] = relationship("FacultySubject", back_populates="subject")
    assessment_sessions: Mapped[List["AssessmentSession"]] = relationship("AssessmentSession", back_populates="subject")
    study_plans: Mapped[List["StudyPlan"]] = relationship("StudyPlan", back_populates="subject")
    activities: Mapped[List["StudentActivity"]] = relationship("StudentActivity", back_populates="subject")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Subject(id={self.id}, code='{self.code}', name='{self.name}')>"

class Topic(BaseModel):
    """Topic model."""
    __tablename__ = 'topics'

    subject_id: Mapped[str] = mapped_column(GUID(), ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(SAEnum(DifficultyLevel), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint('subject_id', 'name', name='uq_topic_subject_name'),
    )

    subject: Mapped["Subject"] = relationship("Subject", back_populates="topics")
    topic_skills: Mapped[List["TopicSkill"]] = relationship("TopicSkill", back_populates="topic")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="topic")
    assessment_sessions: Mapped[List["AssessmentSession"]] = relationship("AssessmentSession", back_populates="topic")
    study_tasks: Mapped[List["StudyTask"]] = relationship("StudyTask", back_populates="topic")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Topic(id={self.id}, subject_id={self.subject_id}, name='{self.name}')>"

class Skill(BaseModel):
    """Skill model."""
    __tablename__ = 'skills'

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    topic_skills: Mapped[List["TopicSkill"]] = relationship("TopicSkill", back_populates="skill")
    student_skills: Mapped[List["StudentSkill"]] = relationship("StudentSkill", back_populates="skill")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="skill")
    knowledge_profiles: Mapped[List["KnowledgeProfile"]] = relationship("KnowledgeProfile", back_populates="skill")
    study_tasks: Mapped[List["StudyTask"]] = relationship("StudyTask", back_populates="skill")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Skill(id={self.id}, name='{self.name}')>"

class TopicSkill(BaseModel):
    """Topic skill mapping model."""
    __tablename__ = 'topic_skills'

    topic_id: Mapped[str] = mapped_column(GUID(), ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    skill_id: Mapped[str] = mapped_column(GUID(), ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    relevance_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    __table_args__ = (
        UniqueConstraint('topic_id', 'skill_id', name='uq_topic_skill'),
        CheckConstraint('relevance_weight >= 0.0 AND relevance_weight <= 1.0', name='check_relevance_weight'),
    )

    topic: Mapped["Topic"] = relationship("Topic", back_populates="topic_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="topic_skills")

    def __repr__(self) -> str:
        """String representation."""
        return f"<TopicSkill(topic_id={self.topic_id}, skill_id={self.skill_id})>"

class StudentSubject(BaseModel):
    """Student subject enrollment model."""
    __tablename__ = 'student_subjects'

    student_id: Mapped[str] = mapped_column(GUID(), ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    subject_id: Mapped[str] = mapped_column(GUID(), ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint('student_id', 'subject_id', name='uq_student_subject'),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="subjects")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="student_subjects")

    def __repr__(self) -> str:
        """String representation."""
        return f"<StudentSubject(student_id={self.student_id}, subject_id={self.subject_id})>"

class FacultySubject(BaseModel):
    """Faculty subject assignment model."""
    __tablename__ = 'faculty_subjects'

    faculty_id: Mapped[str] = mapped_column(GUID(), ForeignKey('faculty_profiles.id', ondelete='CASCADE'), nullable=False)
    subject_id: Mapped[str] = mapped_column(GUID(), ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('faculty_id', 'subject_id', name='uq_faculty_subject'),
    )

    faculty: Mapped["FacultyProfile"] = relationship("FacultyProfile", back_populates="subjects")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="faculty_subjects")

    def __repr__(self) -> str:
        """String representation."""
        return f"<FacultySubject(faculty_id={self.faculty_id}, subject_id={self.subject_id})>"

class StudentSkill(BaseModel):
    """Student skill proficiency model."""
    __tablename__ = 'student_skills'

    student_id: Mapped[str] = mapped_column(GUID(), ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    skill_id: Mapped[str] = mapped_column(GUID(), ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    proficiency_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_practiced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('student_id', 'skill_id', name='uq_student_skill'),
        CheckConstraint('proficiency_level >= 0.0 AND proficiency_level <= 1.0', name='check_proficiency_level'),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="student_skills")

    def __repr__(self) -> str:
        """String representation."""
        return f"<StudentSkill(student_id={self.student_id}, skill_id={self.skill_id})>"

class LearningPreference(BaseModel):
    """Student learning preference model."""
    __tablename__ = 'learning_preferences'

    student_id: Mapped[str] = mapped_column(GUID(), ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False, unique=True)
    learning_style: Mapped[Optional[LearningStyle]] = mapped_column(SAEnum(LearningStyle), nullable=True)
    weekly_study_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    preferred_difficulty: Mapped[Optional[DifficultyLevel]] = mapped_column(SAEnum(DifficultyLevel), nullable=True)
    preferred_session_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __table_args__ = (
        CheckConstraint('weekly_study_hours >= 0', name='check_weekly_study_hours'),
        CheckConstraint('preferred_session_length > 0', name='check_preferred_session_length'),
        CheckConstraint('target_score >= 0 AND target_score <= 100', name='check_target_score'),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="learning_preference")

    def __repr__(self) -> str:
        """String representation."""
        return f"<LearningPreference(student_id={self.student_id})>"
