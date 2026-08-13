import sys
import os
import time
import random
import uuid
import logging
import statistics
from datetime import datetime, timezone, timedelta
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from app.database.session import get_db, SessionLocal
from app.database.database import get_engine
from app.database.base import Base
from app.config import get_settings
from app.models import User, StudentProfile, Subject, Topic, Question, QuestionOption, StudentSubject, KnowledgeProfile, Notification, StudyPlan
from app.core.enums import UserRole, DifficultyLevel, AssessmentDifficulty, QuestionDifficulty, GenerationMethod
from app.services.assessment import AssessmentService
from app.events.handlers import handle_assessment_completed
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SystemAcceptance")
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

def init_db():
    engine = get_engine(get_settings())
    Base.metadata.create_all(bind=engine)
    return engine

def seed_curriculum(db: Session):
    subject = db.query(Subject).filter_by(code="CS101-SIM").first()
    if not subject:
        subject = Subject(id=str(uuid.uuid4()), name="Simulation CS", code="CS101-SIM", description="For testing")
        db.add(subject)
        
    topic = db.query(Topic).filter_by(subject_id=subject.id, name="Simulation Topic").first()
    if not topic:
        topic = Topic(id=str(uuid.uuid4()), subject_id=subject.id, name="Simulation Topic", description="Topic for sim", difficulty_level=DifficultyLevel.INTERMEDIATE)
        db.add(topic)
        
    db.commit()
    return subject, topic

def create_simulated_learners(db: Session, subject_id: str, count: int = 100):
    profiles = ["high_performer", "average", "struggling", "inactive", "improving", "declining"]
    learners = []
    
    for i in range(count):
        profile_type = profiles[i % len(profiles)]
        user = User(
            id=str(uuid.uuid4()), 
            firebase_uid=f"sim-user-{uuid.uuid4()}", 
            email=f"sim{uuid.uuid4()}@test.com", 
            display_name=f"Learner {i}", 
            role=UserRole.STUDENT, 
            is_active=True
        )
        db.add(user)
        db.flush()
        
        student = StudentProfile(id=str(uuid.uuid4()), user_id=user.id)
        db.add(student)
        db.flush()
        
        enrollment = StudentSubject(id=str(uuid.uuid4()), student_id=student.id, subject_id=subject_id, is_active=True)
        db.add(enrollment)
        
        learners.append({"student_id": student.id, "profile_type": profile_type})
        
    db.commit()
    return learners

def determine_correctness(profile_type: str, attempt_idx: int) -> bool:
    r = random.random()
    if profile_type == "high_performer": return r < 0.95
    elif profile_type == "struggling": return r < 0.30
    elif profile_type == "average": return r < min(0.40 + (attempt_idx * 0.05), 0.85)
    elif profile_type == "improving": return r < min(0.20 + (attempt_idx * 0.10), 0.90)
    elif profile_type == "declining": return r < max(0.90 - (attempt_idx * 0.08), 0.30)
    elif profile_type == "inactive": return r < 0.80
    return r < 0.50

def run_simulation():
    engine = init_db()
    db = next(get_db())
    
    try:
        subject, topic = seed_curriculum(db)
        learners = create_simulated_learners(db, subject.id, count=100)
        
        assessment_service = AssessmentService()
        
        metrics = {
            "assessments_created": 0,
            "questions_answered": 0,
            "latency_assessment_submit": [],
            "latency_adaptive_loop": [],
            "exceptions": 0,
            "rollbacks": 0
        }
        
        assessments_per_learner = 6
        questions_per_assessment = 5
        
        for learner in learners:
            student_id = learner["student_id"]
            profile_type = learner["profile_type"]
            
            for attempt_idx in range(assessments_per_learner):
                try:
                    session = assessment_service.create_assessment_session(
                        db=db, student_id=student_id, subject_id=subject.id, topic_id=topic.id,
                        title=f"Sim Assessment {attempt_idx}", difficulty=AssessmentDifficulty.INTERMEDIATE,
                        total_questions=questions_per_assessment, time_limit=300, generation_method=GenerationMethod.MANUAL
                    )
                    
                    q_payload = []
                    for _ in range(questions_per_assessment):
                        q_payload.append({
                            "topic_id": topic.id, "question_text": "Simulated question", "question_type": "MCQ",
                            "difficulty_level": QuestionDifficulty.MEDIUM, "marks": 1.0,
                            "correct_answer": "Correct", "options": [
                                {"option_text": "Correct", "is_correct": True, "order_index": 0, "option_label": "A"},
                                {"option_text": "Wrong", "is_correct": False, "order_index": 1, "option_label": "B"}
                            ]
                        })
                    
                    db_qs = assessment_service.add_questions_to_session(db, session.id, q_payload)
                    assessment_service.start_assessment(db, session.id, student_id)
                    
                    responses = []
                    for q in db_qs:
                        is_correct = determine_correctness(profile_type, attempt_idx)
                        correct_opt = next((o for o in q.options if o.is_correct), None)
                        wrong_opt = next((o for o in q.options if not o.is_correct), None)
                        selected_opt = correct_opt if is_correct else wrong_opt
                        responses.append({
                            "question_id": q.id, "selected_option_id": selected_opt.id if selected_opt else None,
                            "time_taken_seconds": random.randint(5, 45)
                        })
                    
                    t0 = time.perf_counter()
                    result = assessment_service.submit_assessment(db, session.id, student_id, responses)
                    db.commit()
                    t1 = time.perf_counter()
                    
                    metrics["latency_assessment_submit"].append((t1 - t0) * 1000)
                    metrics["assessments_created"] += 1
                    metrics["questions_answered"] += len(responses)
                    
                    if profile_type == "inactive" and attempt_idx == assessments_per_learner - 1:
                        kp = db.query(KnowledgeProfile).filter_by(student_id=student_id).first()
                        if kp:
                            kp.last_practiced_at = datetime.now(timezone.utc) - timedelta(days=30)
                            db.commit()
                    
                    t2 = time.perf_counter()
                    handle_assessment_completed(db, student_id=student_id, session_id=session.id, skill_updates=result.get("skill_updates", []))
                    t3 = time.perf_counter()
                    
                    metrics["latency_adaptive_loop"].append((t3 - t2) * 1000)
                    
                except Exception as e:
                    db.rollback()
                    metrics["exceptions"] += 1
                    metrics["rollbacks"] += 1
                    logger.error(f"Error processing learner {student_id}, attempt {attempt_idx}: {e}")
                    
        # Calculate Percentiles
        submit_lats = sorted(metrics["latency_assessment_submit"])
        loop_lats = sorted(metrics["latency_adaptive_loop"])
        
        def p(lats, perc): return lats[int(len(lats) * perc)]
        
        print("\n" + "="*50)
        print("SYSTEM ACCEPTANCE VALIDATION - PHASE 0D")
        print("="*50)
        print(f"Total Learners: {len(learners)}")
        print(f"Total Assessments: {metrics['assessments_created']}")
        print(f"Total Questions Answered: {metrics['questions_answered']}")
        print(f"Exceptions: {metrics['exceptions']}")
        print(f"Database Rollbacks: {metrics['rollbacks']}")
        print("-" * 50)
        print("LATENCY METRICS (ms)")
        print(f"Assessment Submit | Avg: {statistics.mean(submit_lats):.2f} | Med: {statistics.median(submit_lats):.2f} | P95: {p(submit_lats, 0.95):.2f} | P99: {p(submit_lats, 0.99):.2f} | Max: {max(submit_lats):.2f}")
        print(f"Adaptive Loop     | Avg: {statistics.mean(loop_lats):.2f} | Med: {statistics.median(loop_lats):.2f} | P95: {p(loop_lats, 0.95):.2f} | P99: {p(loop_lats, 0.99):.2f} | Max: {max(loop_lats):.2f}")
        
        # Validation checks
        print("-" * 50)
        print("Validating Knowledge Profiles consistency...")
        
        validation_failures = 0
        for learner in learners:
            student_id = learner["student_id"]
            profile_type = learner["profile_type"]
            
            kp = db.query(KnowledgeProfile).filter_by(student_id=student_id).first()
            if not kp: continue
            
            if kp.mastery_level > 0.8 and kp.forgetting_probability > 0.6:
                time_since = (datetime.now(timezone.utc) - kp.last_practiced_at).days
                if time_since < 10:
                    validation_failures += 1
            
            # Logic bounds
            if profile_type == "high_performer" and kp.forgetting_probability > 0.5:
                validation_failures += 1
            elif profile_type == "inactive" and kp.forgetting_probability < 0.6:
                validation_failures += 1
            elif profile_type == "struggling" and kp.forgetting_probability < 0.4:
                validation_failures += 1
                
        print(f"Profile Inconsistencies Found: {validation_failures}")
        
        if metrics["exceptions"] == 0 and validation_failures == 0 and p(loop_lats, 0.5) < 500:
            print("\n[SUCCESS] SYSTEM ACCEPTANCE CRITERIA MET.")
        else:
            print("\n[FAILED] System acceptance criteria not met.")

    finally:
        db.close()

if __name__ == "__main__":
    run_simulation()
