"""Dashboard repository module for executing database queries."""
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy import func, desc, asc, or_
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.faculty import FacultyProfile
from app.models.student import StudentProfile
from app.models.learning import Skill, Subject
from app.models.knowledge import KnowledgeProfile, PredictionHistory
from app.models.recommendation import StudyTask, TaskStatus
from app.models.analytics import StudentActivity


class DashboardRepository:
    """Repository handling dashboard database analytics and aggregations."""

    def get_faculty_profile(self, db: Session, user_id: str) -> Tuple[User, Optional[FacultyProfile]]:
        """Fetch user and associated faculty profile entity."""
        user = db.query(User).filter(User.id == user_id).first()
        faculty_profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == user_id).first() if user else None
        return user, faculty_profile

    def get_summary_metrics(self, db: Session) -> Dict[str, int]:
        """Aggregate high-level platform counts directly from DB tables."""
        total_students = db.query(func.count(StudentProfile.id)).scalar() or 0
        total_skills = db.query(func.count(Skill.id)).scalar() or 0
        
        # High risk students are those with any knowledge profile having forget_probability > 0.6
        high_risk_students = (
            db.query(func.count(func.distinct(KnowledgeProfile.student_id)))
            .filter(KnowledgeProfile.forget_probability >= 0.6)
            .scalar() or 0
        )
        
        pending_revisions = (
            db.query(func.count(StudyTask.id))
            .filter(StudyTask.status == TaskStatus.PENDING)
            .scalar() or 0
        )
        
        predictions_generated = db.query(func.count(PredictionHistory.id)).scalar() or 0
        active_courses = db.query(func.count(Subject.id)).filter(Subject.is_active == True).scalar() or 0

        return {
            "total_students": total_students,
            "total_skills": total_skills,
            "high_risk_students": high_risk_students,
            "pending_revisions": pending_revisions,
            "predictions_generated": predictions_generated,
            "active_courses": active_courses,
        }

    def get_knowledge_health_time_series(self, db: Session) -> List[Dict[str, Any]]:
        """Retrieve aggregated daily retention and forget probabilities from prediction history."""
        results = (
            db.query(
                func.date(PredictionHistory.predicted_at).label("pred_date"),
                func.avg(PredictionHistory.retention_score).label("avg_retention"),
                func.avg(PredictionHistory.forget_probability).label("avg_forget_prob"),
                func.count(PredictionHistory.id).label("pred_count")
            )
            .group_by(func.date(PredictionHistory.predicted_at))
            .order_by(asc("pred_date"))
            .limit(30)
            .all()
        )

        time_series = []
        for r in results:
            time_series.append({
                "date_label": str(r.pred_date) if r.pred_date else "",
                "avg_retention": round(float(r.avg_retention or 0.0), 3),
                "avg_forget_prob": round(float(r.avg_forget_prob or 0.0), 3),
                "predictions_count": int(r.pred_count or 0),
            })
        return time_series

    def get_revision_queue_paginated(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        sort_by: str = "forget_probability",
        sort_order: str = "desc",
        search: Optional[str] = None,
        priority_filter: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Fetch paginated student knowledge profiles requiring revision."""
        query = (
            db.query(KnowledgeProfile)
            .join(StudentProfile, KnowledgeProfile.student_id == StudentProfile.id)
            .join(User, StudentProfile.user_id == User.id)
            .join(Skill, KnowledgeProfile.skill_id == Skill.id)
        )

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.display_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    Skill.name.ilike(search_pattern)
                )
            )

        if priority_filter:
            p_upper = priority_filter.upper()
            if p_upper == "HIGH":
                query = query.filter(KnowledgeProfile.forget_probability >= 0.6)
            elif p_upper == "MEDIUM":
                query = query.filter(KnowledgeProfile.forget_probability >= 0.3, KnowledgeProfile.forget_probability < 0.6)
            elif p_upper == "LOW":
                query = query.filter(KnowledgeProfile.forget_probability < 0.3)

        total = query.count()

        # Sorting
        if sort_by == "student_name":
            order_col = User.display_name
        elif sort_by == "skill_name":
            order_col = Skill.name
        else:
            order_col = KnowledgeProfile.forget_probability

        if sort_order.lower() == "asc":
            query = query.order_by(asc(order_col))
        else:
            query = query.order_by(desc(order_col))

        offset = (page - 1) * size
        profiles = query.offset(offset).limit(size).all()

        items = []
        for kp in profiles:
            student_name = kp.student.user.display_name if (kp.student and kp.student.user) else "Unknown Student"
            skill_name = kp.skill.name if kp.skill else "General Skill"
            fp = float(kp.forget_probability or 0.0)

            priority = "HIGH" if fp >= 0.6 else ("MEDIUM" if fp >= 0.3 else "LOW")
            status = "PENDING" if fp >= 0.5 else "COMPLETED"

            rec_date = kp.last_predicted_at.strftime("%Y-%m-%d") if kp.last_predicted_at else datetime.utcnow().strftime("%Y-%m-%d")

            items.append({
                "id": str(kp.id),
                "student_id": str(kp.student_id),
                "student_name": student_name,
                "skill_id": str(kp.skill_id),
                "skill_name": skill_name,
                "forget_probability": round(fp, 3),
                "revision_priority": priority,
                "recommended_revision_date": rec_date,
                "status": status
            })

        return items, total

    def get_weak_skills(self, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Identify skills with highest forget probability or lowest mastery across all students."""
        results = (
            db.query(
                Skill.id.label("skill_id"),
                Skill.name.label("skill_name"),
                func.avg(KnowledgeProfile.past_accuracy).label("avg_mastery"),
                func.avg(KnowledgeProfile.forget_probability).label("avg_forget_prob"),
                func.count(func.distinct(KnowledgeProfile.student_id)).label("students_affected")
            )
            .join(KnowledgeProfile, Skill.id == KnowledgeProfile.skill_id)
            .group_by(Skill.id, Skill.name)
            .order_by(desc("avg_forget_prob"))
            .limit(limit)
            .all()
        )

        weak_skills = []
        for r in results:
            weak_skills.append({
                "skill_id": str(r.skill_id),
                "skill_name": str(r.skill_name),
                "avg_mastery": round(float(r.avg_mastery or 0.0), 3),
                "avg_forget_probability": round(float(r.avg_forget_prob or 0.0), 3),
                "students_affected": int(r.students_affected or 0),
            })
        return weak_skills

    def get_recent_activities(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent student activities log."""
        activities = (
            db.query(StudentActivity)
            .join(StudentProfile, StudentActivity.student_id == StudentProfile.id)
            .join(User, StudentProfile.user_id == User.id)
            .order_by(desc(StudentActivity.activity_date))
            .limit(limit)
            .all()
        )

        result = []
        for act in activities:
            student_name = act.student.user.display_name if (act.student and act.student.user) else "Student"
            act_type = str(act.activity_type.value) if hasattr(act.activity_type, "value") else str(act.activity_type)
            result.append({
                "id": str(act.id),
                "student_name": student_name,
                "activity_type": act_type.replace("_", " ").title(),
                "description": f"Engaged in {act_type.replace('_', ' ')} session",
                "timestamp": act.activity_date.strftime("%Y-%m-%d") if act.activity_date else ""
            })
        return result
