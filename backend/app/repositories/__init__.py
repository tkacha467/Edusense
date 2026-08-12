"""Repository package initialization."""

from .base import BaseRepository
from .user import UserRepository
from .student import StudentProfileRepository
from .faculty import FacultyProfileRepository
from .learning import (
    SubjectRepository,
    TopicRepository,
    SkillRepository,
    TopicSkillRepository,
    StudentSubjectRepository,
    FacultySubjectRepository,
    StudentSkillRepository,
    LearningPreferenceRepository,
)
from .assessment import (
    AssessmentSessionRepository,
    QuestionRepository,
    QuestionOptionRepository,
    StudentResponseRepository,
)
from .knowledge import KnowledgeProfileRepository, PredictionHistoryRepository
from .recommendation import StudyPlanRepository, StudyTaskRepository
from .notification import NotificationRepository
from .analytics import StudentActivityRepository
from .audit import AuditLogRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "StudentProfileRepository",
    "FacultyProfileRepository",
    "SubjectRepository",
    "TopicRepository",
    "SkillRepository",
    "TopicSkillRepository",
    "StudentSubjectRepository",
    "FacultySubjectRepository",
    "StudentSkillRepository",
    "LearningPreferenceRepository",
    "AssessmentSessionRepository",
    "QuestionRepository",
    "QuestionOptionRepository",
    "StudentResponseRepository",
    "KnowledgeProfileRepository",
    "PredictionHistoryRepository",
    "StudyPlanRepository",
    "StudyTaskRepository",
    "NotificationRepository",
    "StudentActivityRepository",
    "AuditLogRepository",
]
