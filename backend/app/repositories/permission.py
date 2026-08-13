"""Permission repository."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.permission import Permission, RolePermission
from app.core.enums import UserRole

class PermissionRepository:
    """Repository for managing Role Permissions."""

    def __init__(self, db: Session):
        self.db = db

    def get_role_permissions(self, role: UserRole) -> List[str]:
        """Get all permission codes for a specific role."""
        role_permissions = self.db.query(RolePermission).options(joinedload(RolePermission.permission)).filter(RolePermission.role == role).all()
        return [rp.permission.code for rp.permission in role_permissions]

    def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """Get a permission by its code."""
        return self.db.query(Permission).filter(Permission.code == code).first()

    def add_permission_to_role(self, role: UserRole, permission_id: str) -> RolePermission:
        """Assign a permission to a role."""
        role_perm = RolePermission(role=role, permission_id=permission_id)
        self.db.add(role_perm)
        self.db.commit()
        self.db.refresh(role_perm)
        return role_perm
