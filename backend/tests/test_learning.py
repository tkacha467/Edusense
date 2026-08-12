"""Learning Taxonomy & Enrolment test suite."""
import pytest
from fastapi.testclient import TestClient
from app.models import User, Subject, Topic, Skill
from tests.fixtures.users import faculty_user, onboarded_student_user
from tests.fixtures.subjects import sample_subject, sample_topic
from tests.fixtures.skills import sample_skill


def test_list_subjects(client: TestClient, sample_subject: Subject, onboarded_student_user, make_auth_header):
    """Verify retrieving subjects catalogue."""
    headers = make_auth_header(onboarded_student_user.firebase_uid)
    res = client.get("/api/v1/learning/subjects", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["code"] == sample_subject.code


def test_create_topic_and_skill(client: TestClient, faculty_user: User, sample_subject: Subject):
    """Verify topic and skill creation by Faculty."""
    headers = {"Authorization": f"Bearer dev-token-{faculty_user.firebase_uid}"}

    # Create Topic
    res_topic = client.post("/api/v1/learning/topics", json={
        "subject_id": str(sample_subject.id),
        "name": "Graph Traversal",
        "difficulty_level": "intermediate",
        "description": "BFS and DFS algorithms",
        "order_index": 2
    }, headers=headers)
    assert res_topic.status_code == 201
    topic_id = res_topic.json()["id"]

    # Create Skill
    res_skill = client.post("/api/v1/learning/skills", json={
        "name": "Breadth-First Search",
        "description": "Queue-based traversal",
        "category": "Graph Algorithms"
    }, headers=headers)
    assert res_skill.status_code == 201


def test_get_subject_topics(client: TestClient, sample_subject: Subject, onboarded_student_user, make_auth_header, sample_topic: Topic):
    """Verify fetching topics for a subject."""
    headers = make_auth_header(onboarded_student_user.firebase_uid)
    res = client.get(f"/api/v1/learning/subjects/{sample_subject.id}/topics", headers=headers)
    assert res.status_code == 200
    topics = res.json()
    assert len(topics) >= 1
    assert topics[0]["name"] == sample_topic.name


def test_student_enrolment_and_unenrollment(client: TestClient, onboarded_student_user: User, sample_subject: Subject):
    """Verify student enrolment retrieval and unenrollment."""
    headers = {"Authorization": f"Bearer dev-token-{onboarded_student_user.firebase_uid}"}

    # Enroll
    client.post("/api/v1/onboarding/subjects", json={"subject_ids": [str(sample_subject.id)]}, headers=headers)

    # Get enrolled subjects
    res_enrolled = client.get("/api/v1/students/me/subjects", headers=headers)
    assert res_enrolled.status_code == 200

    # Unenroll
    res_unenroll = client.delete(f"/api/v1/students/me/subjects/{sample_subject.id}", headers=headers)
    assert res_unenroll.status_code == 204
