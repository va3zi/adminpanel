from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import crud
from ...schemas import PlanCreate, PlanPublic, PlanUpdate
from ...models import SuperAdmin as SuperAdminModel # For type hinting current_super_admin
from ...models import Admin as AdminModel # For type hinting current_admin
from .. import deps

router = APIRouter()

# Endpoints for SuperAdmins to manage plans
@router.post("/", response_model=PlanPublic, status_code=status.HTTP_201_CREATED)
async def create_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_in: PlanCreate,
    current_super_admin: SuperAdminModel = Depends(deps.get_current_active_super_admin_user)
) -> Any:
    """
    Create a new VPN plan (SuperAdmin only).
    """
    existing_plan = crud.plan.get_by_name(db, name=plan_in.name)
    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan with name '{plan_in.name}' already exists.",
        )
    plan = crud.plan.create(db=db, obj_in=plan_in)
    return plan

@router.put("/{plan_id}", response_model=PlanPublic)
async def update_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_id: int,
    plan_in: PlanUpdate,
    current_super_admin: SuperAdminModel = Depends(deps.get_current_active_super_admin_user)
) -> Any:
    """
    Update an existing VPN plan (SuperAdmin only).
    """
    db_plan = crud.plan.get(db, id=plan_id)
    if not db_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    # Check if new name conflicts (if name is being changed)
    if plan_in.name and plan_in.name != db_plan.name:
        existing_plan_with_new_name = crud.plan.get_by_name(db, name=plan_in.name)
        if existing_plan_with_new_name and existing_plan_with_new_name.id != plan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Another plan with name '{plan_in.name}' already exists.",
            )

    plan = crud.plan.update(db=db, db_obj=db_plan, obj_in=plan_in)
    return plan

@router.get("/{plan_id}", response_model=PlanPublic)
async def read_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_id: int,
    # Accessible by both SuperAdmins and Admins
    # No specific dependency for current_user here, public read or check if user is authenticated at all
    # For now, let's make it SuperAdmin only for consistency, Admins will use the list endpoint.
    current_super_admin: SuperAdminModel = Depends(deps.get_current_active_super_admin_user)
) -> Any:
    """
    Get a specific plan by ID (SuperAdmin only for this specific endpoint).
    Admins will use the /list-for-admin endpoint.
    """
    plan = crud.plan.get(db, id=plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan

@router.delete("/{plan_id}", response_model=PlanPublic)
async def delete_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_id: int,
    current_super_admin: SuperAdminModel = Depends(deps.get_current_active_super_admin_user)
) -> Any:
    """
    Delete a plan (SuperAdmin only).
    """
    plan = crud.plan.get(db, id=plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    # The FK on VPNUser.plan_id is RESTRICT, so DB will prevent deletion if users exist.
    # crud.plan.remove will attempt delete and DB will raise error if constrained.
    # Catching that IntegrityError would be good practice here.
    try:
        deleted_plan = crud.plan.remove(db=db, id=plan_id)
    except Exception as e: # Catch potential IntegrityError from DB
        # A more specific exception catch for sqlalchemy.exc.IntegrityError would be better
        # For now, a generic catch.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete plan. It might be in use by existing VPN users. Error: {e}",
        )
    if not deleted_plan: # Should not happen if get() found it, but as a safeguard
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found for deletion")
    return deleted_plan


# Endpoint for Admins to list available (active) plans
@router.get("/list-for-admin/", response_model=List[PlanPublic])
async def list_plans_for_admin(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: AdminModel = Depends(deps.get_current_active_admin_user) # Ensures only authenticated admins
) -> Any:
    """
    List available (active) VPN plans for Admins.
    """
    plans = crud.plan.get_multi(db, skip=skip, limit=limit, only_active=True)
    return plans


# Endpoint for SuperAdmins to list all plans (active and inactive)
@router.get("/list-for-superadmin/", response_model=List[PlanPublic])
async def list_plans_for_super_admin(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_super_admin: SuperAdminModel = Depends(deps.get_current_active_super_admin_user)
) -> Any:
    """
    List all VPN plans for SuperAdmins (both active and inactive).
    """
    plans = crud.plan.get_multi(db, skip=skip, limit=limit, only_active=False)
    return plans
