from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None # Subject of the token, e.g., user_id or username
    # exp: Optional[int] = None # Expiry is handled by JWT itself, not typically in payload schema for validation here

# Schema for user login
class LoginRequest(BaseModel):
    username: str
    password: str
