from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import datetime

from ..models.vpn_user import VPNUser
from ..schemas.vpn_user import VPNUserCreateRequestByAdmin # Used for input type hint
from ..schemas.plan import Plan as PlanSchema # To access plan details
from ..models.plan import Plan as PlanModel # To type hint plan_obj

class CRUDVPNUser:
    def get(self, db: Session, id: int) -> Optional[VPNUser]:
        return db.query(VPNUser).filter(VPNUser.id == id).first()

    def get_by_username(self, db: Session, username: str, admin_id: Optional[int] = None) -> Optional[VPNUser]:
        query = db.query(VPNUser).filter(VPNUser.username == username)
        if admin_id: # Check if username is unique for a specific admin
            query = query.filter(VPNUser.created_by_admin_id == admin_id)
        return query.first()

    def get_multi_by_admin(
        self, db: Session, *, admin_id: int, skip: int = 0, limit: int = 100
    ) -> List[VPNUser]:
        return (
            db.query(VPNUser)
            .filter(VPNUser.created_by_admin_id == admin_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[VPNUser]: # For superadmin or system use
        return db.query(VPNUser).offset(skip).limit(limit).all()

    def create_with_plan(
        self,
        db: Session,
        *,
        obj_in: VPNUserCreateRequestByAdmin, # Schema for data from admin
        admin_id: int,
        plan_obj: PlanModel # The actual Plan ORM object
    ) -> VPNUser:

        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=plan_obj.duration_days)

        db_obj = VPNUser(
            username=obj_in.username,
            created_by_admin_id=admin_id,
            plan_id=plan_obj.id,
            expires_at=expires_at,
            is_active=True, # Initially active, Marzban creation will confirm
            # marzban_user_id, abresani_user_id, subscription_link, qr_code_link will be updated after Marzban/Abresani interaction
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: VPNUser, obj_in: Dict[str, Any] # Accepts a dict for flexibility
    ) -> VPNUser:
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[VPNUser]:
        obj = db.query(VPNUser).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

vpn_user = CRUDVPNUser()
