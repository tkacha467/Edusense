"""Faculty service module."""
from typing import List
from sqlalchemy.orm import Session

from app.repositories import FacultyProfileRepository, FacultySubjectRepository
from app.models import FacultyProfile, FacultySubject
from app.core.exceptions import NotFoundException, ValidationException


class FacultyService:
    """Service for managing faculty profiles and their assigned subjects."""

    def __init__(self) -> None:
        """Initialize FacultyService with required repositories."""
        self.faculty_profile_repo = FacultyProfileRepository()
        self.faculty_subject_repo = FacultySubjectRepository()

    def get_profile(self, db: Session, faculty_id: str) -> FacultyProfile:
        """
        Retrieve a faculty profile by its ID.

        Args:
            db (Session): Database session.
            faculty_id (str): The unique identifier of the faculty profile.

        Returns:
            FacultyProfile: The faculty profile entity.

        Raises:
            NotFoundException: If the profile is not found.
        """
        profile = self.faculty_profile_repo.get_by_id(db, faculty_id)
        if not profile:
            raise NotFoundException(f"Faculty profile with ID '{faculty_id}' not found.")
        return profile

    def get_profile_by_user_id(self, db: Session, user_id: str) -> FacultyProfile:
        """
        Retrieve a faculty profile by the associated user's ID.

        Args:
            db (Session): Database session.
            user_id (str): The user ID associated with the profile.

        Returns:
            FacultyProfile: The faculty profile entity.

        Raises:
            NotFoundException: If the profile is not found.
        """
        profile = self.faculty_profile_repo.get_by_user_id(db, user_id=user_id)
        if not profile:
            raise NotFoundException(f"Faculty profile for user ID '{user_id}' not found.")
        return profile

    def update_profile(self, db: Session, faculty_id: str, **kwargs) -> FacultyProfile:
        """
        Update a faculty profile.

        Args:
            db (Session): Database session.
            faculty_id (str): The unique identifier of the faculty profile.
            **kwargs: Fields to update.

        Returns:
            FacultyProfile: The updated faculty profile entity.
        """
        profile = self.get_profile(db, faculty_id)
        return self.faculty_profile_repo.update(db, db_obj=profile, obj_in=kwargs)

    def assign_subjects(self, db: Session, faculty_id: str, subject_ids: List[str]) -> List[FacultySubject]:
        """
        Assign multiple subjects to a faculty member.

        Args:
            db (Session): Database session.
            faculty_id (str): The faculty profile ID.
            subject_ids (List[str]): A list of subject IDs to assign.

        Returns:
            List[FacultySubject]: A list of new assignment entities.
            
        Raises:
            NotFoundException: If the faculty profile does not exist.
        """
        # Ensure faculty exists
        self.get_profile(db, faculty_id)

        existing_assignments = self.get_assigned_subjects(db, faculty_id)
        assigned_subject_ids = {assignment.subject_id for assignment in existing_assignments}

        new_assignments = []
        for subject_id in subject_ids:
            if subject_id not in assigned_subject_ids:
                assignment = self.faculty_subject_repo.create(
                    db, obj_in={"faculty_id": faculty_id, "subject_id": subject_id}
                )
                new_assignments.append(assignment)

        return new_assignments

    def get_assigned_subjects(self, db: Session, faculty_id: str) -> List[FacultySubject]:
        """
        Retrieve a list of subjects assigned to the faculty member.

        Args:
            db (Session): Database session.
            faculty_id (str): The faculty profile ID.

        Returns:
            List[FacultySubject]: The list of faculty subject assignments.
        """
        return self.faculty_subject_repo.get_multi_by_faculty_id(db, faculty_id=faculty_id)

    def unassign_subject(self, db: Session, faculty_id: str, subject_id: str) -> bool:
        """
        Unassign a subject from a faculty member.

        Args:
            db (Session): Database session.
            faculty_id (str): The faculty profile ID.
            subject_id (str): The subject ID to unassign.

        Returns:
            bool: True if successfully unassigned.

        Raises:
            NotFoundException: If the assignment is not found.
        """
        assignment = self.faculty_subject_repo.get_by_faculty_and_subject(
            db, faculty_id=faculty_id, subject_id=subject_id
        )
        if not assignment:
            raise NotFoundException(f"Assignment for faculty '{faculty_id}' in subject '{subject_id}' not found.")
            
        self.faculty_subject_repo.delete(db, id=assignment.id)
        return True
