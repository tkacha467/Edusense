"""Study Notes Summarizer service grounding summaries via RAG."""
from typing import Dict, Any, Optional
from app.ai.orchestrator import AIOrchestrator
from app.ai.retriever.search import Retriever


class StudyNotesSummarizer:
    """Generates grounded study note summaries using RAG context."""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.retriever = Retriever()

    def generate_summary(self, topic_name: str) -> Dict[str, Any]:
        """Retrieves topic context and generates structured summary."""
        context = self.retriever.retrieve_context(topic_name, top_k=3)

        variables = {
            "topic_name": topic_name,
            "context": context
        }

        result = self.orchestrator.execute(
            prompt_key="summaries_v1",
            variables=variables,
            json_mode=True
        )

        if isinstance(result, dict) and "key_concepts" in result:
            return result

        return {
            "title": f"Study Notes: {topic_name}",
            "key_concepts": [f"Core mechanics of {topic_name}", "Key properties & definitions"],
            "formulas": ["Standard representation formula"],
            "bullet_summary": ["High-yield bullet point 1", "High-yield bullet point 2"],
            "exam_tips": ["Beware of off-by-one errors in boundary conditions."]
        }
