"""Hint Generator for progressive assessment hints."""
from typing import Dict, Any, Optional
from app.ai.orchestrator import AIOrchestrator


class HintGenerator:
    """Generates guiding hints for assessment questions without spoiling answers."""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()

    async def generate_hint(
        self,
        question_text: str,
        skill_name: str = "Target Skill"
    ) -> Dict[str, Any]:
        """Generates a progressive hint for a student."""
        variables = {
            "question_text": question_text,
            "skill_name": skill_name
        }

        result = await self.orchestrator.execute(
            prompt_key="hints_v1",
            variables=variables,
            json_mode=False
        )

        return {
            "question_text": question_text,
            "skill_name": skill_name,
            "hint": result.get("text", f"Consider the fundamental definition of {skill_name} and break down the problem step by step.")
        }
