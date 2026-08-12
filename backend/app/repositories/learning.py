"""Learning repository module."""
from sqlalchemy.orm import Session
from sqlalchemy import select, asc
from typing import Any
from datetime import datetime, timezone
from app.repositories.base import BaseRepository
from app.models import Subject, Topic, Skill, TopicSkill, StudentSubject, FacultySubject, StudentSkill, LearningPreference
from app.core.enums import DifficultyLevel

class SubjectRepository(BaseRepository[Subject]):
    """Repository for Subject model."""
    
    def __init__(self) -> None:
        """Initialize with Subject model."""
        super().__init__(Subject)

    def get_by_code(self, db: Session, code: str) -> Subject | None:
        """Get subject by code."""
        stmt = select(Subject).where(Subject.code == code)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_category(self, db: Session, category: str, skip: int = 0, limit: int = 100) -> list[Subject]:
        """Get subjects by category."""
        stmt = select(Subject).where(Subject.category == category).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    get_multi_by_category = get_by_category

    def get_multi_with_count(self, db: Session, skip: int = 0, limit: int = 100) -> tuple[list[Subject], int]:
        """Get all subjects with count."""
        total_stmt = select(Subject)
        total = len(list(db.execute(total_stmt).scalars().all()))
        stmt = select(Subject).offset(skip).limit(limit)
        items = list(db.execute(stmt).scalars().all())
        return items, total

    def get_active_subjects(self, db: Session, skip: int = 0, limit: int = 100) -> list[Subject]:
        """Get active subjects."""
        stmt = select(Subject).where(Subject.is_active == True).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def search(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> list[Subject]:
        """Search subjects by name or code."""
        stmt = select(Subject).where(
            (Subject.name.ilike(f"%{query}%")) |
            (Subject.code.ilike(f"%{query}%"))
        ).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())


class TopicRepository(BaseRepository[Topic]):
    """Repository for Topic model."""
    
    def __init__(self) -> None:
        """Initialize with Topic model."""
        super().__init__(Topic)

    def get_by_subject(self, db: Session, subject_id: str, skip: int = 0, limit: int = 100) -> list[Topic]:
        """Get topics by subject ID."""
        stmt = select(Topic).where(Topic.subject_id == subject_id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    get_multi_by_subject = get_by_subject

    def get_by_difficulty(self, db: Session, difficulty: DifficultyLevel, skip: int = 0, limit: int = 100) -> list[Topic]:
        """Get topics by difficulty level."""
        stmt = select(Topic).where(Topic.difficulty == difficulty).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_ordered_by_subject(self, db: Session, subject_id: str) -> list[Topic]:
        """Get topics ordered by index for a subject."""
        stmt = select(Topic).where(Topic.subject_id == subject_id).order_by(asc(Topic.order_index))
        return list(db.execute(stmt).scalars().all())


class SkillRepository(BaseRepository[Skill]):
    """Repository for Skill model."""
    
    def __init__(self) -> None:
        """Initialize with Skill model."""
        super().__init__(Skill)

    def get_by_name(self, db: Session, name: str) -> Skill | None:
        """Get skill by name."""
        stmt = select(Skill).where(Skill.name == name)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_category(self, db: Session, category: str, skip: int = 0, limit: int = 100) -> list[Skill]:
        """Get skills by category."""
        stmt = select(Skill).where(Skill.category == category).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def search(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> list[Skill]:
        """Search skills by name."""
        stmt = select(Skill).where(Skill.name.ilike(f"%{query}%")).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())


class TopicSkillRepository(BaseRepository[TopicSkill]):
    """Repository for TopicSkill model."""
    
    def __init__(self) -> None:
        """Initialize with TopicSkill model."""
        super().__init__(TopicSkill)

    def get_by_topic(self, db: Session, topic_id: str) -> list[TopicSkill]:
        """Get skills mapped to a topic."""
        stmt = select(TopicSkill).where(TopicSkill.topic_id == topic_id)
        return list(db.execute(stmt).scalars().all())

    def get_by_skill(self, db: Session, skill_id: str) -> list[TopicSkill]:
        """Get topics mapped to a skill."""
        stmt = select(TopicSkill).where(TopicSkill.skill_id == skill_id)
        return list(db.execute(stmt).scalars().all())

    def get_by_topic_and_skill(self, db: Session, topic_id: str, skill_id: str) -> TopicSkill | None:
        """Get specific topic-skill mapping."""
        stmt = select(TopicSkill).where(TopicSkill.topic_id == topic_id, TopicSkill.skill_id == skill_id)
        return db.execute(stmt).scalar_one_or_none()


class StudentSubjectRepository(BaseRepository[StudentSubject]):
    """Repository for StudentSubject model."""
    
    def __init__(self) -> None:
        """Initialize with StudentSubject model."""
        super().__init__(StudentSubject)

    def get_by_student(self, db: Session, student_id: str) -> list[StudentSubject]:
        """Get subjects enrolled by a student."""
        stmt = select(StudentSubject).where(StudentSubject.student_id == student_id)
        return list(db.execute(stmt).scalars().all())

    get_multi_by_student_id = get_by_student

    def get_by_subject(self, db: Session, subject_id: str) -> list[StudentSubject]:
        """Get students enrolled in a subject."""
        stmt = select(StudentSubject).where(StudentSubject.subject_id == subject_id)
        return list(db.execute(stmt).scalars().all())

    def get_enrollment(self, db: Session, student_id: str, subject_id: str) -> StudentSubject | None:
        """Get specific enrollment."""
        stmt = select(StudentSubject).where(StudentSubject.student_id == student_id, StudentSubject.subject_id == subject_id)
        return db.execute(stmt).scalar_one_or_none()

    get_by_student_and_subject = get_enrollment

    def is_enrolled(self, db: Session, student_id: str, subject_id: str) -> bool:
        """Check if student is enrolled in subject."""
        return self.get_enrollment(db, student_id, subject_id) is not None


class FacultySubjectRepository(BaseRepository[FacultySubject]):
    """Repository for FacultySubject model."""
    
    def __init__(self) -> None:
        """Initialize with FacultySubject model."""
        super().__init__(FacultySubject)

    def get_by_faculty(self, db: Session, faculty_id: str) -> list[FacultySubject]:
        """Get subjects assigned to faculty."""
        stmt = select(FacultySubject).where(FacultySubject.faculty_id == faculty_id)
        return list(db.execute(stmt).scalars().all())

    def get_by_subject(self, db: Session, subject_id: str) -> list[FacultySubject]:
        """Get faculties teaching a subject."""
        stmt = select(FacultySubject).where(FacultySubject.subject_id == subject_id)
        return list(db.execute(stmt).scalars().all())


class StudentSkillRepository(BaseRepository[StudentSkill]):
    """Repository for StudentSkill model."""
    
    def __init__(self) -> None:
        """Initialize with StudentSkill model."""
        super().__init__(StudentSkill)

    def get_by_student(self, db: Session, student_id: str) -> list[StudentSkill]:
        """Get all skills of a student."""
        stmt = select(StudentSkill).where(StudentSkill.student_id == student_id)
        return list(db.execute(stmt).scalars().all())

    def get_by_skill(self, db: Session, skill_id: str) -> list[StudentSkill]:
        """Get all students possessing a skill."""
        stmt = select(StudentSkill).where(StudentSkill.skill_id == skill_id)
        return list(db.execute(stmt).scalars().all())

    def get_student_skill(self, db: Session, student_id: str, skill_id: str) -> StudentSkill | None:
        """Get specific student skill record."""
        stmt = select(StudentSkill).where(StudentSkill.student_id == student_id, StudentSkill.skill_id == skill_id)
        return db.execute(stmt).scalar_one_or_none()

    get_by_student_and_skill = get_student_skill

    def update_proficiency(self, db: Session, student_id: str, skill_id: str, is_correct: bool) -> StudentSkill | None:
        """Update student proficiency based on attempt."""
        student_skill = self.get_student_skill(db, student_id, skill_id)
        if not student_skill:
            student_skill = self.model(student_id=student_id, skill_id=skill_id, total_attempts=0, correct_attempts=0, proficiency_level=0.0)
            db.add(student_skill)
            
        student_skill.total_attempts += 1
        if is_correct:
            student_skill.correct_attempts += 1
            
        student_skill.proficiency_level = student_skill.correct_attempts / student_skill.total_attempts
        student_skill.last_practiced_at = datetime.now(timezone.utc)
        db.flush()
        return student_skill

    def get_weak_skills(self, db: Session, student_id: str, threshold: float = 0.5) -> list[StudentSkill]:
        """Get skills below proficiency threshold."""
        stmt = select(StudentSkill).where(StudentSkill.student_id == student_id, StudentSkill.proficiency_level < threshold)
        return list(db.execute(stmt).scalars().all())


class LearningPreferenceRepository(BaseRepository[LearningPreference]):
    """Repository for LearningPreference model."""
    
    def __init__(self) -> None:
        """Initialize with LearningPreference model."""
        super().__init__(LearningPreference)

    def get_by_student(self, db: Session, student_id: str) -> LearningPreference | None:
        """Get learning preferences for a student."""
        stmt = select(LearningPreference).where(LearningPreference.student_id == student_id)
        return db.execute(stmt).scalar_one_or_none()

    get_by_student_id = get_by_student

    def create_or_update(self, db: Session, student_id: str, **kwargs: Any) -> LearningPreference:
        """Create or update learning preferences."""
        pref = self.get_by_student(db, student_id)
        if pref:
            for key, value in kwargs.items():
                if value is not None and hasattr(pref, key):
                    setattr(pref, key, value)
        else:
            pref = self.model(student_id=student_id, **kwargs)
            db.add(pref)
        db.flush()
        return pref
