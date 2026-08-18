"""AI Platform REST API router."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, require_onboarding_completed, require_role
from app.dependencies.database import get_db
from app.models import User, StudentProfile
from app.core.enums import UserRole
from app.services.ollama_service import get_ollama_rag_service
from app.ai.orchestrator import AIOrchestrator
from app.ai.chat.assistant import AIStudyAssistant
from app.ai.flashcards.generator import FlashcardGenerator
from app.ai.summaries.summarizer import StudyNotesSummarizer
from app.ai.explanations.engine import ExplanationEngine
from app.ai.hints.generator import HintGenerator
from app.ai.question_generation.generator import AIQuestionGenerator
from app.ai.recommendations.writer import AIRecommendationWriter
from app.services.adaptive.decision_engine import RecommendationDecisionEngine

router = APIRouter(prefix="/ai", tags=["AI Platform Engine"])

def get_orchestrator() -> AIOrchestrator:
    return AIOrchestrator()


# Pydantic Schemas for AI Endpoints
class ChatQueryInput(BaseModel):
    query: str = Field(..., description="Student query")

class ExplainInput(BaseModel):
    concept_name: str
    subject_name: Optional[str] = "Computer Science"
    difficulty: Optional[str] = "intermediate"

class SummarizeInput(BaseModel):
    topic_name: str

class FlashcardInput(BaseModel):
    skill_name: str
    difficulty: Optional[str] = "intermediate"
    count: Optional[int] = 3

class HintInput(BaseModel):
    question_text: str
    skill_name: Optional[str] = "Target Skill"

class QuestionGenInput(BaseModel):
    topic_name: str
    subject_name: Optional[str] = "Computer Science"
    question_type: Optional[str] = "mcq"
    difficulty: Optional[str] = "intermediate"
    count: Optional[int] = 3

class RecommendationTextInput(BaseModel):
    skill_id: str


@router.post("/chat")
async def chat_with_ai_assistant(
    input_data: ChatQueryInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
) -> Any:
    """Grounded AI Study Assistant conversation endpoint."""
    assistant = AIStudyAssistant(orchestrator=orchestrator, student_id=student_profile.id)
    return await assistant.answer_query(db, student_profile, input_data.query)


@router.post("/explain")
async def explain_concept(
    input_data: ExplainInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
) -> Any:
    """Grounded concept explanation with analogies and examples."""
    engine = ExplanationEngine(orchestrator=orchestrator)
    return await engine.explain_concept(
        concept_name=input_data.concept_name,
        subject_name=input_data.subject_name or "Computer Science",
        difficulty=input_data.difficulty or "intermediate"
    )


@router.post("/summarize")
async def summarize_topic(
    input_data: SummarizeInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
) -> Any:
    """Grounded study notes summarizer."""
    summarizer = StudyNotesSummarizer(orchestrator=orchestrator)
    return await summarizer.generate_summary(topic_name=input_data.topic_name)


@router.post("/flashcards")
async def generate_flashcards(
    input_data: FlashcardInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
) -> Any:
    """Generates adaptive flashcards for spaced repetition."""
    generator = FlashcardGenerator(orchestrator=orchestrator)
    return await generator.generate_flashcards(
        skill_name=input_data.skill_name,
        difficulty=input_data.difficulty or "intermediate",
        count=input_data.count or 3
    )


@router.post("/hints")
async def generate_hint(
    input_data: HintInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
) -> Any:
    """Generates progressive hints without spoiling correct answers."""
    generator = HintGenerator(orchestrator=orchestrator)
    return await generator.generate_hint(
        question_text=input_data.question_text,
        skill_name=input_data.skill_name or "Target Skill"
    )


@router.post("/questions")
async def generate_questions(
    input_data: QuestionGenInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
) -> Any:
    """Multi-format question generator (MCQ, True/False, Short Answer, Coding)."""
    generator = AIQuestionGenerator(orchestrator=orchestrator)
    return await generator.generate_questions(
        topic_name=input_data.topic_name,
        subject_name=input_data.subject_name or "Computer Science",
        question_type=input_data.question_type or "mcq",
        difficulty=input_data.difficulty or "intermediate",
        count=input_data.count or 3
    )


@router.post("/recommendation-text")
async def generate_recommendation_text(
    input_data: RecommendationTextInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
) -> Any:
    """Enhances deterministic study recommendation into encouraging natural language."""
    from app.repositories import KnowledgeProfileRepository
    kp_repo = KnowledgeProfileRepository()
    profile = kp_repo.get_by_student_and_skill(db, student_id=student_profile.id, skill_id=input_data.skill_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Skill knowledge profile not found")

    decision_engine = RecommendationDecisionEngine()
    writer = AIRecommendationWriter(orchestrator=orchestrator)

    decision = decision_engine.evaluate_skill_decision(db, student_profile, profile)
    return await writer.enhance_recommendation_text(decision)


@router.get("/history")
async def get_ai_chat_history(
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
) -> Any:
    """Returns conversation history."""
    assistant = AIStudyAssistant(orchestrator=orchestrator, student_id=student_profile.id)
    return {"history": assistant.memory.get_recent_history()}


@router.get("/usage")
async def get_ai_usage_stats(
    current_user: User = Depends(get_current_user),
    orchestrator: AIOrchestrator = Depends(get_orchestrator)
) -> Any:
    """Returns AI Platform latency, usage, and observability statistics."""
    return orchestrator.get_usage_statistics()


# Pydantic Schemas for Dedicated RAG Ollama Endpoints
class StudentExplanationInput(BaseModel):
    student_id: str
    skill_id: Optional[str] = "general"

class RevisionGuidanceInput(BaseModel):
    student_id: str
    skill_id: Optional[str] = "general"

class FacultyStudentAnalysisInput(BaseModel):
    student_id: str

class GroundedMCQGenInput(BaseModel):
    subject_name: str = "Computer Science"
    topic_name: str = "Data Structures"
    difficulty: Optional[str] = "INTERMEDIATE"
    count: Optional[int] = 3


@router.post("/student-explanation")
def get_grounded_student_explanation(
    input_data: StudentExplanationInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    USE CASE A — Student Risk Explanation.
    Provides grounded AI explanation of ML forgetting risk with strict context isolation.
    """
    service = get_ollama_rag_service()
    return service.explain_student_risk(db, current_user, input_data.student_id, input_data.skill_id)


@router.post("/revision-guidance")
def get_grounded_revision_guidance(
    input_data: RevisionGuidanceInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    USE CASE B — Student Revision Guidance.
    """
    service = get_ollama_rag_service()
    return service.generate_revision_guidance(db, current_user, input_data.student_id, input_data.skill_id)


@router.post("/faculty-student-analysis")
def get_faculty_student_analysis(
    input_data: FacultyStudentAnalysisInput,
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    USE CASE C — Faculty Student Analysis.
    """
    service = get_ollama_rag_service()
    return service.explain_faculty_student_analysis(db, current_user, input_data.student_id)


@router.post("/generate-question")
def generate_grounded_questions(
    input_data: GroundedMCQGenInput,
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    USE CASE E — Grounded MCQ Question Generation with Option & Correct Answer Validation.
    """
    service = get_ollama_rag_service()
    return service.generate_grounded_mcqs(
        db,
        subject_name=input_data.subject_name,
        topic_name=input_data.topic_name,
        difficulty=input_data.difficulty or "INTERMEDIATE",
        count=input_data.count or 3
    )
