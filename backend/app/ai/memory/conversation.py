"""Conversation Memory Service for building student context."""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models import StudentProfile, KnowledgeProfile
from app.repositories import KnowledgeProfileRepository, LearningPreferenceRepository

_chat_histories: Dict[str, List[Dict[str, str]]] = {}

class ConversationMemoryService:
    """Manages student learning context memory for RAG chat prompts."""

    def __init__(self, student_id: Optional[str] = None) -> None:
        self.kp_repo = KnowledgeProfileRepository()
        self.pref_repo = LearningPreferenceRepository()
        self.student_id = student_id or "default"
        if self.student_id not in _chat_histories:
            _chat_histories[self.student_id] = []

    @property
    def history(self) -> List[Dict[str, str]]:
        return _chat_histories[self.student_id]

    @history.setter
    def history(self, value: List[Dict[str, str]]) -> None:
        _chat_histories[self.student_id] = value

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
        """Stores conversation turn and limits history to the last 20 messages."""
        self.history.append({"role": role, "content": message})
        if len(self.history) > 20:
            self.history = self.history[-20:]

    def get_recent_history(self, limit: int = 6) -> List[Dict[str, str]]:
        """Returns recent conversation history turns."""
        return self.history[-limit:]
