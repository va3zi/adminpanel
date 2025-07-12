from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # For form data login
from sqlalchemy.orm import Session
import timedelta # This was not imported, should be datetime.timedelta

from ... import crud
from ...schemas.token import Token, LoginRequest # LoginRequest for JSON body login
from ...schemas.admin import AdminPublic # To return admin details on login
from ...schemas.super_admin import SuperAdminPublic # To return super_admin details
from ...core import security
from ...core.config import settings # For token expiry, not directly used here but security module uses it
from .. import deps
import datetime # For timedelta

router = APIRouter()

@router.post("/login/admin", response_model=Token)
async def login_admin_for_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends() # Using form data for OAuth2 compatibility
):
    """
    OAuth2 compatible token login, get an access token for future requests (Admin).
    """
    admin_user = crud.admin.authenticate(db, username=form_data.username, password=form_data.password)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not crud.admin.is_active(admin_user):
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(admin_user.id), expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/superadmin", response_model=Token)
async def login_super_admin_for_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests (SuperAdmin).
    """
    # For super_admin, we need an authenticate method in crud_super_admin
    # Let's assume it's similar to admin.authenticate for now or create one.
    super_admin_user = crud.super_admin.authenticate(db, username=form_data.username, password=form_data.password)

    if not super_admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # SuperAdmins are implicitly active if they exist.

    access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(super_admin_user.id), expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Example of a test route requiring admin authentication
@router.get("/auth/me/admin", response_model=AdminPublic)
async def read_current_admin(
    current_admin: AdminPublic = Depends(deps.get_current_active_admin_user),
):
    """
    Get current authenticated admin.
    """
    return current_admin

# Example of a test route requiring super admin authentication
@router.get("/auth/me/superadmin", response_model=SuperAdminPublic)
async def read_current_super_admin(
    current_super_admin: SuperAdminPublic = Depends(deps.get_current_active_super_admin_user),
):
    """
    Get current authenticated super admin.
    """
    return current_super_admin
