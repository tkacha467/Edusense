"""Assessment Engine router."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.ai.question_generation.generator import AIQuestionGenerator
from app.dependencies.auth import get_current_user, require_role, require_onboarding_completed
from app.dependencies.database import get_db
from app.models.user import User
from app.models.student import StudentProfile
from app.schemas.assessment import (
    AssessmentSessionCreate, AssessmentSessionResponse,
    QuestionOptionPublic, QuestionResponse,
    AssessmentSubmission, AssessmentResult
)
from app.schemas.base import PaginatedResponse
from app.services.assessment import AssessmentService
from app.services.learning import SubjectService, TopicService

router = APIRouter(prefix="/assessments", tags=["Assessment Engine"])

def get_assessment_service() -> AssessmentService: return AssessmentService()
def get_subject_service() -> SubjectService: return SubjectService()
def get_topic_service() -> TopicService: return TopicService()


@router.post("/generate", response_model=AssessmentSessionResponse, status_code=status.HTTP_201_CREATED)
def generate_assessment_session(
    session_data: AssessmentSessionCreate,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    assessment_service: AssessmentService = Depends(get_assessment_service),
    subject_service: SubjectService = Depends(get_subject_service),
    topic_service: TopicService = Depends(get_topic_service)
) -> Any:
    """
    Generate a new assessment session and populate questions via AI Gateway Provider.
    """
    subject = subject_service.get_subject(db, subject_id=session_data.subject_id)
    topic_name = None
    if session_data.topic_id:
        topic = topic_service.get_topic(db, topic_id=session_data.topic_id)
        topic_name = topic.name

    # 1. Create PENDING Session
    session = assessment_service.create_assessment_session(
        db=db,
        student_id=student_profile.id,
        subject_id=session_data.subject_id,
        topic_id=session_data.topic_id,
        title=session_data.title,
        difficulty=session_data.difficulty_level.value if hasattr(session_data.difficulty_level, 'value') else str(session_data.difficulty_level),
        total_questions=session_data.total_questions,
        time_limit=session_data.time_limit_seconds or 900,
        generation_method=session_data.generation_method.value if hasattr(session_data.generation_method, 'value') else str(session_data.generation_method)
    )

    # 2. Invoke AI Question Generator
    ai_generator = AIQuestionGenerator()
    diff_val = session_data.difficulty_level.value if hasattr(session_data.difficulty_level, 'value') else str(session_data.difficulty_level)
    generated_dtos = ai_generator.generate_questions(
        subject_name=subject.name,
        topic_name=topic_name,
        difficulty=diff_val,
        count=session_data.total_questions
    )

    # 3. Add questions & options to session in database
    questions_payload = []
    for idx, dto in enumerate(generated_dtos):
        diff_str = str(dto.get("difficulty_level", "MEDIUM")).upper()
        if "BEGINNER" in diff_str or "EASY" in diff_str:
            mapped_diff = "EASY"
        elif "ADVANCED" in diff_str or "HARD" in diff_str:
            mapped_diff = "HARD"
        else:
            mapped_diff = "MEDIUM"

        questions_payload.append({
            "topic_id": session_data.topic_id,
            "question_text": dto.get("question_text"),
            "question_type": dto.get("question_type", "MCQ").upper() if dto.get("question_type") else "MCQ",
            "difficulty_level": mapped_diff,
            "marks": dto.get("marks", 1.0),
            "correct_answer": dto.get("correct_answer"),
            "explanation": dto.get("explanation"),
            "hint": dto.get("hint"),
            "order_index": idx,
            "ai_model_used": dto.get("ai_model_used"),
            "ai_generation_params": dto.get("ai_generation_params"),
            "options": dto.get("options", [])
        })

    assessment_service.add_questions_to_session(db, session_id=session.id, questions_data=questions_payload)
    
    # Reload session with questions
    updated_session = assessment_service.get_assessment_detail(db, session_id=session.id)
    return updated_session


@router.post("/{session_id}/start", response_model=AssessmentSessionResponse)
def start_assessment_session(
    session_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    assessment_service: AssessmentService = Depends(get_assessment_service)
) -> Any:
    """
    Transition assessment session state from PENDING to IN_PROGRESS and stamp started_at.
    """
    session = assessment_service.start_assessment(db, session_id=session_id)
    return session


@router.get("/{session_id}/questions", response_model=List[Dict[str, Any]])
def get_assessment_questions(
    session_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    assessment_service: AssessmentService = Depends(get_assessment_service)
) -> Any:
    """
    Fetch questions for an active test session without revealing correct answers or explanations.
    """
    session = assessment_service.get_assessment_detail(db, session_id=session_id)
    
    public_questions = []
    for q in session.questions:
        options_public = [
            {
                "id": opt.id,
                "option_label": opt.option_label,
                "option_text": opt.option_text,
                "order_index": opt.order_index
            }
            for opt in q.options
        ]
        public_questions.append({
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "difficulty_level": q.difficulty_level,
            "marks": q.marks,
            "hint": q.hint,
            "order_index": q.order_index,
            "options": options_public
        })

    return public_questions


@router.post("/{session_id}/submit", response_model=AssessmentResult)
def submit_assessment_session(
    session_id: str,
    submission: AssessmentSubmission,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    assessment_service: AssessmentService = Depends(get_assessment_service)
) -> Any:
    """
    Submit assessment responses, auto-evaluate correct answers, update student skill proficiency,
    and return evaluation result breakdown.
    """
    responses_payload = [r.model_dump() for r in submission.responses]
    result_data = assessment_service.submit_assessment(
        db=db,
        session_id=session_id,
        student_id=student_profile.id,
        responses=responses_payload
    )

    return {
        "assessment_session_id": session_id,
        "total_questions": result_data["total_questions"],
        "correct_answers": result_data["correct_answers"],
        "scored_marks": result_data["scored_marks"],
        "total_marks": result_data["total_marks"],
        "percentage": result_data["percentage"],
        "time_taken_seconds": result_data.get("time_taken_seconds", 0)
    }


@router.get("/history", response_model=PaginatedResponse[AssessmentSessionResponse])
def get_student_assessment_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    assessment_service: AssessmentService = Depends(get_assessment_service)
) -> Any:
    """
    Fetch paginated assessment session history for the logged-in student.
    """
    history, total = assessment_service.get_assessment_history(
        db=db,
        student_id=student_profile.id,
        page=page,
        page_size=page_size
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return {
        "items": [AssessmentSessionResponse.model_validate(h) for h in history],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.post("/{session_id}/abandon", response_model=AssessmentSessionResponse)
def abandon_assessment_session(
    session_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    assessment_service: AssessmentService = Depends(get_assessment_service)
) -> Any:
    """
    Abandon an in-progress assessment session.
    """
    session = assessment_service.abandon_assessment(db, session_id=session_id)
    return session
