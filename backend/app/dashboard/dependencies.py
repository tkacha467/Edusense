"""Dependency providers for Faculty Dashboard module."""
from app.dashboard.service import DashboardService


def get_dashboard_service() -> DashboardService:
    """Provide initialized instance of DashboardService."""
    return DashboardService()
