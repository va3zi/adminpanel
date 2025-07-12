from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel

from .schemas import TokenData # Assuming TokenData is in schemas.py

load_dotenv()

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "a_very_default_secret_key_for_dev_only")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT Token Handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        # You could add more checks here, e.g., token type, scope, etc.
        return TokenData(username=username) # Create a TokenData object
    except JWTError:
        return None

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models # Assuming models.py is in the same directory or accessible
from .database import get_db # Assuming get_db is in database.py

# OAuth2PasswordBearer for SuperAdmin. Token URL points to the SuperAdmin login endpoint.
# Make sure this tokenUrl matches the actual login endpoint path.
oauth2_scheme_super_admin = OAuth2PasswordBearer(tokenUrl="/api/v1/superadmin/login/token")

# Placeholder for OAuth2PasswordBearer for regular Admin (will be defined later)
oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/login/token") # Defined Admin token URL


async def get_current_super_admin(
    token: str = Depends(oauth2_scheme_super_admin),
    db: Session = Depends(get_db)
) -> models.SuperAdmin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials for SuperAdmin",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception

    user = db.query(models.SuperAdmin).filter(models.SuperAdmin.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    # Add more checks if needed, e.g., is_active
    return user


# Placeholder for get_current_admin (similar to above but for Admin model)
async def get_current_admin(
    token: str = Depends(oauth2_scheme_admin), # Use the admin-specific scheme
    db: Session = Depends(get_db)
) -> models.Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials for Admin",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception

    # Verify token type if you add it to the token data during creation
    # For example, if payload includes "type": "admin"
    # if token_data.get("type") != "admin":
    #     raise credentials_exception

    user = db.query(models.Admin).filter(models.Admin.username == token_data.username).first()

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive admin user")
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user_roles: list[str] = None): # Simplified: user_roles would come from token/DB
        if user_roles is None: # For early dev, allow if no roles specified in check
            return True
        # In a real scenario, you'd check if any of user_roles intersect with self.allowed_roles
        # For now, this is a stub.
        # if not any(role in self.allowed_roles for role in user_roles):
        #     raise HTTPException(status_code=403, detail="Not enough permissions")
        pass # Placeholder logic

# Example usage for role-based access (will be refined)
# super_admin_access = RoleChecker(["super_admin"])
# admin_access = RoleChecker(["admin"])
