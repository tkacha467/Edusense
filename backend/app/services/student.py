"""Student service module."""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories import (
    StudentProfileRepository,
    LearningPreferenceRepository,
    StudentSubjectRepository,
    StudentSkillRepository,
)
from app.models import StudentProfile, LearningPreference, StudentSubject, StudentSkill
from app.core.exceptions import NotFoundException, ValidationException


class StudentService:
    """Service for managing student profiles, learning preferences, and subject enrollments."""

    def __init__(self) -> None:
        """Initialize StudentService with required repositories."""
        self.student_profile_repo = StudentProfileRepository()
        self.learning_pref_repo = LearningPreferenceRepository()
        self.student_subject_repo = StudentSubjectRepository()
        self.student_skill_repo = StudentSkillRepository()

    def get_profile(self, db: Session, student_id: str) -> StudentProfile:
        """
        Retrieve a student profile by its ID.

        Args:
            db (Session): Database session.
            student_id (str): The unique identifier of the student profile.

        Returns:
            StudentProfile: The student profile entity.

        Raises:
            NotFoundException: If the profile is not found.
        """
        profile = self.student_profile_repo.get_by_id(db, student_id)
        if not profile:
            raise NotFoundException(f"Student profile with ID '{student_id}' not found.")
        return profile

    def get_profile_by_user_id(self, db: Session, user_id: str) -> StudentProfile:
        """
        Retrieve a student profile by the associated user's ID.

        Args:
            db (Session): Database session.
            user_id (str): The user ID associated with the profile.

        Returns:
            StudentProfile: The student profile entity.

        Raises:
            NotFoundException: If the profile is not found.
        """
        profile = self.student_profile_repo.get_by_user_id(db, user_id=user_id)
        if not profile:
            raise NotFoundException(f"Student profile for user ID '{user_id}' not found.")
        return profile

    def update_profile(self, db: Session, student_id: str, **kwargs) -> StudentProfile:
        """
        Update a student profile.

        Args:
            db (Session): Database session.
            student_id (str): The unique identifier of the student profile.
            **kwargs: Fields to update.

        Returns:
            StudentProfile: The updated student profile entity.
        """
        profile = self.get_profile(db, student_id)
        return self.student_profile_repo.update(db, db_obj=profile, obj_in=kwargs)

    def complete_onboarding(self, db: Session, student_id: str) -> StudentProfile:
        """
        Mark the student's onboarding as complete.

        Args:
            db (Session): Database session.
            student_id (str): The unique identifier of the student profile.

        Returns:
            StudentProfile: The updated student profile.

        Raises:
            NotFoundException: If the profile does not exist.
        """
        # Business rule: verify profile exists
        profile = self.get_profile(db, student_id)
        return self.student_profile_repo.update(db, db_obj=profile, obj_in={"onboarding_completed": True})

    def set_learning_preferences(self, db: Session, student_id: str, **kwargs) -> LearningPreference:
        """
        Create or update the student's learning preferences.

        Args:
            db (Session): Database session.
            student_id (str): The student profile ID.
            **kwargs: Learning preference fields to set or update.

        Returns:
            LearningPreference: The updated or newly created preferences.
        """
        preferences = self.get_learning_preferences(db, student_id)
        if preferences:
            return self.learning_pref_repo.update(db, db_obj=preferences, obj_in=kwargs)
        
        # Create new preferences
        create_data = {"student_id": student_id, **kwargs}
        return self.learning_pref_repo.create(db, obj_in=create_data)

    def get_learning_preferences(self, db: Session, student_id: str) -> Optional[LearningPreference]:
        """
        Retrieve learning preferences for a student.

        Args:
            db (Session): Database session.
            student_id (str): The student profile ID.

        Returns:
            Optional[LearningPreference]: The learning preferences if they exist, else None.
        """
        return self.learning_pref_repo.get_by_student_id(db, student_id=student_id)

    def enroll_in_subjects(self, db: Session, student_id: str, subject_ids: List[str]) -> List[StudentSubject]:
        """
        Enroll a student in multiple subjects.

        Args:
            db (Session): Database session.
            student_id (str): The student profile ID.
            subject_ids (List[str]): A list of subject IDs to enroll the student in.

        Returns:
            List[StudentSubject]: A list of new enrollment entities.

        Raises:
            NotFoundException: If the student does not exist.
        """
        # Business rule: verify student exists
        self.get_profile(db, student_id)

        # Skip already-enrolled subjects
        existing_enrollments = self.get_enrolled_subjects(db, student_id)
        enrolled_subject_ids = {enrollment.subject_id for enrollment in existing_enrollments}

        new_enrollments = []
        for subject_id in subject_ids:
            if subject_id not in enrolled_subject_ids:
                # In a real app, verify subject exists here using SubjectRepository
                new_enrollment = self.student_subject_repo.create(
                    db, obj_in={"student_id": student_id, "subject_id": subject_id}
                )
                new_enrollments.append(new_enrollment)

        return new_enrollments

    def get_enrolled_subjects(self, db: Session, student_id: str) -> List[StudentSubject]:
        """
        Retrieve a list of subjects the student is enrolled in.

        Args:
            db (Session): Database session.
            student_id (str): The student profile ID.

        Returns:
            List[StudentSubject]: The list of student subject enrollments.
        """
        return self.student_subject_repo.get_multi_by_student_id(db, student_id=student_id)

    def unenroll_from_subject(self, db: Session, student_id: str, subject_id: str) -> bool:
        """
        Unenroll a student from a subject.

        Args:
            db (Session): Database session.
            student_id (str): The student profile ID.
            subject_id (str): The subject ID to unenroll from.

        Returns:
            bool: True if successfully unenrolled.

        Raises:
            NotFoundException: If the enrollment is not found.
        """
        enrollment = self.student_subject_repo.get_by_student_and_subject(
            db, student_id=student_id, subject_id=subject_id
        )
        if not enrollment:
            raise NotFoundException(f"Enrollment for student '{student_id}' in subject '{subject_id}' not found.")
            
        self.student_subject_repo.delete(db, id=enrollment.id)
        return True
