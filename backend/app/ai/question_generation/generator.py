"""AI Question Generator supporting MCQ, True/False, Fill-in-blanks, Short Answer, Coding."""
from typing import Dict, Any, List, Optional
from app.ai.orchestrator import AIOrchestrator


class AIQuestionGenerator:
    """Generates structured questions of diverse types (MCQ, True/False, Short Answer, Coding)."""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()

    async def generate_questions(
        self,
        topic_name: str,
        subject_name: str = "Computer Science",
        question_type: str = "mcq",
        difficulty: str = "intermediate",
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generates validated question items."""
        variables = {
            "topic_name": topic_name,
            "subject_name": subject_name,
            "question_type": question_type,
            "difficulty": difficulty,
            "count": count
        }

        result = await self.orchestrator.execute(
            prompt_key="question_generator_v1",
            variables=variables,
            json_mode=True
        )

        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "questions" in result:
            return result["questions"]

        # 1. Try Ollama local LLM for dynamic RAG question generation if available
        try:
            from app.services.ollama_service import generate_questions_with_ollama
            ollama_questions = generate_questions_with_ollama(
                subject_name=subject_name,
                topic_name=topic_name,
                difficulty=difficulty,
                count=count
            )
            if ollama_questions and len(ollama_questions) > 0:
                return ollama_questions
        except Exception:
            pass

        # 2. Hybrid Fallback: Use domain-specific questions dataset grounded in topic and subject
        from app.ai.question_generation.domain_questions import get_domain_questions
        return get_domain_questions(subject_name=subject_name, topic_name=topic_name, count=count)
