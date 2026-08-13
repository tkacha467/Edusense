import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.core.enums import UserRole, UserStatus

def create_super_admin():
    db = next(get_db())
    try:
        # Check if any SUPER_ADMIN exists
        admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
        if admin:
            print(f"Super admin already exists: {admin.email}")
            return
        
        firebase_uid = "uid_admin_edusense_com"
        
        user = User(
            firebase_uid=firebase_uid,
            email="admin@edusense.com",
            display_name="Master Admin",
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True
        )
        db.add(user)
        db.commit()
        print("Created Super Admin user: admin@edusense.com")
    finally:
        db.close()

if __name__ == "__main__":
    create_super_admin()
