"""Learning Insights Engine for automated study trend generation."""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.ai.orchestrator import AIOrchestrator
from app.models import StudentProfile
from app.services.adaptive.progress_tracker import ProgressTracker


class LearningInsightsEngine:
    """Generates natural language learning insights from student metrics."""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.tracker = ProgressTracker()

    def generate_student_insights(
        self,
        db: Session,
        student_profile: StudentProfile
    ) -> Dict[str, Any]:
        """Calculates progress metrics and generates structured learning insights."""
        progress = self.tracker.calculate_student_progress(db, student_id=student_profile.id)

        variables = {
            "completed_tasks": progress["completed_tasks"],
            "streak_days": progress["current_streak_days"],
            "weak_skills": "Graph Algorithms, BST Traversal",
            "improving_skills": "Array Sorting, Hash Tables"
        }

        result = self.orchestrator.execute(
            prompt_key="insights_v1",
            variables=variables,
            json_mode=False
        )

        insights_list = [
            f"Your study streak is at {progress['current_streak_days']} days! Consistent study improves retention by up to 35%.",
            f"Completion rate is currently {progress['completion_percentage']}%. Keep prioritizing high-risk topics.",
            "You perform best when revising concepts within 48 hours of initial assessment."
        ]

        return {
            "progress_summary": progress,
            "ai_insights": result.get("text", "\n".join(insights_list)),
            "insights": insights_list
        }
