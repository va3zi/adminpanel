from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .... import schemas, models # Adjusted import path
from ....database import get_db
from ....security import get_current_super_admin # For protecting these routes

router = APIRouter()

# CRUD operations for Plans (to be performed by SuperAdmin)

@router.post("/", response_model=schemas.Plan, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan_in: schemas.PlanCreate,
    db: Session = Depends(get_db),
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin) # Protects endpoint
):
    """
    Create a new VPN Plan. Only accessible by SuperAdmins.
    """
    db_plan_by_name = db.query(models.Plan).filter(models.Plan.name == plan_in.name).first()
    if db_plan_by_name:
        raise HTTPException(status_code=400, detail=f"Plan with name '{plan_in.name}' already exists.")

    db_plan = models.Plan(**plan_in.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.get("/{plan_id}", response_model=schemas.Plan)
def read_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin) # Protects endpoint
):
    """
    Get a specific Plan by ID. Only accessible by SuperAdmins.
    """
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.get("/", response_model=List[schemas.Plan])
def read_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # No current_super_admin dependency here if plans are public to view by anyone,
    # or add it if only super admins can see all plans.
    # For now, let's assume only SuperAdmins list all plans via this specific admin endpoint.
    # Regular admins will have a different endpoint to see active plans.
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin)
):
    """
    Get a list of all Plans. Only accessible by SuperAdmins via this endpoint.
    """
    plans = db.query(models.Plan).offset(skip).limit(limit).all()
    return plans

@router.put("/{plan_id}", response_model=schemas.Plan)
def update_plan(
    plan_id: int,
    plan_in: schemas.PlanUpdate,
    db: Session = Depends(get_db),
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin) # Protects endpoint
):
    """
    Update a Plan's details. Only accessible by SuperAdmins.
    """
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    update_data = plan_in.dict(exclude_unset=True)

    if 'name' in update_data and update_data['name'] != db_plan.name:
        existing_plan = db.query(models.Plan).filter(models.Plan.name == update_data['name']).first()
        if existing_plan:
            raise HTTPException(status_code=400, detail=f"Plan with name '{update_data['name']}' already exists.")

    for field, value in update_data.items():
        setattr(db_plan, field, value)

    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.delete("/{plan_id}", response_model=schemas.Plan) # Or return a success message
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin) # Protects endpoint
):
    """
    Delete a Plan. Only accessible by SuperAdmins.
    Consider if this should be a soft delete (e.g., set is_active=False) or hard delete.
    For now, it's a hard delete. If plans are linked to existing users,
    this could cause issues or require a soft delete / deactivation instead.
    """
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Check if plan is in use before deleting?
    # For now, direct delete.
    # linked_vpn_users = db.query(models.VpnUser).filter(models.VpnUser.plan_id == plan_id).first()
    # if linked_vpn_users:
    #     raise HTTPException(status_code=400, detail="Cannot delete plan as it is currently linked to VPN users. Consider deactivating it instead.")

    db.delete(db_plan)
    db.commit()
    return db_plan # Or return {"message": "Plan deleted successfully"}
