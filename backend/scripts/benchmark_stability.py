import sys
import os
import time
import random
import logging
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Import simulation methods so we don't duplicate code
from scripts.simulate_learner_journeys import (
    init_db, seed_curriculum, create_simulated_learners, 
    determine_correctness, get_engine
)
from app.database.session import get_db
from app.database.base import Base
from app.services.assessment import AssessmentService
from app.events.handlers import handle_assessment_completed
from app.core.enums import AssessmentDifficulty, QuestionDifficulty, GenerationMethod
from app.models import KnowledgeProfile, Recommendation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("BenchmarkStability")
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

def run_stability_test(seed: int, run_idx: int):
    # Set determinism
    random.seed(seed)
    
    # We use an entirely fresh DB per run to avoid side effects
    db_url = f"sqlite:///./stability_{run_idx}.db"
    os.environ["DATABASE_URL"] = db_url
    
    engine = init_db()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    try:
        subject, topic = seed_curriculum(db)
        # For stability test, just run 10 learners, 5 assessments each, to be quick but cover edges
        learners = create_simulated_learners(db, subject.id, count=10)
        
        assessment_service = AssessmentService()
        predictions_history = []
        
        assessments_per_learner = 5
        questions_per_assessment = 3
        
        for learner in learners:
            student_id = learner["student_id"]
            profile_type = learner["profile_type"]
            
            for attempt_idx in range(assessments_per_learner):
                session = assessment_service.create_assessment_session(
                    db=db, student_id=student_id, subject_id=subject.id, topic_id=topic.id,
                    title=f"Sim {attempt_idx}", difficulty=AssessmentDifficulty.INTERMEDIATE,
                    total_questions=questions_per_assessment, time_limit=300, generation_method=GenerationMethod.MANUAL
                )
                
                q_payload = []
                for _ in range(questions_per_assessment):
                    q_payload.append({
                        "topic_id": topic.id, "question_text": "Q", "question_type": "MCQ",
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
                        "time_taken_seconds": 15
                    })
                    
                result = assessment_service.submit_assessment(db, session.id, student_id, responses)
                db.commit()
                
                handle_assessment_completed(db, student_id=student_id, session_id=session.id, skill_updates=result.get("skill_updates", []))
                
                kp = db.query(KnowledgeProfile).filter_by(student_id=student_id).first()
                if kp:
                    predictions_history.append(kp.forgetting_probability)
                    
        return predictions_history
        
    finally:
        db.close()
        # Cleanup
        try:
            os.remove(f"./stability_{run_idx}.db")
        except:
            pass

if __name__ == "__main__":
    SEED = 42
    NUM_RUNS = 10
    
    print(f"Running Stability Test ({NUM_RUNS} runs, seed={SEED})")
    all_predictions = []
    
    for i in range(NUM_RUNS):
        print(f"Run {i+1}/{NUM_RUNS}...")
        preds = run_stability_test(SEED, i)
        all_predictions.append(preds)
        
    # Validation
    reference = all_predictions[0]
    is_stable = True
    
    for i in range(1, NUM_RUNS):
        if all_predictions[i] != reference:
            print(f"[FAILED] Run {i+1} diverged from reference!")
            is_stable = False
            
    if is_stable:
        print("[SUCCESS] Pipeline is strictly deterministic across 10 independent runs.")
    else:
        print("[FAILED] Non-determinism detected in ML pipeline or database.")
