from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import crud
from ...schemas.admin import AdminCreate, AdminPublic, AdminUpdate
from ...models.super_admin import SuperAdmin as SuperAdminModel # For type hinting current_user
from .. import deps

router = APIRouter()

@router.post("/", response_model=AdminPublic, status_code=status.HTTP_201_CREATED)
def create_admin_by_super_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: AdminCreate,
    current_super_admin: SuperAdminModel = Depends(deps.get_current_active_super_admin_user) # Ensure only super_admin can create
) -> Any:
    """
    Create new admin by a super admin.
    """
    # Check if admin with that username already exists
    existing_admin = crud.admin.get_by_username(db, username=admin_in.username)
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin with this username already exists.",
        )

    admin = crud.admin.create(db=db, obj_in=admin_in, created_by_super_admin_id=current_super_admin.id)
    return admin

@router.get("/{admin_id}", response_model=AdminPublic)
def read_admin_by_super_admin(
    admin_id: int,
    db: Session = Depends(deps.get_db),
    current_super_admin: SuperAdminModel = Depends(deps.get_current_active_super_admin_user)
) -> Any:
    """
    Get a specific admin by id (for super_admin).
    """
    admin = crud.admin.get(db, id=admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


@router.get("/", response_model=List[AdminPublic])
def read_admins_by_super_admin(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_super_admin: SuperAdminModel = Depends(deps.get_current_active_super_admin_user)
) -> Any:
    """
    Retrieve admins (for super_admin).
    """
    admins = crud.admin.get_multi(db, skip=skip, limit=limit)
    return admins


@router.put("/{admin_id}", response_model=AdminPublic)
def update_admin_by_super_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_id: int,
    admin_in: AdminUpdate,
    current_super_admin: SuperAdminModel = Depends(deps.get_current_active_super_admin_user)
) -> Any:
    """
    Update an admin (for super_admin).
    """
    admin = crud.admin.get(db=db, id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Admin not found",
        )
    admin = crud.admin.update(db=db, db_obj=admin, obj_in=admin_in)
    return admin

# TODO: Add endpoints for SuperAdmin to manage VPN plans (create, list, update, delete)
# This will be part of a different router, e.g., plans.py

# Endpoint for an Admin to view their own balance (as per step requirements)
# This could also go into a dedicated "me" router for admins or stay here for now.
@router.get("/me/balance", response_model=AdminPublic) # Reusing AdminPublic as it contains balance
def read_admin_me_balance(
    db: Session = Depends(deps.get_db),
    current_admin: AdminModel = Depends(deps.get_current_active_admin_user) # Admin model from deps
) -> Any:
    """
    Get current admin's own details including balance.
    """
    # current_admin is already the admin model instance from the dependency
    return current_admin
