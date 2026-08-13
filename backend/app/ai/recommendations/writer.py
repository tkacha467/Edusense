"""AI Recommendation Writer for enhancing deterministic decision text."""
from typing import Dict, Any, Optional
from app.ai.orchestrator import AIOrchestrator
from app.services.adaptive.decision_engine import RecommendationDecision


class AIRecommendationWriter:
    """Enhances deterministic RecommendationDecision DTOs with encouraging AI language."""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()

    async def enhance_recommendation_text(
        self,
        decision: RecommendationDecision
    ) -> Dict[str, Any]:
        """Translates deterministic decision parameters into motivating natural language."""
        variables = {
            "skill_name": decision.skill_name,
            "revision_type": decision.revision_type,
            "priority": decision.priority.value if hasattr(decision.priority, 'value') else str(decision.priority),
            "forget_prob": int(decision.forget_probability * 100)
        }

        result = await self.orchestrator.execute(
            prompt_key="recommendations_v1",
            variables=variables,
            json_mode=False
        )

        enhanced_text = result.get("text", f"We recommend revising {decision.skill_name} today to strengthen your retention score.")

        return {
            "decision": decision.__dict__,
            "enhanced_text": enhanced_text
        }
