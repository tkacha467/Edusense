"""Learning taxonomy service module."""
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.repositories import (
    SubjectRepository, 
    TopicRepository, 
    TopicSkillRepository,
    SkillRepository
)
from app.models import Subject, Topic, Skill, TopicSkill
from app.core.exceptions import NotFoundException, ValidationException


class SubjectService:
    """Service for managing subjects in the learning taxonomy."""

    def __init__(self) -> None:
        """Initialize SubjectService with required repositories."""
        self.subject_repo = SubjectRepository()
        self.topic_repo = TopicRepository()

    def create_subject(self, db: Session, **kwargs) -> Subject:
        """
        Create a new subject.

        Args:
            db (Session): Database session.
            **kwargs: Subject fields.

        Returns:
            Subject: The newly created subject.
        """
        return self.subject_repo.create(db, obj_in=kwargs)

    def get_subject(self, db: Session, subject_id: str) -> Subject:
        """
        Retrieve a subject by its ID.

        Args:
            db (Session): Database session.
            subject_id (str): The unique identifier of the subject.

        Returns:
            Subject: The subject entity.

        Raises:
            NotFoundException: If the subject is not found.
        """
        subject = self.subject_repo.get_by_id(db, subject_id)
        if not subject:
            raise NotFoundException(f"Subject with ID '{subject_id}' not found.")
        return subject

    def get_all_subjects(self, db: Session, page: int = 1, page_size: int = 100) -> Tuple[List[Subject], int]:
        """
        Retrieve paginated subjects.

        Args:
            db (Session): Database session.
            page (int): Page number (1-indexed).
            page_size (int): Number of items per page.

        Returns:
            Tuple[List[Subject], int]: A tuple containing the list of subjects and the total count.
        """
        skip = (page - 1) * page_size
        return self.subject_repo.get_multi_with_count(db, skip=skip, limit=page_size)

    def update_subject(self, db: Session, subject_id: str, **kwargs) -> Subject:
        """
        Update a subject.

        Args:
            db (Session): Database session.
            subject_id (str): The unique identifier of the subject.
            **kwargs: Fields to update.

        Returns:
            Subject: The updated subject entity.
        """
        subject = self.get_subject(db, subject_id)
        return self.subject_repo.update(db, db_obj=subject, obj_in=kwargs)

    def search_subjects(self, db: Session, query: str, page: int = 1, page_size: int = 100) -> Tuple[List[Subject], int]:
        """
        Search for subjects by name or description.

        Args:
            db (Session): Database session.
            query (str): The search term.
            page (int): Page number.
            page_size (int): Items per page.

        Returns:
            Tuple[List[Subject], int]: List of matched subjects and total count.
        """
        skip = (page - 1) * page_size
        return self.subject_repo.search(db, query=query, skip=skip, limit=page_size)

    def get_subjects_by_category(self, db: Session, category: str, page: int = 1, page_size: int = 100) -> Tuple[List[Subject], int]:
        """
        Retrieve subjects filtered by a category.

        Args:
            db (Session): Database session.
            category (str): The category to filter by.
            page (int): Page number.
            page_size (int): Items per page.

        Returns:
            Tuple[List[Subject], int]: List of subjects in the category and total count.
        """
        skip = (page - 1) * page_size
        return self.subject_repo.get_by_category(db, category=category, skip=skip, limit=page_size)

    def get_subject_with_topics(self, db: Session, subject_id: str) -> Subject:
        """
        Retrieve a subject along with its associated topics.

        Args:
            db (Session): Database session.
            subject_id (str): The unique identifier of the subject.

        Returns:
            Subject: The subject entity with topics loaded.
        """
        subject = self.subject_repo.get_with_topics(db, id=subject_id)
        if not subject:
            raise NotFoundException(f"Subject with ID '{subject_id}' not found.")
        return subject


class TopicService:
    """Service for managing topics within subjects."""

    def __init__(self) -> None:
        """Initialize TopicService with required repositories."""
        self.topic_repo = TopicRepository()
        self.topic_skill_repo = TopicSkillRepository()

    def create_topic(self, db: Session, **kwargs) -> Topic:
        """
        Create a new topic.

        Args:
            db (Session): Database session.
            **kwargs: Topic fields including subject_id.

        Returns:
            Topic: The newly created topic.
        """
        return self.topic_repo.create(db, obj_in=kwargs)

    def get_topic(self, db: Session, topic_id: str) -> Topic:
        """
        Retrieve a topic by its ID.

        Args:
            db (Session): Database session.
            topic_id (str): The unique identifier of the topic.

        Returns:
            Topic: The topic entity.

        Raises:
            NotFoundException: If the topic is not found.
        """
        topic = self.topic_repo.get_by_id(db, topic_id)
        if not topic:
            raise NotFoundException(f"Topic with ID '{topic_id}' not found.")
        return topic

    def get_topics_by_subject(self, db: Session, subject_id: str) -> List[Topic]:
        """
        Retrieve all topics for a given subject.

        Args:
            db (Session): Database session.
            subject_id (str): The subject ID.

        Returns:
            List[Topic]: List of topics for the subject.
        """
        return self.topic_repo.get_multi_by_subject(db, subject_id=subject_id)

    def update_topic(self, db: Session, topic_id: str, **kwargs) -> Topic:
        """
        Update a topic.

        Args:
            db (Session): Database session.
            topic_id (str): The topic ID.
            **kwargs: Fields to update.

        Returns:
            Topic: The updated topic entity.
        """
        topic = self.get_topic(db, topic_id)
        return self.topic_repo.update(db, db_obj=topic, obj_in=kwargs)

    def reorder_topics(self, db: Session, subject_id: str, ordered_topic_ids: List[str]) -> bool:
        """
        Reorder topics within a subject.

        Args:
            db (Session): Database session.
            subject_id (str): The subject ID.
            ordered_topic_ids (List[str]): The new ordered list of topic IDs.

        Returns:
            bool: True if successful.
        """
        # Verify topics belong to subject and reorder
        for index, topic_id in enumerate(ordered_topic_ids):
            topic = self.get_topic(db, topic_id)
            if str(topic.subject_id) != str(subject_id):
                raise ValidationException(f"Topic {topic_id} does not belong to subject {subject_id}")
            self.topic_repo.update(db, db_obj=topic, obj_in={"order_index": index})
        return True

    def get_topic_with_skills(self, db: Session, topic_id: str) -> Topic:
        """
        Retrieve a topic along with its associated skills.

        Args:
            db (Session): Database session.
            topic_id (str): The unique identifier of the topic.

        Returns:
            Topic: The topic entity with skills loaded.
        """
        topic = self.topic_repo.get_with_skills(db, id=topic_id)
        if not topic:
            raise NotFoundException(f"Topic with ID '{topic_id}' not found.")
        return topic


class SkillService:
    """Service for managing individual skills and their associations with topics."""

    def __init__(self) -> None:
        """Initialize SkillService with required repositories."""
        self.skill_repo = SkillRepository()
        self.topic_skill_repo = TopicSkillRepository()

    def create_skill(self, db: Session, **kwargs) -> Skill:
        """
        Create a new skill.

        Args:
            db (Session): Database session.
            **kwargs: Skill fields.

        Returns:
            Skill: The newly created skill.
        """
        return self.skill_repo.create(db, obj_in=kwargs)

    def get_skill(self, db: Session, skill_id: str) -> Skill:
        """
        Retrieve a skill by its ID.

        Args:
            db (Session): Database session.
            skill_id (str): The unique identifier of the skill.

        Returns:
            Skill: The skill entity.

        Raises:
            NotFoundException: If the skill is not found.
        """
        skill = self.skill_repo.get_by_id(db, skill_id)
        if not skill:
            raise NotFoundException(f"Skill with ID '{skill_id}' not found.")
        return skill

    def get_all_skills(self, db: Session, page: int = 1, page_size: int = 100) -> Tuple[List[Skill], int]:
        """
        Retrieve paginated skills.

        Args:
            db (Session): Database session.
            page (int): Page number.
            page_size (int): Items per page.

        Returns:
            Tuple[List[Skill], int]: List of skills and total count.
        """
        skip = (page - 1) * page_size
        return self.skill_repo.get_multi_with_count(db, skip=skip, limit=page_size)

    def update_skill(self, db: Session, skill_id: str, **kwargs) -> Skill:
        """
        Update a skill.

        Args:
            db (Session): Database session.
            skill_id (str): The skill ID.
            **kwargs: Fields to update.

        Returns:
            Skill: The updated skill entity.
        """
        skill = self.get_skill(db, skill_id)
        return self.skill_repo.update(db, db_obj=skill, obj_in=kwargs)

    def search_skills(self, db: Session, query: str, page: int = 1, page_size: int = 100) -> Tuple[List[Skill], int]:
        """
        Search for skills by name or description.

        Args:
            db (Session): Database session.
            query (str): The search term.
            page (int): Page number.
            page_size (int): Items per page.

        Returns:
            Tuple[List[Skill], int]: List of matched skills and total count.
        """
        skip = (page - 1) * page_size
        return self.skill_repo.search(db, query=query, skip=skip, limit=page_size)

    def link_to_topic(self, db: Session, skill_id: str, topic_id: str) -> TopicSkill:
        """
        Link a skill to a topic.

        Args:
            db (Session): Database session.
            skill_id (str): The skill ID.
            topic_id (str): The topic ID.

        Returns:
            TopicSkill: The linking entity.
        """
        existing_link = self.topic_skill_repo.get_by_topic_and_skill(db, topic_id=topic_id, skill_id=skill_id)
        if existing_link:
            return existing_link

        return self.topic_skill_repo.create(db, obj_in={"topic_id": topic_id, "skill_id": skill_id})

    def unlink_from_topic(self, db: Session, skill_id: str, topic_id: str) -> bool:
        """
        Unlink a skill from a topic.

        Args:
            db (Session): Database session.
            skill_id (str): The skill ID.
            topic_id (str): The topic ID.

        Returns:
            bool: True if successfully unlinked.
        """
        link = self.topic_skill_repo.get_by_topic_and_skill(db, topic_id=topic_id, skill_id=skill_id)
        if not link:
            raise NotFoundException(f"Link between topic '{topic_id}' and skill '{skill_id}' not found.")
            
        self.topic_skill_repo.delete(db, id=link.id)
        return True

    def get_skills_for_topic(self, db: Session, topic_id: str) -> List[Skill]:
        """
        Retrieve all skills associated with a specific topic.

        Args:
            db (Session): Database session.
            topic_id (str): The topic ID.

        Returns:
            List[Skill]: List of skills linked to the topic.
        """
        links = self.topic_skill_repo.get_by_topic(db, topic_id=topic_id)
        # Assuming the repository loads the skill relationship or we fetch them
        # In an ideal repository, get_by_topic could return the Skill entities directly via join
        return [link.skill for link in links]
