"""Knowledge Decay ML & Retention APIs router."""
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.enums import PredictionTrigger
from app.dependencies.auth import get_current_user, require_onboarding_completed
from app.dependencies.database import get_db
from app.models.student import StudentProfile
from app.schemas.knowledge import KnowledgeProfileResponse, PredictionHistoryResponse
from app.services.knowledge import KnowledgeDecayService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Decay ML Engine"])

def get_knowledge_decay_service() -> KnowledgeDecayService: return KnowledgeDecayService()


class ManualPredictionTriggerInput(BaseModel):
    """Input payload for triggering manual skill prediction."""
    skill_id: str = Field(..., description="Target skill ID to evaluate")


@router.get("/profiles", response_model=List[KnowledgeProfileResponse])
def get_student_knowledge_profiles(
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    knowledge_service: KnowledgeDecayService = Depends(get_knowledge_decay_service)
) -> Any:
    """
    Fetch student knowledge profiles across all practiced skills.
    """
    profiles = knowledge_service.get_student_knowledge_profiles(db, student_id=student_profile.id)
    return profiles


@router.get("/at-risk", response_model=List[KnowledgeProfileResponse])
def get_at_risk_skills(
    threshold: float = Query(0.50, ge=0.0, le=1.0, description="Forget probability threshold"),
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    knowledge_service: KnowledgeDecayService = Depends(get_knowledge_decay_service)
) -> Any:
    """
    Fetch skills with forgetting probability above threshold (at-risk skills).
    """
    at_risk_profiles = knowledge_service.get_at_risk_skills(
        db=db,
        student_id=student_profile.id,
        threshold=threshold
    )
    return at_risk_profiles


@router.get("/skills/{skill_id}/trend", response_model=List[PredictionHistoryResponse])
def get_skill_prediction_trend(
    skill_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    knowledge_service: KnowledgeDecayService = Depends(get_knowledge_decay_service)
) -> Any:
    """
    Fetch historical prediction timeline for a specific skill.
    """
    trend = knowledge_service.get_skill_prediction_trend(
        db=db,
        student_id=student_profile.id,
        skill_id=skill_id
    )
    return trend


@router.post("/predict", response_model=KnowledgeProfileResponse)
def trigger_manual_prediction(
    input_data: ManualPredictionTriggerInput,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    knowledge_service: KnowledgeDecayService = Depends(get_knowledge_decay_service)
) -> Any:
    """
    Manually trigger feature calculation and ML model inference for a skill.
    """
    updated_profile, _ = knowledge_service.run_prediction_pipeline(
        db=db,
        student_id=student_profile.id,
        skill_id=input_data.skill_id,
        triggered_by=PredictionTrigger.MANUAL
    )
    return updated_profile
