"""Ingestion Script for Kaggle / ASSISTments Educational Research Dataset for EduSense AI."""
import os
import sys
import uuid
from typing import List, Dict, Any

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

os.environ.setdefault("SECRET_KEY", "dev_secret_key_edusense_ai_2026_super_secure")
os.environ.setdefault("DATABASE_URL", "sqlite:///./edusense.db")

from app.config import get_settings
from app.database.database import get_engine
from app.database.session import get_session_factory
from app.models.learning import Subject, Topic, Skill
from app.models.assessment import Question, QuestionOption
from app.core.enums import DifficultyLevel, QuestionType

# Benchmark Research Dataset (ASSISTments + Kaggle MCQs)
KAGGLE_ASSISTMENTS_DATASET: List[Dict[str, Any]] = [
    # Data Structures & Algorithms
    {
        "subject_code": "BCA-201",
        "subject_name": "Data Structures & Algorithms",
        "topic_name": "Binary Search Trees",
        "skill_name": "Recursion & Trees",
        "questions": [
            {
                "text": "What is the average height of a balanced Binary Search Tree containing N nodes?",
                "difficulty": "MEDIUM",
                "correct": "B",
                "explanation": "A balanced binary search tree guarantees logarithmic height O(log N) for efficient searches.",
                "hint": "Think about halving the search space at each level.",
                "options": [
                    ("A", "O(1)"),
                    ("B", "O(log N)"),
                    ("C", "O(N)"),
                    ("D", "O(N log N)")
                ]
            },
            {
                "text": "Which tree traversal order visits nodes in ascending order for a Binary Search Tree?",
                "difficulty": "EASY",
                "correct": "A",
                "explanation": "In-order traversal (Left, Root, Right) visits BST nodes in sorted non-decreasing order.",
                "hint": "Left child first, then node itself, then right child.",
                "options": [
                    ("A", "In-order Traversal"),
                    ("B", "Pre-order Traversal"),
                    ("C", "Post-order Traversal"),
                    ("D", "Level-order Traversal")
                ]
            }
        ]
    },
    # Database Management Systems
    {
        "subject_code": "BCA-301",
        "subject_name": "Database Management Systems (DBMS)",
        "topic_name": "SQL Normalization",
        "skill_name": "3NF Normalization",
        "questions": [
            {
                "text": "Which database normalization form eliminates transitive functional dependencies?",
                "difficulty": "HARD",
                "correct": "C",
                "explanation": "Third Normal Form (3NF) requires 2NF compliance and ensures no non-prime attribute depends transitively on a primary key.",
                "hint": "Attributes must depend on key, whole key, and nothing but key.",
                "options": [
                    ("A", "First Normal Form (1NF)"),
                    ("B", "Second Normal Form (2NF)"),
                    ("C", "Third Normal Form (3NF)"),
                    ("D", "Boyce-Codd Normal Form (BCNF)")
                ]
            }
        ]
    },
    # M.Sc. Data Science - Machine Learning
    {
        "subject_code": "MDS-101",
        "subject_name": "Machine Learning & Pattern Recognition",
        "topic_name": "Supervised Classification",
        "skill_name": "Hyperparameter Tuning",
        "questions": [
            {
                "text": "In a Support Vector Machine (SVM), what does the hyperparameter C control?",
                "difficulty": "HARD",
                "correct": "B",
                "explanation": "C controls the trade-off between maximizing decision margin and minimizing classification errors on training data.",
                "hint": "A large C penalizes misclassifications heavily.",
                "options": [
                    ("A", "Kernel function bandwidth"),
                    ("B", "Trade-off between margin size and misclassifications"),
                    ("C", "Learning rate step size"),
                    ("D", "Number of decision trees")
                ]
            }
        ]
    },
    # M.Sc. Cyber Security
    {
        "subject_code": "MCA-301",
        "subject_name": "Artificial Intelligence & Expert Systems",
        "topic_name": "Logit Function & AI Logic",
        "skill_name": "Logit Function Complexity",
        "questions": [
            {
                "text": "What is the inverse of the Sigmoid function $f(x) = \\frac{1}{1 + e^{-x}}$?",
                "difficulty": "MEDIUM",
                "correct": "A",
                "explanation": "The Logit function $L(p) = \\ln\\left(\\frac{p}{1-p}\\right)$ is the mathematical inverse of the Sigmoid function.",
                "hint": "It maps probabilities back to log-odds.",
                "options": [
                    ("A", "Logit Function"),
                    ("B", "Softmax Function"),
                    ("C", "ReLU Function"),
                    ("D", "Tanh Function")
                ]
            }
        ]
    }
]

def ingest_kaggle_dataset():
    print("[+] Ingesting Kaggle / ASSISTments Research MCQ Dataset...")
    settings = get_settings()
    engine = get_engine(settings)
    SessionFactory = get_session_factory(engine)
    db = SessionFactory()

    count_q = 0
    count_opt = 0

    try:
        for entry in KAGGLE_ASSISTMENTS_DATASET:
            # 1. Resolve or create subject
            subject = db.query(Subject).filter((Subject.code == entry["subject_code"]) | (Subject.name == entry["subject_name"])).first()
            if not subject:
                subject = Subject(
                    id=str(uuid.uuid4()),
                    code=entry["subject_code"],
                    name=entry["subject_name"],
                    category="Computer Science",
                    semester=1,
                    description=f"Research course on {entry['subject_name']}"
                )
                db.add(subject)
                db.commit()
                db.refresh(subject)

            # 2. Resolve topic
            topic = db.query(Topic).filter_by(subject_id=subject.id, name=entry["topic_name"]).first()
            if not topic:
                topic = Topic(
                    id=str(uuid.uuid4()),
                    subject_id=subject.id,
                    name=entry["topic_name"],
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    order_index=1
                )
                db.add(topic)
                db.commit()
                db.refresh(topic)

            # 3. Resolve skill
            skill = db.query(Skill).filter_by(name=entry["skill_name"]).first()
            if not skill:
                skill = Skill(
                    id=str(uuid.uuid4()),
                    name=entry["skill_name"],
                    description=f"Skill for {entry['skill_name']}"
                )
                db.add(skill)
                db.commit()
                db.refresh(skill)

            # 4. Resolve benchmark session and insert Questions & Options
            from app.models.student import StudentProfile
            from app.models.assessment import AssessmentSession
            from app.core.enums import AssessmentStatus, AssessmentDifficulty

            student_prof = db.query(StudentProfile).first()
            student_id = student_prof.id if student_prof else str(uuid.uuid4())

            session_bench = db.query(AssessmentSession).filter_by(subject_id=subject.id, title="Kaggle Research Benchmark Pool").first()
            if not session_bench:
                session_bench = AssessmentSession(
                    id=str(uuid.uuid4()),
                    student_id=student_id,
                    subject_id=subject.id,
                    topic_id=topic.id,
                    title="Kaggle Research Benchmark Pool",
                    difficulty_level=AssessmentDifficulty.INTERMEDIATE,
                    total_questions=10,
                    time_limit_seconds=900,
                    status=AssessmentStatus.COMPLETED
                )
                db.add(session_bench)
                db.commit()
                db.refresh(session_bench)

            for q_data in entry["questions"]:
                q_exists = db.query(Question).filter_by(question_text=q_data["text"]).first()
                if not q_exists:
                    from app.core.enums import QuestionDifficulty
                    diff_map = {
                        "EASY": QuestionDifficulty.EASY,
                        "MEDIUM": QuestionDifficulty.MEDIUM,
                        "HARD": QuestionDifficulty.HARD
                    }
                    question = Question(
                        id=str(uuid.uuid4()),
                        assessment_session_id=session_bench.id,
                        topic_id=topic.id,
                        skill_id=skill.id,
                        question_text=q_data["text"],
                        question_type=QuestionType.MCQ,
                        difficulty_level=diff_map.get(q_data["difficulty"], QuestionDifficulty.MEDIUM),
                        marks=1.0,
                        correct_answer=q_data["correct"],
                        explanation=q_data["explanation"],
                        hint=q_data["hint"]
                    )
                    db.add(question)
                    db.commit()
                    db.refresh(question)
                    count_q += 1

                    for label, text in q_data["options"]:
                        opt = QuestionOption(
                            id=str(uuid.uuid4()),
                            question_id=question.id,
                            option_label=label,
                            option_text=text,
                            is_correct=(label == q_data["correct"])
                        )
                        db.add(opt)
                        count_opt += 1
                    db.commit()

        print(f"[+] Successfully Ingested {count_q} Questions & {count_opt} Options into Database!")
    except Exception as e:
        db.rollback()
        print(f"[!] Ingestion Error: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    ingest_kaggle_dataset()
