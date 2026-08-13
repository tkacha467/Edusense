"""User service module."""
from datetime import datetime, timezone
from typing import Tuple, List, Optional
from sqlalchemy.orm import Session

from app.repositories import UserRepository, StudentProfileRepository, FacultyProfileRepository
from app.models import User, StudentProfile, FacultyProfile
from app.core.exceptions import AlreadyExistsException, NotFoundException, ValidationException
from app.core.enums import UserRole


class UserService:
    """Service for managing user accounts, registration, and roles."""

    def __init__(self) -> None:
        """Initialize UserService with user, student, and faculty repositories."""
        self.user_repo = UserRepository()
        self.student_profile_repo = StudentProfileRepository()
        self.faculty_profile_repo = FacultyProfileRepository()

    def register_user(
        self,
        db: Session,
        firebase_uid: str,
        email: str,
        display_name: str,
        role: UserRole,
        avatar_url: Optional[str] = None,
        institution_id: Optional[str] = None,
        department_id: Optional[str] = None,
    ) -> User:
        """
        Register a new user and create their corresponding profile based on role.
        """
        from app.core.enums import UserStatus
        from app.services.faculty_request import FacultyRequestService
        from app.schemas.faculty_request import FacultyRequestCreate
        
        existing_uid = self.user_repo.get_by_firebase_uid(db, firebase_uid=firebase_uid)
        if existing_uid:
            return existing_uid

        # Business rules: Check email not taken
        if self.user_repo.get_by_email(db, email=email):
            raise AlreadyExistsException(f"User with email '{email}' already exists.")

        role_str = role.value if hasattr(role, "value") else str(role)
        is_faculty = (role_str == UserRole.FACULTY.value)
        
        # Create user
        user_data = {
            "firebase_uid": firebase_uid,
            "email": email,
            "display_name": display_name,
            "role": role,
            "avatar_url": avatar_url,
            "is_active": not is_faculty,
            "status": UserStatus.PENDING if is_faculty else UserStatus.ACTIVE,
        }
        user = self.user_repo.create(db, obj_in=user_data)
        
        if is_faculty:
            self.faculty_profile_repo.create(db, user_id=user.id)
            
            # Create FacultyRequest
            faculty_req_service = FacultyRequestService()
            req_data = FacultyRequestCreate(
                institution_id=institution_id,
                department_id=department_id
            )
            faculty_req_service.submit_request(db, user.id, req_data)
        elif role_str == UserRole.STUDENT.value:
            self.student_profile_repo.create(db, user_id=user.id)

        return user

    def get_user(self, db: Session, user_id: str) -> User:
        """
        Retrieve a user by their system ID.

        Args:
            db (Session): Database session.
            user_id (str): The internal UUID of the user.

        Returns:
            User: The user entity.

        Raises:
            NotFoundException: If the user is not found.
        """
        user = self.user_repo.get_by_id(db, user_id)
        if not user:
            raise NotFoundException(f"User with ID '{user_id}' not found.")
        return user

    def get_user_by_firebase_uid(self, db: Session, firebase_uid: str) -> User:
        """
        Retrieve a user by their Firebase UID.

        Args:
            db (Session): Database session.
            firebase_uid (str): The unique identifier from Firebase Auth.

        Returns:
            User: The user entity.

        Raises:
            NotFoundException: If the user is not found.
        """
        user = self.user_repo.get_by_firebase_uid(db, firebase_uid=firebase_uid)
        if not user:
            raise NotFoundException(f"User with Firebase UID '{firebase_uid}' not found.")
        return user

    def update_user(self, db: Session, user_id: str, **kwargs) -> User:
        """
        Update a user's details.

        Args:
            db (Session): Database session.
            user_id (str): The internal UUID of the user.
            **kwargs: The fields to update.

        Returns:
            User: The updated user entity.

        Raises:
            NotFoundException: If the user is not found.
        """
        user = self.get_user(db, user_id)
        return self.user_repo.update(db, db_obj=user, obj_in=kwargs)

    def deactivate_user(self, db: Session, user_id: str) -> User:
        """
        Soft delete a user by setting is_active=False and deleted_at to current UTC time.

        Args:
            db (Session): Database session.
            user_id (str): The internal UUID of the user.

        Returns:
            User: The updated (deactivated) user entity.
        """
        user = self.get_user(db, user_id)
        update_data = {
            "is_active": False,
            "deleted_at": datetime.now(timezone.utc)
        }
        return self.user_repo.update(db, db_obj=user, obj_in=update_data)

    def record_login(self, db: Session, user_id: str) -> User:
        """
        Update the last_login_at timestamp for a user.

        Args:
            db (Session): Database session.
            user_id (str): The internal UUID of the user.

        Returns:
            User: The updated user entity.
        """
        user = self.get_user(db, user_id)
        return self.user_repo.update(
            db, 
            db_obj=user, 
            obj_in={"last_login_at": datetime.now(timezone.utc)}
        )

    def get_users_by_role(
        self, 
        db: Session, 
        role: UserRole, 
        page: int = 1, 
        page_size: int = 100
    ) -> Tuple[List[User], int]:
        """
        Retrieve paginated users filtered by role.

        Args:
            db (Session): Database session.
            role (UserRole): The role to filter by.
            page (int): Page number (1-indexed).
            page_size (int): Number of items per page.

        Returns:
            Tuple[List[User], int]: A tuple containing the list of users and the total count.
        """
        skip = (page - 1) * page_size
        return self.user_repo.get_paginated(db, page=page, page_size=page_size, filters={"role": role})
