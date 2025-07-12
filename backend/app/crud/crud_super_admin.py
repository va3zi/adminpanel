from typing import Optional

from sqlalchemy.orm import Session

from ..models.super_admin import SuperAdmin
from ..schemas.super_admin import SuperAdminCreate
from ..core.security import get_password_hash, verify_password

class CRUDSuperAdmin:
    def get_by_username(self, db: Session, *, username: str) -> Optional[SuperAdmin]:
        return db.query(SuperAdmin).filter(SuperAdmin.username == username).first()

    def get(self, db: Session, id: int) -> Optional[SuperAdmin]:
        return db.query(SuperAdmin).filter(SuperAdmin.id == id).first()

    def create(self, db: Session, *, obj_in: SuperAdminCreate) -> SuperAdmin:
        db_obj = SuperAdmin(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # Add other methods like update, remove if super admins can be managed by other super admins
    # For now, assuming super admin is created via CLI or initial setup,
    # and this CRUD is mainly for fetching for login.
    # If we need an endpoint to create super_admins, this create() method will be used.

    def authenticate(
        self, db: Session, *, username: str, password: str
    ) -> Optional[SuperAdmin]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password): # Ensure verify_password is imported
            return None
        return user

super_admin = CRUDSuperAdmin()
