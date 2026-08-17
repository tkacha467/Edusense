"""Seed script to populate local EduSense DB with realistic student decay data."""
import sys
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Set default env vars for dev seeding
os.environ.setdefault("SECRET_KEY", "dev_secret_key_edusense_ai_2026_super_secure")
os.environ.setdefault("DATABASE_URL", "sqlite:///./edusense.db")

from app.config import get_settings
from app.database.database import get_engine
from app.database.session import get_session_factory
from app.database.base import BaseModel
import app.models  # Register all models

from app.models.user import User
from app.models.student import StudentProfile
from app.models.learning import Subject, Skill, StudentSubject, StudentSkill
from app.models.knowledge import KnowledgeProfile, PredictionHistory
from app.core.enums import UserRole, UserStatus

def seed_demo_dataset():
    print("[+] Initializing EduSense AI Seed Data Generation...")
    settings = get_settings()
    engine = get_engine(settings)
    
    # Auto-create SQLite tables if they do not exist
    BaseModel.metadata.create_all(bind=engine)
    print("[+] Database tables verified/created successfully.")

    SessionFactory = get_session_factory(engine)
    db = SessionFactory()

    try:
        # 1. Ensure Faculty User exists
        faculty_email = "faculty@edusense.ai"
        faculty_user = db.query(User).filter(User.email == faculty_email).first()
        if not faculty_user:
            faculty_user = User(
                id=str(uuid.uuid4()),
                firebase_uid=f"firebase_fac_{uuid.uuid4().hex[:8]}",
                email=faculty_email,
                display_name="Prof. Sarah Jenkins",
                role=UserRole.FACULTY,
                status=UserStatus.ACTIVE,
                is_active=True,
                is_email_verified=True
            )
            db.add(faculty_user)
            db.commit()
            db.refresh(faculty_user)
            print(f"[+] Created Faculty User: {faculty_user.display_name} ({faculty_user.email})")

        # 2. Subjects and Skills Data
        subject_catalog = [
            {
                "code": "CS-401",
                "name": "Logit Function & AI Logic",
                "department": "Computer Science",
                "semester": 4,
                "skills": [
                    {"code": "SK-LOG-01", "name": "Logit Function Complexity"},
                    {"code": "SK-LOG-02", "name": "Sigmoid Activation Curves"},
                    {"code": "SK-LOG-03", "name": "Binary Cross-Entropy Loss"}
                ]
            },
            {
                "code": "CS-601",
                "name": "Neural Decay Networks",
                "department": "Computer Science",
                "semester": 6,
                "skills": [
                    {"code": "SK-NEU-01", "name": "Gradient Descent Rates"},
                    {"code": "SK-NEU-02", "name": "Backpropagation Matrix Calculus"},
                    {"code": "SK-NEU-03", "name": "Weight Decay Regularization"}
                ]
            },
            {
                "code": "DS-402",
                "name": "Matrix Calculus",
                "department": "Data Science",
                "semester": 4,
                "skills": [
                    {"code": "SK-MAT-01", "name": "Jacobian Determinants"},
                    {"code": "SK-MAT-02", "name": "Hessian Matrix Optimization"},
                    {"code": "SK-MAT-03", "name": "Vector Partial Derivatives"}
                ]
            }
        ]

        created_subjects = []
        created_skills = []

        for subj_data in subject_catalog:
            subj = db.query(Subject).filter(Subject.code == subj_data["code"]).first()
            if not subj:
                subj = Subject(
                    id=str(uuid.uuid4()),
                    code=subj_data["code"],
                    name=subj_data["name"],
                    category=subj_data["department"],
                    semester=subj_data["semester"],
                    description=f"Course on {subj_data['name']}"
                )
                db.add(subj)
                db.commit()
                db.refresh(subj)
            created_subjects.append(subj)

            for sk_data in subj_data["skills"]:
                sk = db.query(Skill).filter(Skill.name == sk_data["name"]).first()
                if not sk:
                    sk = Skill(
                        id=str(uuid.uuid4()),
                        name=sk_data["name"],
                        category="Core Concept"
                    )
                    db.add(sk)
                    db.commit()
                    db.refresh(sk)
                created_skills.append(sk)

        print(f"[+] Created/Verified {len(created_subjects)} Subjects and {len(created_skills)} Skills")

        # 3. Student Roster Data (15 Students with realistic decay distribution)
        roster = [
            {"name": "Alex Vance", "email": "alex.vance@student.edusense.ai", "enrollment": "EDU-2026-AV8910", "risk": "Critical", "health": 42.5, "prob": 0.72},
            {"name": "Sarah Connor", "email": "sarah.c@student.edusense.ai", "enrollment": "EDU-2026-SC4421", "risk": "High", "health": 58.0, "prob": 0.58},
            {"name": "Marcus Wright", "email": "marcus.w@student.edusense.ai", "enrollment": "EDU-2026-MW9012", "risk": "High", "health": 54.2, "prob": 0.54},
            {"name": "Elena Rostova", "email": "elena.r@student.edusense.ai", "enrollment": "EDU-2026-ER1102", "risk": "Medium", "health": 68.5, "prob": 0.38},
            {"name": "David Chen", "email": "david.c@student.edusense.ai", "enrollment": "EDU-2026-DC5534", "risk": "Low", "health": 88.0, "prob": 0.12},
            {"name": "Priya Sharma", "email": "priya.s@student.edusense.ai", "enrollment": "EDU-2026-PS8890", "risk": "Low", "health": 92.4, "prob": 0.08},
            {"name": "Jordan Miller", "email": "jordan.m@student.edusense.ai", "enrollment": "EDU-2026-JM3341", "risk": "Low", "health": 84.0, "prob": 0.15},
            {"name": "Sophia Martinez", "email": "sophia.m@student.edusense.ai", "enrollment": "EDU-2026-SM7782", "risk": "Low", "health": 86.5, "prob": 0.14},
            {"name": "Liam O'Connor", "email": "liam.o@student.edusense.ai", "enrollment": "EDU-2026-LO9912", "risk": "Medium", "health": 72.0, "prob": 0.32},
            {"name": "Zoe Wang", "email": "zoe.w@student.edusense.ai", "enrollment": "EDU-2026-ZW2201", "risk": "Low", "health": 90.1, "prob": 0.09},
            {"name": "Karthik Raja", "email": "karthik.r@student.edusense.ai", "enrollment": "EDU-2026-KR6678", "risk": "Low", "health": 85.3, "prob": 0.16},
            {"name": "Aisha Patel", "email": "aisha.p@student.edusense.ai", "enrollment": "EDU-2026-AP4456", "risk": "Low", "health": 89.0, "prob": 0.11},
            {"name": "Lucas Silva", "email": "lucas.s@student.edusense.ai", "enrollment": "EDU-2026-LS1123", "risk": "Medium", "health": 69.4, "prob": 0.35},
            {"name": "Emily Watson", "email": "emily.w@student.edusense.ai", "enrollment": "EDU-2026-EW8834", "risk": "Low", "health": 87.2, "prob": 0.13},
            {"name": "Noah Taylor", "email": "noah.t@student.edusense.ai", "enrollment": "EDU-2026-NT5567", "risk": "Low", "health": 91.5, "prob": 0.07}
        ]

        for sdata in roster:
            user = db.query(User).filter(User.email == sdata["email"]).first()
            if not user:
                user = User(
                    id=str(uuid.uuid4()),
                    firebase_uid=f"firebase_stu_{uuid.uuid4().hex[:8]}",
                    email=sdata["email"],
                    display_name=sdata["name"],
                    role=UserRole.STUDENT,
                    status=UserStatus.ACTIVE,
                    is_active=True,
                    is_email_verified=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
            if not profile:
                profile = StudentProfile(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    institution="Engineering Institute of AI",
                    department="Computer Science",
                    semester=4,
                    enrollment_year=2024,
                    onboarding_completed=True
                )
                db.add(profile)
                db.commit()
                db.refresh(profile)

            # Assign Student Subject
            subj = created_subjects[0]
            st_subj = db.query(StudentSubject).filter_by(student_id=profile.id, subject_id=subj.id).first()
            if not st_subj:
                st_subj = StudentSubject(
                    id=str(uuid.uuid4()),
                    student_id=profile.id,
                    subject_id=subj.id,
                    is_active=True
                )
                db.add(st_subj)
                db.commit()

            # Assign Knowledge Profiles & Decay Logs
            for sk in created_skills:
                kp = db.query(KnowledgeProfile).filter_by(student_id=profile.id, skill_id=sk.id).first()
                if not kp:
                    kp = KnowledgeProfile(
                        id=str(uuid.uuid4()),
                        student_id=profile.id,
                        skill_id=sk.id,
                        past_attempts=12,
                        past_correct=int(12 * (sdata["health"] / 100.0)),
                        past_accuracy=sdata["health"] / 100.0,
                        rolling_accuracy=sdata["health"] / 100.0,
                        mastered=(sdata["health"] >= 80.0),
                        forget_probability=sdata["prob"],
                        retention_score=sdata["health"] / 100.0,
                        confidence_score=0.92,
                        last_predicted_at=datetime.now(timezone.utc),
                        last_interaction_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 7))
                    )
                    db.add(kp)
                    db.commit()

        print("[+] Seed Data Generation Completed Successfully!")

    except Exception as e:
        db.rollback()
        print(f"[!] Error seeding database: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_dataset()
