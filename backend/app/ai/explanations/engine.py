"""Explanation Engine for generating grounded concept explanations and analogies."""
from typing import Dict, Any, Optional
from app.ai.orchestrator import AIOrchestrator
from app.ai.retriever.search import Retriever


class ExplanationEngine:
    """Generates grounded explanations, real-world analogies, and step-by-step examples."""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.retriever = Retriever()

    def explain_concept(
        self,
        concept_name: str,
        subject_name: str = "Computer Science",
        difficulty: str = "intermediate"
    ) -> Dict[str, Any]:
        """Retrieves grounded documents and generates a structured concept explanation."""
        context = self.retriever.retrieve_context(concept_name, top_k=3)

        variables = {
            "concept_name": concept_name,
            "subject_name": subject_name,
            "difficulty": difficulty,
            "context": context
        }

        result = self.orchestrator.execute(
            prompt_key="explanations_v1",
            variables=variables,
            json_mode=False
        )

        return {
            "concept_name": concept_name,
            "subject_name": subject_name,
            "difficulty": difficulty,
            "explanation": result.get("text", f"Grounded explanation for {concept_name}."),
            "retrieved_context": context
        }
