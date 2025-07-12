from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from .... import schemas, models
from ....database import get_db
from ....security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_admin # Use the admin-specific dependency
)

router = APIRouter()

@router.post("/login/token", response_model=schemas.Token)
async def login_admin_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Admin login for token.
    Uses OAuth2PasswordRequestForm, so expects 'username' and 'password'
    in a form-data body.
    """
    admin_user = db.query(models.Admin).filter(models.Admin.username == form_data.username).first()

    if not admin_user or not verify_password(form_data.password, admin_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password for Admin",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not admin_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # Or 403 Forbidden
            detail="Admin account is inactive.",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin_user.username, "type": "admin"}, # "sub" is standard, added "type"
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.Admin) # Use schemas.Admin for response
async def read_admin_me(
    current_admin: models.Admin = Depends(get_current_admin) # Protected by get_current_admin
):
    """
    Get current logged-in Admin details.
    """
    return current_admin
