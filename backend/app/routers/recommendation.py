"""Adaptive Recommendation & Study Planner REST API router."""
from datetime import datetime, timezone
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import require_onboarding_completed
from app.dependencies.database import get_db
from app.models import StudentProfile, StudyPlan, StudyTask
from app.repositories import StudyPlanRepository, StudyTaskRepository, KnowledgeProfileRepository
from app.schemas.recommendation import StudyPlanResponse, StudyTaskResponse
from app.services.adaptive.decision_engine import RecommendationDecisionEngine, RecommendationDecision
from app.services.adaptive.planner import RevisionPlanner
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="", tags=["Adaptive Recommendation Engine"])

def get_planner() -> RevisionPlanner: return RevisionPlanner()
def get_decision_engine() -> RecommendationDecisionEngine: return RecommendationDecisionEngine()
def get_recommendation_service() -> RecommendationService: return RecommendationService()


@router.get("/recommendations", response_model=List[Dict[str, Any]])
def get_student_recommendations(
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    engine: RecommendationDecisionEngine = Depends(get_decision_engine)
) -> Any:
    """Fetch personalized adaptive recommendation decisions for student's skills."""
    kp_repo = KnowledgeProfileRepository()
    profiles = kp_repo.get_by_student(db, student_id=student_profile.id)
    decisions = [engine.evaluate_skill_decision(db, student_profile, p) for p in profiles]
    return [dec.__dict__ for dec in decisions]


@router.get("/recommendations/today", response_model=List[StudyTaskResponse])
def get_today_recommendations(
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    rec_service: RecommendationService = Depends(get_recommendation_service)
) -> Any:
    """Fetch tasks recommended and scheduled for today."""
    return rec_service.get_today_tasks(db, student_id=student_profile.id)


@router.get("/recommendations/upcoming", response_model=List[StudyTaskResponse])
def get_upcoming_recommendations(
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    rec_service: RecommendationService = Depends(get_recommendation_service)
) -> Any:
    """Fetch upcoming pending study tasks."""
    return rec_service.get_pending_tasks(db, student_id=student_profile.id)


@router.post("/recommendations/generate", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
def generate_recommendations_and_plan(
    subject_id: Optional[str] = None,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    planner: RevisionPlanner = Depends(get_planner)
) -> Any:
    """Triggers generation of an adaptive study plan and prioritized tasks."""
    plan = planner.generate_adaptive_study_plan(db, student_profile, subject_id=subject_id)
    return plan


@router.get("/study-plans", response_model=List[StudyPlanResponse])
def get_study_plans(
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    rec_service: RecommendationService = Depends(get_recommendation_service)
) -> Any:
    """List student study plans."""
    return rec_service.plan_repo.get_by_student(db, student_id=student_profile.id)


@router.get("/study-plans/{plan_id}", response_model=StudyPlanResponse)
def get_study_plan_detail(
    plan_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    rec_service: RecommendationService = Depends(get_recommendation_service)
) -> Any:
    """Get study plan detail by ID."""
    plan = rec_service.get_plan_detail(db, plan_id=plan_id)
    if not plan or plan.student_id != student_profile.id:
        raise HTTPException(status_code=404, detail="Study plan not found")
    return plan


@router.put("/study-tasks/{task_id}/complete", response_model=StudyTaskResponse)
def complete_study_task(
    task_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    rec_service: RecommendationService = Depends(get_recommendation_service)
) -> Any:
    """Mark a study task as completed."""
    task = rec_service.complete_task(db, task_id=task_id, student_id=student_profile.id)
    db.commit()
    return task


@router.put("/study-tasks/{task_id}/skip", response_model=StudyTaskResponse)
def skip_study_task(
    task_id: str,
    student_profile: StudentProfile = Depends(require_onboarding_completed),
    db: Session = Depends(get_db),
    rec_service: RecommendationService = Depends(get_recommendation_service)
) -> Any:
    """Mark a study task as skipped."""
    task = rec_service.skip_task(db, task_id=task_id, student_id=student_profile.id)
    db.commit()
    return task
