"""Authentication and RBAC dependencies for FastAPI routers."""
from typing import Callable, List, Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.core.firebase import verify_firebase_token
from app.dependencies.database import get_db
from app.models.user import User
from app.models.student import StudentProfile
from app.repositories.user import UserRepository
from app.repositories.student import StudentProfileRepository

user_repo = UserRepository()
student_repo = StudentProfileRepository()


def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> User:
    print("\n" + "=" * 60)
    print("AUTH DEBUG")
    print("=" * 60)
    print(f"Raw Authorization Header : {repr(authorization)}")

    if authorization:
        print(f"Starts with 'Bearer '? : {authorization.startswith('Bearer ')}")

        try:
            id_token = authorization.split("Bearer ")[1].strip()
            print(f"Extracted Token         : {repr(id_token)}")

            from app.core.firebase import verify_firebase_token
            claims = verify_firebase_token(id_token)

            print(f"Decoded Claims          : {claims}")
            print(f"Extracted UID           : {claims.get('uid')}")

            from app.repositories.user import UserRepository
            repo = UserRepository()
            user = repo.get_by_firebase_uid(
                db,
                firebase_uid=claims.get("uid")
            )

            print(f"Database User Found     : {user is not None}")

            if user:
                print(f"Database User ID        : {user.id}")
                print(f"Database Firebase UID   : {user.firebase_uid}")
                print(f"Database Email          : {user.email}")

        except Exception as e:
            print(f"ERROR: {e}")

    print("=" * 60 + "\n")

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
