from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.plan import Plan
from ..schemas.plan import PlanCreate, PlanUpdate

class CRUDPlan:
    def get(self, db: Session, id: int) -> Optional[Plan]:
        return db.query(Plan).filter(Plan.id == id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Plan]:
        return db.query(Plan).filter(Plan.name == name).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, only_active: bool = False
    ) -> List[Plan]:
        query = db.query(Plan)
        if only_active:
            query = query.filter(Plan.is_active == True)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: PlanCreate) -> Plan:
        db_obj = Plan(
            name=obj_in.name,
            duration_days=obj_in.duration_days,
            data_limit_gb=obj_in.data_limit_gb,
            price=obj_in.price,
            is_active=True # Default to active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Plan, obj_in: PlanUpdate
    ) -> Plan:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[Plan]:
        obj = db.query(Plan).get(id)
        if obj:
            # Consider if there are dependencies (e.g., VPNUsers on this plan)
            # The FK on VPNUser.plan_id is RESTRICT, so DB will prevent deletion if users exist.
            # Application logic could check this first.
            db.delete(obj)
            db.commit()
        return obj # Return the deleted object or None

plan = CRUDPlan()
