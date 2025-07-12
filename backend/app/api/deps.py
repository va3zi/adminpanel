from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from ..db.session import SessionLocal # Will create this later
from ..core import security
from ..core.config import settings
from ..schemas.token import TokenPayload
from ..models.admin import Admin as AdminModel
from ..models.super_admin import SuperAdmin as SuperAdminModel
from ..crud import crud_admin, crud_super_admin


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/admin" # Example: admin login
)

reusable_oauth2_super_admin = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/superadmin" # Example: superadmin login
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user_abstract(
    db: Session, token: str, user_type: str, crud_module: Any
) -> Any: # Return type can be AdminModel or SuperAdminModel
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_token(token)
        if payload is None or payload.sub is None: # Check payload and payload.sub
            raise credentials_exception

        # Assuming sub contains the username or ID prefixed with type, e.g., "admin:<id>" or "super:<id>"
        # Or more simply, if token subject is just the ID as a string

        # For simplicity, let's assume 'sub' is the user_id (integer after validation)
        # and token type is implicitly known by the endpoint that uses the dependency.
        # A more robust way would be to include user_type in the token or have different decode logic.

        user_id_str = payload.sub
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise credentials_exception # If subject is not a valid int ID

        user = crud_module.get(db, id=user_id)
        if not user:
            raise credentials_exception
        return user

    except JWTError: # This is already handled in decode_token, but as a safeguard
        raise credentials_exception
    except Exception as e: # Catch any other error, including potential int conversion if sub isn't ID
        # Log e
        raise credentials_exception


def get_current_admin_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> AdminModel:
    user = get_current_user_abstract(db, token, "admin", crud_admin.admin)
    if not crud_admin.admin.is_active(user): # Check if user is AdminModel and active
         raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_active_admin_user(
    current_admin_user: AdminModel = Depends(get_current_admin_user)
) -> AdminModel:
    # This function primarily exists if further checks on current_admin_user were needed.
    # The active check is already in get_current_admin_user.
    # If is_active check was not there, it would be here:
    # if not crud_admin.admin.is_active(current_admin_user):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_admin_user


def get_current_super_admin_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2_super_admin)
) -> SuperAdminModel:
    # Assuming SuperAdmin doesn't have an 'is_active' field, or it's always true
    user = get_current_user_abstract(db, token, "super_admin", crud_super_admin.super_admin)
    return user

def get_current_active_super_admin_user(
    current_super_admin_user: SuperAdminModel = Depends(get_current_super_admin_user)
) -> SuperAdminModel:
    # Placeholder if super_admins could be deactivated
    return current_super_admin_user
