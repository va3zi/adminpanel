from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Use this for standard login form
from sqlalchemy.orm import Session
from datetime import timedelta

from .... import schemas, models # Adjusted import path
from ....database import get_db
from ....security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_super_admin

router = APIRouter()

@router.post("/login/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    SuperAdmin login for token.
    Uses OAuth2PasswordRequestForm, so expects 'username' and 'password'
    in a form-data body.
    """
    super_admin = db.query(models.SuperAdmin).filter(models.SuperAdmin.username == form_data.username).first()
    if not super_admin or not verify_password(form_data.password, super_admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password for SuperAdmin",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": super_admin.username, "type": "super_admin"}, # "sub" is standard for subject (username)
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.SuperAdmin)
async def read_super_admin_me(
    current_super_admin: models.SuperAdmin = Depends(get_current_super_admin)
):
    """
    Get current logged-in SuperAdmin details.
    """
    return current_super_admin

# In a real application, you might also want:
# - Registration endpoint for the very first SuperAdmin (if not created by CLI/startup script)
# - Password recovery endpoints
# - Endpoint to change password
# - Endpoint to update SuperAdmin's own details

# For now, the initial SuperAdmin is created on startup (see main.py)
# if not found in .env variables.
# Additional SuperAdmins would typically not be created via an open API endpoint
# for security reasons, unless there's a specific multi-superadmin requirement
# managed by existing superadmins.
