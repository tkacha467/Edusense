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

        # 2. Complete Academic Degree Curriculum Catalog (BCA, MCA, BSc DS, MSc DS, Computer Engg)
        subject_catalog = [
            # BCA (Bachelor of Computer Applications)
            {
                "code": "BCA-101",
                "name": "Programming in C & C++",
                "department": "BCA",
                "semester": 1,
                "topics": ["Pointers & Memory Allocation", "Object Oriented Concepts", "File Handling in C++"],
                "skills": [{"name": "Dynamic Memory Allocation"}, {"name": "Class Inheritance"}, {"name": "File I/O Streams"}]
            },
            {
                "code": "BCA-201",
                "name": "Data Structures & Algorithms",
                "department": "BCA",
                "semester": 2,
                "topics": ["Linked Lists & Stacks", "Binary Search Trees", "Sorting & Searching"],
                "skills": [{"name": "Recursion & Trees"}, {"name": "Array Sorting Complexity"}, {"name": "Stack Push/Pop"}]
            },
            {
                "code": "BCA-301",
                "name": "Database Management Systems (DBMS)",
                "department": "BCA",
                "semester": 3,
                "topics": ["SQL Normalization", "Relational Algebra", "Transactions & ACID"],
                "skills": [{"name": "3NF Normalization"}, {"name": "SQL Join Queries"}, {"name": "ACID Properties"}]
            },
            {
                "code": "BCA-401",
                "name": "Web Technologies (HTML/CSS/JS)",
                "department": "BCA",
                "semester": 4,
                "topics": ["DOM Manipulation", "Async JavaScript & Fetch API", "CSS Grid & Flexbox"],
                "skills": [{"name": "Async/Await API Calls"}, {"name": "Responsive Web Design"}, {"name": "Event Listeners"}]
            },

            # MCA (Master of Computer Applications)
            {
                "code": "MCA-101",
                "name": "Advanced Java & Enterprise Apps",
                "department": "MCA",
                "semester": 1,
                "topics": ["Spring Boot Microservices", "Hibernate ORM", "Java Multithreading"],
                "skills": [{"name": "Dependency Injection"}, {"name": "JPA Entities"}, {"name": "Thread Concurrency"}]
            },
            {
                "code": "MCA-201",
                "name": "Cloud Computing & DevOps",
                "department": "MCA",
                "semester": 2,
                "topics": ["Docker Containerization", "Kubernetes Orchestration", "CI/CD Pipelines"],
                "skills": [{"name": "Dockerfile Configuration"}, {"name": "K8s Pod Scaling"}, {"name": "GitHub Actions Workflow"}]
            },
            {
                "code": "MCA-301",
                "name": "Artificial Intelligence & Expert Systems",
                "department": "MCA",
                "semester": 3,
                "topics": ["Logit Function & AI Logic", "Heuristic Search Algorithms", "Knowledge Representation"],
                "skills": [{"name": "Logit Function Complexity"}, {"name": "A* Search Algorithm"}, {"name": "First-Order Logic"}]
            },

            # B.Sc. Data Science
            {
                "code": "BDS-101",
                "name": "Python for Data Science",
                "department": "B.Sc. Data Science",
                "semester": 1,
                "topics": ["NumPy Array Operations", "Pandas Dataframes", "Matplotlib Visualization"],
                "skills": [{"name": "Vectorized Computations"}, {"name": "Dataframe Filtering"}, {"name": "Statistical Plotting"}]
            },
            {
                "code": "BDS-201",
                "name": "Applied Statistics & Probability",
                "department": "B.Sc. Data Science",
                "semester": 2,
                "topics": ["Hypothesis Testing (t-test)", "Bayesian Probability", "Probability Distributions"],
                "skills": [{"name": "p-value Analysis"}, {"name": "Bayes Theorem Application"}, {"name": "Normal Distribution"}]
            },
            {
                "code": "BDS-301",
                "name": "Data Visualization & EDA",
                "department": "B.Sc. Data Science",
                "semester": 3,
                "topics": ["Exploratory Data Analysis", "Seaborn Heatmaps", "Feature Outlier Detection"],
                "skills": [{"name": "Correlation Heatmaps"}, {"name": "Feature Skewness Removal"}, {"name": "Boxplot Outliers"}]
            },

            # M.Sc. Data Science
            {
                "code": "MDS-101",
                "name": "Machine Learning & Pattern Recognition",
                "department": "M.Sc. Data Science",
                "semester": 1,
                "topics": ["Supervised Classification", "Support Vector Machines", "Random Forest Ensembles"],
                "skills": [{"name": "Decision Tree Gini Impurity"}, {"name": "Hyperparameter Tuning"}, {"name": "ROC-AUC Curves"}]
            },
            {
                "code": "MDS-201",
                "name": "Deep Learning & Neural Networks",
                "department": "M.Sc. Data Science",
                "semester": 2,
                "topics": ["Convolutional Neural Networks", "Neural Decay Networks", "Recurrent Networks & Transformers"],
                "skills": [{"name": "Gradient Descent Rates"}, {"name": "Convolutional Feature Maps"}, {"name": "Attention Mechanism"}]
            },
            {
                "code": "MDS-301",
                "name": "Big Data Engineering (Spark/Hadoop)",
                "department": "M.Sc. Data Science",
                "semester": 3,
                "topics": ["PySpark RDD Transformations", "Distributed File Systems (HDFS)", "MapReduce Paradigms"],
                "skills": [{"name": "Spark Dataframe Aggregations"}, {"name": "MapReduce Jobs"}, {"name": "HDFS Block Replication"}]
            },

            # Computer Engineering
            {
                "code": "CE-101",
                "name": "Computer Organization & Architecture",
                "department": "Computer Engineering",
                "semester": 1,
                "topics": ["Instruction Set Architecture (ISA)", "CPU Pipelining & Hazards", "Cache Memory Mapping"],
                "skills": [{"name": "Cache Hit/Miss Rate"}, {"name": "Pipelining Stall Resolution"}, {"name": "Assembly Addressing Modes"}]
            },
            {
                "code": "CE-201",
                "name": "Operating Systems & Kernels",
                "department": "Computer Engineering",
                "semester": 2,
                "topics": ["Process Synchronization & Mutex", "Virtual Memory & Paging", "Deadlock Prevention"],
                "skills": [{"name": "Banker's Algorithm"}, {"name": "Page Replacement LRU"}, {"name": "Semaphore Locks"}]
            },
            {
                "code": "CE-301",
                "name": "Computer Networks & Security",
                "department": "Computer Engineering",
                "semester": 3,
                "topics": ["TCP/IP 4-Layer Architecture", "RSA Cryptography & Hashes", "Subnetting & IP Routing"],
                "skills": [{"name": "CIDR Subnet Masking"}, {"name": "RSA Public Key Encryption"}, {"name": "TCP 3-Way Handshake"}]
            }
        ]

        created_subjects = []
        created_skills = []

        for subj_data in subject_catalog:
            subj = db.query(Subject).filter((Subject.code == subj_data["code"]) | (Subject.name == subj_data["name"])).first()
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

            # Insert Topics for Subject
            from app.models.learning import Topic
            from app.core.enums import DifficultyLevel
            for t_idx, t_name in enumerate(subj_data.get("topics", [])):
                top = db.query(Topic).filter_by(subject_id=subj.id, name=t_name).first()
                if not top:
                    top = Topic(
                        id=str(uuid.uuid4()),
                        subject_id=subj.id,
                        name=t_name,
                        difficulty_level=DifficultyLevel.INTERMEDIATE,
                        order_index=t_idx
                    )
                    db.add(top)
                    db.commit()

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
