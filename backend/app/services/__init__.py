"""
Service Layer initialization module.

This module exposes all service classes and provides convenience factory functions
to instantiate them, ensuring a clean and consistent interface for controllers/routers.
"""
from typing import Any

from .user import UserService
from .student import StudentService
from .faculty import FacultyService
from .learning import SubjectService, TopicService, SkillService
from .assessment import AssessmentService
from .knowledge import KnowledgeDecayService
from .recommendation import RecommendationService
from .notification import NotificationService
from .analytics import AnalyticsService
from .audit import AuditService

# Service Factories
def get_user_service() -> UserService:
    """Factory for UserService."""
    return UserService()

def get_student_service() -> StudentService:
    """Factory for StudentService."""
    return StudentService()

def get_faculty_service() -> FacultyService:
    """Factory for FacultyService."""
    return FacultyService()

def get_subject_service() -> SubjectService:
    """Factory for SubjectService."""
    return SubjectService()

def get_topic_service() -> TopicService:
    """Factory for TopicService."""
    return TopicService()

def get_skill_service() -> SkillService:
    """Factory for SkillService."""
    return SkillService()

def get_assessment_service() -> AssessmentService:
    """Factory for AssessmentService."""
    return AssessmentService()

def get_knowledge_decay_service() -> KnowledgeDecayService:
    """Factory for KnowledgeDecayService."""
    return KnowledgeDecayService()

def get_recommendation_service() -> RecommendationService:
    """Factory for RecommendationService."""
    return RecommendationService()

def get_notification_service() -> NotificationService:
    """Factory for NotificationService."""
    return NotificationService()

def get_analytics_service() -> AnalyticsService:
    """Factory for AnalyticsService."""
    return AnalyticsService()

def get_audit_service() -> AuditService:
    """Factory for AuditService."""
    return AuditService()

__all__ = [
    "UserService",
    "StudentService",
    "FacultyService",
    "SubjectService",
    "TopicService",
    "SkillService",
    "AssessmentService",
    "KnowledgeDecayService",
    "RecommendationService",
    "NotificationService",
    "AnalyticsService",
    "AuditService",
    "get_user_service",
    "get_student_service",
    "get_faculty_service",
    "get_subject_service",
    "get_topic_service",
    "get_skill_service",
    "get_assessment_service",
    "get_knowledge_decay_service",
    "get_recommendation_service",
    "get_notification_service",
    "get_analytics_service",
    "get_audit_service",
]
