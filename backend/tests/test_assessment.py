"""Assessment Engine & Auto-Evaluation test suite."""
import pytest
from fastapi.testclient import TestClient
from app.models import User, Subject, Topic, AssessmentSession
from tests.fixtures.users import onboarded_student_user
from tests.fixtures.subjects import sample_subject, sample_topic, enrolled_student
from tests.fixtures.skills import sample_skill
from tests.fixtures.assessment import sample_assessment_session, session_with_questions


def test_generate_assessment_session(client: TestClient, enrolled_student: User, sample_subject: Subject, sample_topic: Topic):
    """Verify assessment generation via AI Gateway Provider."""
    headers = {"Authorization": f"Bearer dev-token-{enrolled_student.firebase_uid}"}
    payload = {
        "subject_id": str(sample_subject.id),
        "topic_id": str(sample_topic.id),
        "title": "Data Structures Test Quiz",
        "difficulty_level": "intermediate",
        "total_questions": 2,
        "time_limit_seconds": 600,
        "generation_method": "ai"
    }
    res = client.post("/api/v1/assessments/generate", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "pending"
    assert len(data["questions"]) == 2


def test_get_public_questions_masks_answers(client: TestClient, enrolled_student: User, session_with_questions: AssessmentSession):
    """Verify fetching test questions conceals correct answers from student."""
    headers = {"Authorization": f"Bearer dev-token-{enrolled_student.firebase_uid}"}
    res = client.get(f"/api/v1/assessments/{session_with_questions.id}/questions", headers=headers)
    assert res.status_code == 200
    questions = res.json()
    assert len(questions) == 2

    # Assert correct answer is hidden in public options
    first_opt = questions[0]["options"][0]
    assert "is_correct" not in first_opt


def test_start_assessment_session(client: TestClient, enrolled_student: User, session_with_questions: AssessmentSession):
    """Verify starting an assessment sets IN_PROGRESS status."""
    headers = {"Authorization": f"Bearer dev-token-{enrolled_student.firebase_uid}"}
    res = client.post(f"/api/v1/assessments/{session_with_questions.id}/start", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"


def test_submit_assessment_auto_grading(client: TestClient, enrolled_student: User, session_with_questions: AssessmentSession):
    """Verify submitting answers evaluates score, percentage, and updates session status."""
    headers = {"Authorization": f"Bearer dev-token-{enrolled_student.firebase_uid}"}

    # Start session first
    client.post(f"/api/v1/assessments/{session_with_questions.id}/start", headers=headers)

    # Fetch public questions to get option IDs
    q_res = client.get(f"/api/v1/assessments/{session_with_questions.id}/questions", headers=headers)
    questions = q_res.json()

    # Find correct options (Option B for Q1, Option A for Q2 based on fixture)
    q1_opt_correct = next(opt["id"] for opt in questions[0]["options"] if opt["option_label"] == "B")
    q2_opt_correct = next(opt["id"] for opt in questions[1]["options"] if opt["option_label"] == "A")

    submission_payload = {
        "responses": [
            {"question_id": questions[0]["id"], "selected_option_id": q1_opt_correct, "time_taken_seconds": 25},
            {"question_id": questions[1]["id"], "selected_option_id": q2_opt_correct, "time_taken_seconds": 30}
        ]
    }

    res_sub = client.post(f"/api/v1/assessments/{session_with_questions.id}/submit", json=submission_payload, headers=headers)
    assert res_sub.status_code == 200
    result = res_sub.json()

    assert result["total_questions"] == 2
    assert result["correct_answers"] == 2
    assert result["scored_marks"] == 2.0
    assert result["percentage"] == 100.0


def test_get_assessment_history(client: TestClient, enrolled_student: User):
    """Verify fetching student assessment history."""
    headers = {"Authorization": f"Bearer dev-token-{enrolled_student.firebase_uid}"}
    res = client.get("/api/v1/assessments/history", headers=headers)
    assert res.status_code == 200
    assert "items" in res.json()
