"""Models package for EduSense AI."""

from app.models.user import User
from app.models.student import StudentProfile
from app.models.faculty import FacultyProfile
from app.models.learning import (
    Subject, Topic, Skill, TopicSkill, StudentSubject, FacultySubject,
    StudentSkill, LearningPreference
)
from app.models.assessment import (
    AssessmentSession, Question, QuestionOption, StudentResponse
)
from app.models.knowledge import KnowledgeProfile, PredictionHistory
from app.models.recommendation import StudyPlan, StudyTask
from app.models.notification import Notification
from app.models.analytics import StudentActivity
from app.models.audit import AuditLog

__all__ = [
    "User",
    "StudentProfile",
    "FacultyProfile",
    "Subject",
    "Topic",
    "Skill",
    "TopicSkill",
    "StudentSubject",
    "FacultySubject",
    "StudentSkill",
    "LearningPreference",
    "AssessmentSession",
    "Question",
    "QuestionOption",
    "StudentResponse",
    "KnowledgeProfile",
    "PredictionHistory",
    "StudyPlan",
    "StudyTask",
    "Notification",
    "StudentActivity",
    "AuditLog",
]
