import sys
import os
import json
import logging
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from app.database.session import get_db
from app.services.assessment import AssessmentService
from app.events.handlers import handle_assessment_completed
from app.models import User, StudentProfile, Subject, Topic, QuestionOption
from app.repositories.assessment import QuestionRepository, QuestionOptionRepository
from sqlalchemy.orm import Session
from app.core.enums import AssessmentStatus

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TraceAdaptiveLoop")

def generate_mock_data(db: Session):
    # Ensure there is a student, subject, and topic
    user = db.query(User).first()
    if not user:
        from app.core.enums import UserRole
        user = User(id=str(uuid.uuid4()), firebase_uid="mock-firebase-uid", email="test@trace.com", display_name="Trace Student", role=UserRole.STUDENT, is_active=True)
        db.add(user)
        db.flush()
        
    student = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if not student:
        student = StudentProfile(id=str(uuid.uuid4()), user_id=user.id)
        db.add(student)
        db.flush()
        
    subject = db.query(Subject).first()
    if not subject:
        subject = Subject(id=str(uuid.uuid4()), name="Computer Science", code="CS101", description="Intro to CS")
        db.add(subject)
        db.flush()
        
    topic = db.query(Topic).first()
    if not topic:
        from app.core.enums import DifficultyLevel
        topic = Topic(id=str(uuid.uuid4()), subject_id=subject.id, name="Data Structures", description="Arrays, Lists", difficulty_level=DifficultyLevel.INTERMEDIATE)
        db.add(topic)
        db.flush()
        
    from app.models import StudentSubject
    enrollment = db.query(StudentSubject).filter_by(student_id=student.id, subject_id=subject.id).first()
    if not enrollment:
        enrollment = StudentSubject(id=str(uuid.uuid4()), student_id=student.id, subject_id=subject.id, is_active=True)
        db.add(enrollment)
        db.flush()
        
    db.commit()
    return student, subject, topic

def trace_pipeline():
    logger.info("Starting Adaptive Loop Trace...")
    
    # Reproducibility info
    import app
    # Mocking commit hash / version
    logger.info(f"Reproducibility -> Model Version: v1.0.0, Seed: 42, Timestamp: {datetime.now(timezone.utc)}")

    db = next(get_db())
    
    # Ensure tables exist (for SQLite mock db if used)
    from app.database.database import get_engine
    from app.config import get_settings
    from app.database.base import Base
    
    engine = get_engine(get_settings())
    Base.metadata.create_all(bind=engine)
    
    try:
        student, subject, topic = generate_mock_data(db)
        
        assessment_service = AssessmentService()
        
        # 1. Create Assessment
        from app.core.enums import AssessmentDifficulty, QuestionDifficulty, GenerationMethod
        session = assessment_service.create_assessment_session(
            db=db,
            student_id=student.id,
            subject_id=subject.id,
            topic_id=topic.id,
            title="Trace Evaluation Assessment",
            difficulty=AssessmentDifficulty.INTERMEDIATE,
            total_questions=2,
            time_limit=300,
            generation_method=GenerationMethod.MANUAL
        )
        logger.info(f"Created Assessment Session: {session.id}")
        
        # 2. Add Questions
        questions_payload = [
            {
                "topic_id": topic.id,
                "question_text": "What is an array?",
                "question_type": "MCQ",
                "difficulty_level": QuestionDifficulty.EASY,
                "marks": 1.0,
                "correct_answer": "A contiguous block of memory",
                "options": [
                    {"option_text": "A contiguous block of memory", "is_correct": True, "order_index": 0, "option_label": "A"},
                    {"option_text": "A tree structure", "is_correct": False, "order_index": 1, "option_label": "B"}
                ]
            },
            {
                "topic_id": topic.id,
                "question_text": "What is a linked list?",
                "question_type": "MCQ",
                "difficulty_level": QuestionDifficulty.MEDIUM,
                "marks": 1.0,
                "correct_answer": "Node based sequence",
                "options": [
                    {"option_text": "Node based sequence", "is_correct": True, "order_index": 0, "option_label": "A"},
                    {"option_text": "Graph of nodes", "is_correct": False, "order_index": 1, "option_label": "B"}
                ]
            }
        ]
        
        questions = assessment_service.add_questions_to_session(db, session.id, questions_payload)
        logger.info(f"Added {len(questions)} questions.")
        
        # 3. Start Session
        assessment_service.start_assessment(db, session.id, student.id)
        
        # 4. Generate Responses (100% correct)
        responses = []
        for q in questions:
            correct_opt = db.query(QuestionOption).filter_by(question_id=q.id, is_correct=True).first()
            responses.append({
                "question_id": q.id,
                "selected_option_id": correct_opt.id,
                "time_taken_seconds": 10
            })
            
        logger.info(f"Submitting Responses: {json.dumps(responses)}")
        
        # 5. Submit Assessment (Simulating Router boundary)
        result = assessment_service.submit_assessment(db, session.id, student.id, responses)
        db.commit()
        logger.info(f"Assessment Submit Result: {result}")
        
        # 6. Execute Background Orchestrator
        skill_updates = result.get("skill_updates", [])
        
        # Inject Failure Condition for Testing Isolation
        # We will mock Timeline Service to throw an exception to see if it brings down the whole orchestrator.
        from app.services.adaptive.timeline import LearningTimelineService
        original_record = LearningTimelineService.record_event
        def mock_failing_record(*args, **kwargs):
            logger.warning("INJECTED FAILURE: TimelineService.record_event failed.")
            raise Exception("Simulated DB Connection Failure in TimelineService")
            
        LearningTimelineService.record_event = mock_failing_record
        
        try:
            logger.info("Triggering handle_assessment_completed...")
            handle_assessment_completed(db, student_id=student.id, session_id=session.id, skill_updates=skill_updates)
            # The exception should be caught and logged by handle_assessment_completed, preventing a crash.
        finally:
            # Restore
            LearningTimelineService.record_event = original_record

        logger.info("Trace Complete. Check database for Recommendation and Profile updates.")

    finally:
        db.close()

if __name__ == "__main__":
    trace_pipeline()
