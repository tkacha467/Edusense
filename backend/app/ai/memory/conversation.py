"""Conversation Memory Service for building student context."""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models import StudentProfile, KnowledgeProfile
from app.repositories import KnowledgeProfileRepository, LearningPreferenceRepository


class ConversationMemoryService:
    """Manages student learning context memory for RAG chat prompts."""

    def __init__(self) -> None:
        self.kp_repo = KnowledgeProfileRepository()
        self.pref_repo = LearningPreferenceRepository()
        self.history: List[Dict[str, str]] = []

    def build_student_context(self, db: Session, student_profile: StudentProfile) -> str:
        """
        Builds a comprehensive student context string summarizing institution,
        learning preferences, weak skills, and recent predictions.
        """
        pref = self.pref_repo.get_by_student(db, student_id=student_profile.id)
        profiles = self.kp_repo.get_by_student(db, student_id=student_profile.id)

        weak_skills = [
            p.skill.name if getattr(p, 'skill', None) else p.skill_id
            for p in profiles if (p.forget_probability or 0.0) >= 0.50
        ]

        context_str = (
            f"Student: {student_profile.user.display_name if getattr(student_profile, 'user', None) else 'Student'}\n"
            f"Institution: {student_profile.institution or 'N/A'}, Department: {student_profile.department or 'N/A'}\n"
            f"Preferred Difficulty: {pref.preferred_difficulty if pref else 'intermediate'}\n"
            f"At-Risk / Weak Skills: {', '.join(weak_skills) if weak_skills else 'None'}"
        )
        return context_str

    def add_message(self, role: str, message: str) -> None:
        """Stores conversation turn."""
        self.history.append({"role": role, "content": message})

    def get_recent_history(self, limit: int = 6) -> List[Dict[str, str]]:
        """Returns recent conversation history turns."""
        return self.history[-limit:]
