"""Flashcard Generator service for spaced repetition study."""
from typing import Dict, Any, List, Optional
from app.ai.orchestrator import AIOrchestrator


class FlashcardGenerator:
    """Generates adaptive flashcards for spaced repetition based on skill and difficulty."""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()

    async def generate_flashcards(
        self,
        skill_name: str,
        difficulty: str = "intermediate",
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generates structured adaptive flashcard items."""
        variables = {
            "skill_name": skill_name,
            "difficulty": difficulty,
            "count": count
        }

        result = await self.orchestrator.execute(
            prompt_key="flashcards_v1",
            variables=variables,
            json_mode=True
        )

        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "cards" in result:
            return result["cards"]

        # Default structured fallback items
        return [
            {
                "question": f"What is the key principle behind {skill_name}?",
                "answer": f"Core mechanics and algorithmic properties of {skill_name}.",
                "difficulty": difficulty,
                "explanation": f"Understanding {skill_name} requires mastering its definition and edge cases.",
                "review_priority": "HIGH"
            }
        ]
