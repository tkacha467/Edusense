"""Authentication and RBAC dependencies for FastAPI routers."""
from typing import Callable, List, Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole, UserStatus
from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.core.firebase import verify_firebase_token
from app.dependencies.database import get_db
from app.models.user import User
from app.models.student import StudentProfile
from app.repositories.user import UserRepository
from app.repositories.student import StudentProfileRepository
from app.repositories.permission import PermissionRepository

user_repo = UserRepository()
student_repo = StudentProfileRepository()


def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise UnauthorizedException("Authorization header is missing.")

    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("Invalid token scheme. Expected 'Bearer <token>'.")

    id_token = authorization.split("Bearer ")[1].strip()
    claims = verify_firebase_token(id_token)
    firebase_uid = claims.get("uid")

    if not firebase_uid:
        raise UnauthorizedException("Invalid token claims: Missing UID.")

    user = user_repo.get_by_firebase_uid(db, firebase_uid=firebase_uid)

    if not user:
        raise UnauthorizedException("Authenticated user record not found in database. Please register.")

    if user.is_deleted:
        raise ForbiddenException("Account has been deactivated or deleted.")

    if user.status != UserStatus.ACTIVE:
        if user.status == UserStatus.PENDING:
            raise ForbiddenException("Account is pending approval.")
        elif user.status == UserStatus.REJECTED:
            raise ForbiddenException("Account request was rejected.")
        elif user.status == UserStatus.SUSPENDED:
            raise ForbiddenException("Account is suspended.")
        else:
            raise ForbiddenException("Account is not active.")

    if not user.is_active:
        raise ForbiddenException("Account is currently inactive.")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency ensuring user account is active."""
    return current_user


def require_role(*allowed_roles: UserRole) -> Callable:
    """
    RBAC dependency factory that checks if the authenticated user
    possesses one of the specified allowed roles.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [role.value for role in allowed_roles] and current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Role '{current_user.role}' is not authorized to access this resource. Required: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker

def require_permission(*required_permissions: str) -> Callable:
    """
    RBAC dependency factory that checks if the authenticated user
    has the required permissions based on their role.
    """
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # SUPER_ADMIN bypasses permission checks
        if current_user.role == UserRole.SUPER_ADMIN or current_user.role == UserRole.SUPER_ADMIN.value:
            return current_user
            
        perm_repo = PermissionRepository(db)
        user_permissions = perm_repo.get_role_permissions(current_user.role)
        
        for perm in required_permissions:
            if perm not in user_permissions:
                raise ForbiddenException(
                    f"User role '{current_user.role}' does not have the required permission: '{perm}'."
                )
        return current_user

    return permission_checker

RequireAdmin = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
RequireSuperAdmin = require_role(UserRole.SUPER_ADMIN)
RequireFaculty = require_role(UserRole.FACULTY, UserRole.ADMIN, UserRole.SUPER_ADMIN)


def require_onboarding_completed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> StudentProfile:
    """
    Dependency ensuring the student has completed the onboarding flow.
    Returns the StudentProfile entity.
    """
    if current_user.role != UserRole.STUDENT.value and current_user.role != UserRole.STUDENT:
        raise ForbiddenException("Only student users have onboarding requirements.")

    profile = student_repo.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise NotFoundException("Student profile not found.")

    if not profile.onboarding_completed:
        raise ForbiddenException(
            "Student onboarding incomplete. Please complete onboarding at '/api/v1/onboarding' first."
        )

    return profile
