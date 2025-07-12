from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .... import schemas, models # Adjusted import path
from ....database import get_db
from ....security import get_password_hash, get_current_super_admin # For protecting these routes

router = APIRouter()

# CRUD operations for Admins (to be performed by SuperAdmin)

@router.post("/", response_model=schemas.Admin, status_code=status.HTTP_201_CREATED)
def create_admin(
    admin_in: schemas.AdminCreate,
    db: Session = Depends(get_db),
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin) # Protects endpoint
):
    """
    Create a new Admin account. Only accessible by SuperAdmins.
    """
    db_admin_by_username = db.query(models.Admin).filter(models.Admin.username == admin_in.username).first()
    if db_admin_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_admin_by_email = db.query(models.Admin).filter(models.Admin.email == admin_in.email).first()
    if db_admin_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(admin_in.password)

    # Ensure created_by_super_admin_id is set if provided, otherwise it's null
    # Or, always set it to the current_super_admin.id
    db_admin = models.Admin(
        username=admin_in.username,
        email=admin_in.email,
        hashed_password=hashed_password,
        balance=admin_in.balance if admin_in.balance is not None else 0.0,
        is_active=admin_in.is_active if admin_in.is_active is not None else True,
        created_by_super_admin_id=current_super_admin.id # Associate with the creating SuperAdmin
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.get("/{admin_id}", response_model=schemas.Admin)
def read_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin) # Protects endpoint
):
    """
    Get a specific Admin by ID. Only accessible by SuperAdmins.
    """
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin

@router.get("/", response_model=List[schemas.Admin])
def read_admins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin) # Protects endpoint
):
    """
    Get a list of all Admins. Only accessible by SuperAdmins.
    """
    admins = db.query(models.Admin).offset(skip).limit(limit).all()
    return admins

@router.put("/{admin_id}", response_model=schemas.Admin)
def update_admin(
    admin_id: int,
    admin_in: schemas.AdminUpdate,
    db: Session = Depends(get_db),
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin) # Protects endpoint
):
    """
    Update an Admin's details. Only accessible by SuperAdmins.
    Password updates should be handled by a separate, dedicated endpoint if needed.
    """
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    update_data = admin_in.dict(exclude_unset=True)

    if 'username' in update_data and update_data['username'] != db_admin.username:
        existing_admin = db.query(models.Admin).filter(models.Admin.username == update_data['username']).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Username already taken")

    if 'email' in update_data and update_data['email'] != db_admin.email:
        existing_admin = db.query(models.Admin).filter(models.Admin.email == update_data['email']).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Email already taken")

    for field, value in update_data.items():
        setattr(db_admin, field, value)

    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.delete("/{admin_id}", response_model=schemas.Admin) # Or just return a success message
def delete_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin) # Protects endpoint
):
    """
    Delete an Admin account. Only accessible by SuperAdmins.
    Consider if this should be a soft delete (e.g., set is_active=False) or hard delete.
    For now, it's a hard delete.
    """
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Add any cascading delete logic or checks here if necessary
    # For example, what happens to VPN users owned by this admin?
    # This needs to be defined by business logic. For now, direct delete.

    db.delete(db_admin)
    db.commit()
    return db_admin # Or return {"message": "Admin deleted successfully"}


# TODO: Add endpoint for SuperAdmin to change an Admin's password if necessary.
# This requires careful consideration of security implications.
# Example:
# @router.put("/{admin_id}/change-password")
# def change_admin_password(...): ...
