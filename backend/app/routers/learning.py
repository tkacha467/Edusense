"""Learning Taxonomy (Subjects, Topics, Skills) router."""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.dependencies.auth import get_current_user, require_role
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.learning import (
    SubjectCreate, SubjectResponse, SubjectUpdate,
    TopicCreate, TopicResponse, TopicUpdate,
    SkillCreate, SkillResponse, SkillUpdate,
    TopicSkillCreate, TopicSkillResponse
)
from app.services.learning import SubjectService, TopicService, SkillService

router = APIRouter(prefix="/learning", tags=["Learning Taxonomy"])

def get_subject_service() -> SubjectService: return SubjectService()
def get_topic_service() -> TopicService: return TopicService()
def get_skill_service() -> SkillService: return SkillService()


@router.get("/subjects", response_model=List[SubjectResponse])
def list_subjects(
    category: Optional[str] = Query(None, description="Filter subjects by category"),
    semester: Optional[int] = Query(None, description="Filter subjects by semester"),
    search: Optional[str] = Query(None, description="Search query for subject name or code"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    subject_service: SubjectService = Depends(get_subject_service)
) -> Any:
    """
    List all active subjects in the learning catalogue.
    """
    if search:
        subjects, _ = subject_service.search_subjects(db, query=search)
        return subjects
    if category:
        subjects, _ = subject_service.get_subjects_by_category(db, category=category)
        return subjects
    subjects, _ = subject_service.get_all_subjects(db, page=1, page_size=100)
    return subjects


@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_data: SubjectCreate,
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db),
    subject_service: SubjectService = Depends(get_subject_service)
) -> Any:
    """
    Create a new subject in the taxonomy catalogue (Faculty/Admin).
    """
    subject = subject_service.create_subject(
        db=db,
        name=subject_data.name,
        code=subject_data.code,
        description=subject_data.description,
        category=subject_data.category,
        semester=subject_data.semester
    )
    return subject


@router.get("/subjects/{subject_id}/topics", response_model=List[TopicResponse])
def get_subject_topics(
    subject_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    topic_service: TopicService = Depends(get_topic_service)
) -> Any:
    """
    Fetch all ordered topics associated with a given subject.
    """
    topics = topic_service.get_topics_by_subject(db, subject_id=subject_id)
    return topics


@router.post("/topics", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db),
    topic_service: TopicService = Depends(get_topic_service)
) -> Any:
    """
    Create a new topic within a subject (Faculty/Admin).
    """
    topic = topic_service.create_topic(
        db=db,
        subject_id=topic_data.subject_id,
        name=topic_data.name,
        difficulty_level=topic_data.difficulty_level,
        description=topic_data.description,
        order_index=topic_data.order_index
    )
    return topic


@router.get("/topics/{topic_id}/skills", response_model=List[TopicSkillResponse])
def get_topic_skills(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    """
    Fetch skills associated with a topic along with their relevance weights.
    """
    skills = skill_service.get_skills_for_topic(db, topic_id=topic_id)
    return skills


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(require_role(UserRole.FACULTY, UserRole.ADMIN)),
    db: Session = Depends(get_db),
    skill_service: SkillService = Depends(get_skill_service)
) -> Any:
    """
    Create a new granular skill entity (Faculty/Admin).
    """
    skill = skill_service.create_skill(
        db=db,
        name=skill_data.name,
        description=skill_data.description,
        category=skill_data.category
    )
    return skill
