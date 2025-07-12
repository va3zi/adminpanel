from typing import Optional, List, Any

from sqlalchemy.orm import Session

from ..models.admin import Admin
from ..schemas.admin import AdminCreate, AdminUpdate # Assuming AdminUpdate might be used
from ..core.security import get_password_hash, verify_password # verify_password for auth

class CRUDAdmin:
    def get_by_username(self, db: Session, *, username: str) -> Optional[Admin]:
        return db.query(Admin).filter(Admin.username == username).first()

    def get(self, db: Session, *, id: int) -> Optional[Admin]:
        return db.query(Admin).filter(Admin.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Admin]:
        return db.query(Admin).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: AdminCreate, created_by_super_admin_id: Optional[int] = None) -> Admin:
        db_obj = Admin(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            is_active=True, # Admins created are active by default
            created_by_super_admin_id=created_by_super_admin_id
            # Balance defaults to 0.00 as per model
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Admin, obj_in: AdminUpdate # or Dict[str, Any]
    ) -> Admin:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) # Pydantic v2

        # Password update should be handled separately if needed, e.g. new field in AdminUpdate
        # For now, AdminUpdate doesn't include password.
        # if "password" in update_data and update_data["password"]:
        #     hashed_password = get_password_hash(update_data["password"])
        #     del update_data["password"] # remove plain password
        #     update_data["hashed_password"] = hashed_password

        # Manual update:
        for field_name, value in update_data.items():
            if hasattr(db_obj, field_name):
                setattr(db_obj, field_name, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(
        self, db: Session, *, username: str, password: str
    ) -> Optional[Admin]:
        admin_user = self.get_by_username(db, username=username)
        if not admin_user:
            return None
        if not verify_password(password, admin_user.hashed_password):
            return None
        return admin_user

    def is_active(self, admin_user: Admin) -> bool:
        return admin_user.is_active

admin = CRUDAdmin()
