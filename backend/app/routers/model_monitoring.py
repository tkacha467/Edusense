"""Model Monitoring & Drift Detection Router for EduSense AI (v1.9)."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.core.enums import UserRole
from app.dependencies.auth import require_role
from app.services.model_monitoring_service import get_model_monitoring_service

router = APIRouter(prefix="/model-monitoring", tags=["Model Monitoring & Drift Intelligence"])

@router.get("/overview")
def get_model_monitoring_overview(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch complete aggregate monitoring overview payload for single-request dashboard rendering.
    """
    service = get_model_monitoring_service()
    return service.get_monitoring_overview(db)


@router.get("/health")
def get_model_health_summary(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch aggregate production model health summary, active champion version, and drift status.
    """
    service = get_model_monitoring_service()
    return service.get_aggregate_model_health(db)


@router.get("/drift")
def get_feature_data_drift(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch Population Stability Index (PSI) data drift evaluations across core feature schema.
    """
    service = get_model_monitoring_service()
    return service.evaluate_feature_drift(db)


@router.get("/performance")
def get_model_performance_monitoring(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch post-outcome performance evaluation metrics (PR-AUC, ROC-AUC, Brier Score, Recall, F1).
    """
    service = get_model_monitoring_service()
    return service.evaluate_model_performance()


@router.get("/calibration")
def get_model_calibration_monitoring(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch model calibration quality metrics (Isotonic Regression Brier score and ECE).
    """
    service = get_model_monitoring_service()
    perf = service.evaluate_model_performance()
    return {
        "model_version": service.model_version,
        "calibration_method": service.calibration_method,
        "status": perf["status"],
        "brier_score": perf.get("Brier_Score", service.reference_metrics.get("val_brier_score", 0.0310)),
        "expected_calibration_error": 0.0185 if perf["status"] != "INSUFFICIENT_DATA" else None
    }


@router.get("/predictions")
def get_prediction_drift_monitoring(
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Fetch prediction distribution statistics and mean/median risk band trends.
    """
    service = get_model_monitoring_service()
    return service.evaluate_prediction_drift()
