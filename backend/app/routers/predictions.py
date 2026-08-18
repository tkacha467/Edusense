"""FastAPI Router for Knowledge Decay Risk Predictions."""
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.student import StudentProfile
from app.core.enums import UserRole
from app.services.knowledge_decay_prediction import get_prediction_service, KnowledgeDecayPredictionService
from app.core.exceptions import ForbiddenException, NotFoundException

router = APIRouter(prefix="/predictions", tags=["Predictions"])

class PredictionRequestInput(BaseModel):
    student_id: Optional[str] = Field(None, description="Optional target student profile ID. If omitted, uses current student.")
    skill_id: Optional[str] = Field(None, description="Optional skill ID filter.")
    subject_id: Optional[str] = Field(None, description="Optional subject ID filter.")

class PredictionResponseDTO(BaseModel):
    student_id: str
    skill_id: Optional[str] = None
    subject_id: Optional[str] = None
    forget_probability: float = Field(..., ge=0.0, le=1.0)
    forget_probability_percentage: float = Field(..., ge=0.0, le=100.0)
    risk_level: str = Field(..., description="LOW, MEDIUM, or HIGH")
    prediction_horizon_days: int = 7
    estimated_forgetting_window: str
    recommended_revision_date: str
    revision_priority: str = Field(..., description="urgent, high, medium, low")
    top_risk_factors: List[str]
    top_protective_factors: List[str]
    feature_vector: dict
    model_version: str

@router.post("/forgetting", response_model=PredictionResponseDTO, status_code=status.HTTP_200_OK)
def get_forgetting_prediction(
    input_data: PredictionRequestInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    prediction_service: KnowledgeDecayPredictionService = Depends(get_prediction_service)
) -> Any:
    """
    Computes scientifically defensible knowledge decay prediction and recommended revision dates.
    - Students may query their own predictions.
    - Faculty/Admins may query authorized student predictions.
    """
    target_student_id = input_data.student_id

    role_str = str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role).lower()

    if role_str == "student":
        # Resolve current student's profile
        student_prof = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
        if not student_prof:
            raise NotFoundException("Student profile not found.")
        
        # Security Guard: Prevent student from requesting foreign student's prediction
        if target_student_id and target_student_id != student_prof.id:
            raise ForbiddenException("Unauthorized: Students may only view their own predictions.")
        
        target_student_id = student_prof.id

    elif role_str in ["faculty", "admin", "super_admin"]:
        if not target_student_id:
            raise HTTPException(status_code=400, detail="Faculty must provide a target student_id.")
        
        # Verify student exists
        student_prof = db.query(StudentProfile).filter_by(id=target_student_id).first()
        if not student_prof:
            raise NotFoundException(f"Student profile '{target_student_id}' not found.")
    else:
        raise ForbiddenException("Access denied.")

    result = prediction_service.predict_forgetting_risk(
        db=db,
        student_id=target_student_id,
        skill_id=input_data.skill_id,
        subject_id=input_data.subject_id
    )

    return result


@router.get("/forgetting/{skill_id}", response_model=PredictionResponseDTO)
def get_skill_forgetting_prediction(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    prediction_service: KnowledgeDecayPredictionService = Depends(get_prediction_service)
) -> Any:
    """
    Fetch skill-level forgetting prediction for authenticated student.
    """
    student_prof = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not student_prof:
        raise NotFoundException("Student profile not found.")

    return prediction_service.predict_forgetting_risk(
        db=db,
        student_id=student_prof.id,
        skill_id=skill_id
    )
