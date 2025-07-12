from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import settings
from ..schemas.token import TokenPayload # Will create this schema later

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def decode_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        # Validate payload against TokenPayload schema
        # The 'sub' field will be extracted. 'exp' is used by JWT for validation already.
        token_data = TokenPayload(sub=payload.get("sub"))
        return token_data
    except JWTError: # Covers expired signature, invalid signature, etc.
        return None
    except Exception: # Catch any other validation errors if TokenPayload had more fields
        # Consider logging the exception e
        return None
