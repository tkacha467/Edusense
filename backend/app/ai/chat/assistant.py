"""AI Study Assistant - Grounded academic chat assistant using RAG."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.ai.orchestrator import AIOrchestrator
from app.ai.retriever.search import Retriever
from app.ai.memory.conversation import ConversationMemoryService
from app.models import StudentProfile


class AIStudyAssistant:
    """Grounded AI Study Assistant answering student queries with RAG context."""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.retriever = Retriever()
        self.memory = ConversationMemoryService()

    def answer_query(
        self,
        db: Session,
        student_profile: StudentProfile,
        query: str
    ) -> Dict[str, Any]:
        """
        Processes student query: RAG retrieval -> context assembly -> AIOrchestrator execution.
        """
        # Step 1: Retrieve grounded context from vector store
        retrieved_context = self.retriever.retrieve_context(query, top_k=3)

        # Step 2: Build student memory context
        student_context = self.memory.build_student_context(db, student_profile)

        # Step 3: Execute AI Orchestrator with RAG prompt template
        variables = {
            "query": query,
            "student_context": student_context,
            "retrieved_context": retrieved_context
        }

        result = self.orchestrator.execute(
            prompt_key="ai_chat_v1",
            variables=variables,
            temperature=0.7,
            json_mode=False
        )

        self.memory.add_message("user", query)
        self.memory.add_message("assistant", result.get("text", ""))

        return {
            "query": query,
            "answer": result.get("text", ""),
            "retrieved_context": retrieved_context,
            "status": "success"
        }
