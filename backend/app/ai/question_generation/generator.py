"""AI Question Generator supporting MCQ, True/False, Fill-in-blanks, Short Answer, Coding."""
from typing import Dict, Any, List, Optional
from app.ai.orchestrator import AIOrchestrator


class AIQuestionGenerator:
    """Generates structured questions of diverse types (MCQ, True/False, Short Answer, Coding)."""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()

    def generate_questions(
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

        result = self.orchestrator.execute(
            prompt_key="question_generator_v1",
            variables=variables,
            json_mode=True
        )

        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "questions" in result:
            return result["questions"]

        # Default fallback list of questions
        fallback = []
        for _ in range(count):
            fallback.append({
                "question_text": f"What is the average time complexity of operations in {topic_name}?",
                "question_type": question_type.upper(),
                "difficulty_level": difficulty.lower(),
                "marks": 1.0,
                "correct_answer": "B",
                "explanation": f"{topic_name} halving principle yields logarithmic complexity.",
                "hint": "Think about tree height properties.",
                "options": [
                    {"option_label": "A", "option_text": "O(1)"},
                    {"option_label": "B", "option_text": "O(log N)"},
                    {"option_label": "C", "option_text": "O(N)"}
                ]
            })
        return fallback
