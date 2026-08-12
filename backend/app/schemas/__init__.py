"""
Schema definitions for the application.
"""

from .base import BaseResponse, PaginatedResponse, MessageResponse
from .user import UserCreate, UserUpdate, UserPublic, UserResponse
from .student import StudentProfileCreate, StudentProfileUpdate, StudentProfileResponse, StudentDashboardResponse
from .faculty import FacultyProfileCreate, FacultyProfileUpdate, FacultyProfileResponse
from .learning import (
    SubjectCreate, SubjectUpdate, SubjectResponse,
    TopicCreate, TopicUpdate, TopicResponse,
    SkillCreate, SkillUpdate, SkillResponse,
    TopicSkillCreate, TopicSkillResponse,
    StudentSubjectCreate, StudentSubjectResponse,
    FacultySubjectCreate, FacultySubjectResponse,
    StudentSkillCreate, StudentSkillUpdate, StudentSkillResponse,
    LearningPreferenceCreate, LearningPreferenceUpdate, LearningPreferenceResponse
)
from .assessment import (
    QuestionOptionCreate, QuestionOptionPublic, QuestionOptionResponse,
    QuestionCreate, QuestionResponse,
    AssessmentSessionCreate, AssessmentSessionUpdate, AssessmentSessionResponse,
    StudentResponseCreate, StudentResponseResponse,
    AnswerSubmission, AssessmentSubmission, AssessmentResult
)
from .knowledge import (
    KnowledgeProfileCreate, KnowledgeProfileUpdate, KnowledgeProfileResponse,
    MLFeatureVector, PredictionResult,
    PredictionHistoryCreate, PredictionHistoryResponse
)
from .recommendation import (
    StudyTaskCreate, StudyTaskUpdate, StudyTaskResponse,
    StudyPlanCreate, StudyPlanUpdate, StudyPlanResponse
)
from .notification import NotificationCreate, NotificationUpdate, NotificationResponse, NotificationBatchRead
from .analytics import StudentActivityCreate, StudentActivityResponse, ActivitySummary
from .audit import AuditLogCreate, AuditLogResponse, AuditLogFilter

__all__ = [
    "BaseResponse", "PaginatedResponse", "MessageResponse",
    "UserCreate", "UserUpdate", "UserPublic", "UserResponse",
    "StudentProfileCreate", "StudentProfileUpdate", "StudentProfileResponse", "StudentDashboardResponse",
    "FacultyProfileCreate", "FacultyProfileUpdate", "FacultyProfileResponse",
    "SubjectCreate", "SubjectUpdate", "SubjectResponse",
    "TopicCreate", "TopicUpdate", "TopicResponse",
    "SkillCreate", "SkillUpdate", "SkillResponse",
    "TopicSkillCreate", "TopicSkillResponse",
    "StudentSubjectCreate", "StudentSubjectResponse",
    "FacultySubjectCreate", "FacultySubjectResponse",
    "StudentSkillCreate", "StudentSkillUpdate", "StudentSkillResponse",
    "LearningPreferenceCreate", "LearningPreferenceUpdate", "LearningPreferenceResponse",
    "QuestionOptionCreate", "QuestionOptionPublic", "QuestionOptionResponse",
    "QuestionCreate", "QuestionResponse",
    "AssessmentSessionCreate", "AssessmentSessionUpdate", "AssessmentSessionResponse",
    "StudentResponseCreate", "StudentResponseResponse",
    "AnswerSubmission", "AssessmentSubmission", "AssessmentResult",
    "KnowledgeProfileCreate", "KnowledgeProfileUpdate", "KnowledgeProfileResponse",
    "MLFeatureVector", "PredictionResult",
    "PredictionHistoryCreate", "PredictionHistoryResponse",
    "StudyTaskCreate", "StudyTaskUpdate", "StudyTaskResponse",
    "StudyPlanCreate", "StudyPlanUpdate", "StudyPlanResponse",
    "NotificationCreate", "NotificationUpdate", "NotificationResponse", "NotificationBatchRead",
    "StudentActivityCreate", "StudentActivityResponse", "ActivitySummary",
    "AuditLogCreate", "AuditLogResponse", "AuditLogFilter"
]
