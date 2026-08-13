"""Application enums."""
from enum import Enum


class UserStatus(str, Enum):
    """User account status."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class FacultyRequestStatus(str, Enum):
    """Faculty request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class UserRole(str, Enum):
    """User roles enum."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    DEPARTMENT_ADMIN = "department_admin"
    FACULTY = "faculty"
    STUDENT = "student"
    RESEARCHER = "researcher"
    PARENT = "parent"
    GUEST = "guest"


class DifficultyLevel(str, Enum):
    """General difficulty levels enum."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AssessmentDifficulty(str, Enum):
    """Assessment difficulty levels enum."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ADAPTIVE = "adaptive"


class AssessmentStatus(str, Enum):
    """Assessment status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    EXPIRED = "expired"


class QuestionType(str, Enum):
    """Question type enum."""
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class QuestionDifficulty(str, Enum):
    """Question difficulty enum."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GenerationMethod(str, Enum):
    """Generation method enum."""
    AI = "ai"
    MANUAL = "manual"
    BANK = "bank"


class LearningStyle(str, Enum):
    """Learning style enum."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    READING = "reading"
    KINESTHETIC = "kinesthetic"


class ConfidenceLevel(str, Enum):
    """Confidence level enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StudyPlanType(str, Enum):
    """Study plan type enum."""
    DAILY = "daily"
    WEEKLY = "weekly"
    REVISION = "revision"
    CUSTOM = "custom"


class StudyPlanStatus(str, Enum):
    """Study plan status enum."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskType(str, Enum):
    """Task type enum."""
    REVIEW = "review"
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    READING = "reading"
    REVISION = "revision"


class TaskPriority(str, Enum):
    """Task priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class NotificationType(str, Enum):
    """Notification type enum."""
    PREDICTION_ALERT = "prediction_alert"
    STUDY_REMINDER = "study_reminder"
    ASSESSMENT_READY = "assessment_ready"
    ACHIEVEMENT = "achievement"
    SYSTEM = "system"
    FACULTY_INTERVENTION = "faculty_intervention"


class NotificationPriority(str, Enum):
    """Notification priority enum."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ActivityType(str, Enum):
    """Activity type enum."""
    LOGIN = "login"
    ASSESSMENT_STARTED = "assessment_started"
    ASSESSMENT_COMPLETED = "assessment_completed"
    STUDY_PLAN_STARTED = "study_plan_started"
    TASK_COMPLETED = "task_completed"
    PREDICTION_VIEWED = "prediction_viewed"
    SUBJECT_ENROLLED = "subject_enrolled"
    SKILL_PRACTICED = "skill_practiced"


class PredictionTrigger(str, Enum):
    """Prediction trigger enum."""
    ASSESSMENT_COMPLETE = "assessment_complete"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    SYSTEM = "system"
