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
    AssessmentSubmission, AssessmentResult,
    AdaptiveStartInput, SubmitSingleAnswerInput
)
from app.schemas.base import PaginatedResponse
from app.services.assessment import AssessmentService
from app.services.learning import SubjectService, TopicService
from app.services.adaptive.assessment_orchestrator import AssessmentOrchestrator

router = APIRouter(prefix="/assessments", tags=["Assessment Engine"])

def get_assessment_service() -> AssessmentService: return AssessmentService()
def get_subject_service() -> SubjectService: return SubjectService()
def get_topic_service() -> TopicService: return TopicService()
def get_orchestrator() -> AssessmentOrchestrator: return AssessmentOrchestrator()


@router.post("/generate", response_model=AssessmentSessionResponse, status_code=status.HTTP_201_CREATED)
async def generate_assessment_session(
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
    generated_dtos = await ai_generator.generate_questions(
        subject_name=subject.name,
        topic_name=topic_name,
        difficulty=diff_val,
        count=session_data.total_questions
    )

    # 3. Add questions & options to session in database
    from app.models.learning import Skill
    db_skill = db.query(Skill).first()
    selected_skill_id = str(db_skill.id) if db_skill else "adca46c6-d4c4-4467-9904-a4b69919459d"

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
            "skill_id": selected_skill_id,
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
    return {
        "items": [AssessmentSessionResponse.model_validate(h) for h in history],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
    }


@router.get("/{session_id}", response_model=AssessmentSessionResponse)
def get_assessment_session_by_id(
    session_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    assessment_service: AssessmentService = Depends(get_assessment_service)
) -> Any:
    """
    Fetch full details for a specific assessment session by session_id.
    """
    session = assessment_service.get_assessment_detail(db, session_id=session_id, student_id=student_profile.id)
    return session


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
    session = assessment_service.start_assessment(db, session_id=session_id, student_id=student_profile.id)
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
    session = assessment_service.get_assessment_detail(db, session_id=session_id, student_id=student_profile.id)
    
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
    background_tasks: getattr(__import__("fastapi"), "BackgroundTasks"),
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    assessment_service: AssessmentService = Depends(get_assessment_service)
) -> Any:
    """
    Submit assessment responses, auto-evaluate correct answers, update student skill proficiency,
    and return evaluation result breakdown.
    """
    try:
        responses_payload = [r.model_dump() for r in submission.responses]
        result_data = assessment_service.submit_assessment(
            db=db,
            session_id=session_id,
            student_id=student_profile.id,
            responses=responses_payload
        )

        # Run prediction, planner and timeline updates synchronously inside the transaction
        from app.services.knowledge import KnowledgeDecayService
        from app.services.adaptive.planner import RevisionPlanner
        from app.services.adaptive.timeline import LearningTimelineService

        kd_service = KnowledgeDecayService()
        skill_updates = result_data.pop("skill_updates", [])
        for skill_id in skill_updates:
            kd_service.run_prediction_pipeline(
                db=db, 
                student_id=student_profile.id, 
                skill_id=skill_id
            )

        planner = RevisionPlanner()
        planner.generate_adaptive_study_plan(
            db=db, 
            student_profile=student_profile
        )

        timeline_service = LearningTimelineService()
        timeline_service.record_event(
            db=db,
            user_id=student_profile.user_id,
            event_name="Assessment Completed",
            entity_type="AssessmentSession",
            entity_id=session_id,
            details=f"Completed assessment and generated adaptive recommendations."
        )

        db.commit()
        
        return {
            "assessment_session_id": session_id,
            "total_questions": result_data["total_questions"],
            "correct_answers": result_data["correct_answers"],
            "scored_marks": result_data["scored_marks"],
            "total_marks": result_data["total_marks"],
            "percentage": result_data["percentage"],
            "time_taken_seconds": result_data.get("time_taken_seconds", 0)
        }
    except Exception as e:
        db.rollback()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to submit assessment: {str(e)}")



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
    session = assessment_service.abandon_assessment(db, session_id=session_id, student_id=student_profile.id)
    return session


@router.post("/start", response_model=AssessmentSessionResponse, status_code=status.HTTP_201_CREATED)
def start_adaptive_assessment(
    input_data: AdaptiveStartInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    orchestrator: AssessmentOrchestrator = Depends(get_orchestrator)
) -> Any:
    """
    Start a dynamic, adaptive assessment session for a student.
    """
    session = orchestrator.start_adaptive_session(
        db=db,
        student_id=student_profile.id,
        subject_id=input_data.subject_id,
        title=input_data.title,
        total_questions=input_data.total_questions
    )
    db.commit()
    return session


@router.get("/{session_id}/next")
async def get_adaptive_next_question(
    session_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    orchestrator: AssessmentOrchestrator = Depends(get_orchestrator)
) -> Any:
    """
    Dynamically retrieve or generate the next question in an active adaptive session.
    """
    res = await orchestrator.get_or_generate_next_question(
        db=db,
        session_id=session_id,
        student_id=student_profile.id
    )
    if not res:
        return {"completed": True}
        
    question, q_num = res
    db.commit()
    
    return {
        "completed": False,
        "question_number": q_num,
        "question": {
            "id": str(question.id),
            "question_text": question.question_text,
            "question_type": question.question_type,
            "difficulty_level": question.difficulty_level,
            "marks": question.marks,
            "hint": question.hint,
            "options": [
                {
                    "id": str(opt.id),
                    "option_label": opt.option_label,
                    "option_text": opt.option_text,
                    "order_index": opt.order_index
                } for opt in question.options
            ]
        }
    }


@router.post("/{session_id}/answer")
def submit_adaptive_answer(
    session_id: str,
    input_data: SubmitSingleAnswerInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    orchestrator: AssessmentOrchestrator = Depends(get_orchestrator)
) -> Any:
    """
    Submit a single response, evaluate correctness, and dynamically update profiles/forgetting probability in real-time.
    """
    try:
        evaluation = orchestrator.submit_single_answer(
            db=db,
            session_id=session_id,
            student_id=student_profile.id,
            question_id=input_data.question_id,
            selected_option_id=input_data.selected_option_id,
            time_taken_seconds=input_data.time_taken_seconds
        )
        db.commit()
        return evaluation
    except Exception as e:
        db.rollback()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/finish")
def finish_adaptive_session(
    session_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    orchestrator: AssessmentOrchestrator = Depends(get_orchestrator)
) -> Any:
    """
    Explicitly conclude the adaptive test session and compile the summary report.
    """
    try:
        result = orchestrator.finish_session(
            db=db,
            session_id=session_id,
            student_id=student_profile.id
        )
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/summary")
def get_adaptive_session_summary(
    session_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    orchestrator: AssessmentOrchestrator = Depends(get_orchestrator)
) -> Any:
    """
    Fetch the results summary details for a completed assessment session.
    """
    session = orchestrator.session_repo.get_by_id(db, session_id)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found.")
        
    stmt_res = select(StudentResponse).where(StudentResponse.assessment_session_id == session_id)
    responses = list(db.execute(stmt_res).scalars().all())

    total_questions = len(responses)
    correct_count = sum(1 for r in responses if r.is_correct)
    total_marks = sum(1.0 for r in responses)
    scored_marks = sum(1.0 for r in responses if r.is_correct)
    percentage = (scored_marks / total_marks * 100) if total_marks > 0 else 0.0

    return {
        "assessment_session_id": session_id,
        "total_questions": total_questions,
        "correct_answers": correct_count,
        "scored_marks": scored_marks,
        "total_marks": total_marks,
        "percentage": percentage,
        "time_taken_seconds": sum(r.time_taken_seconds for r in responses)
    }
