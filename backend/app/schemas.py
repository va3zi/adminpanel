from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --------------- Plan Schemas ---------------
class PlanBase(BaseModel):
    name: str
    price: float
    duration_days: int
    data_limit_gb: float
    is_active: bool = True

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    name: Optional[str] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None
    data_limit_gb: Optional[float] = None
    is_active: Optional[bool] = None

class Plan(PlanBase): # Schema for returning a plan
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# --------------- SuperAdmin Schemas ---------------
class SuperAdminBase(BaseModel):
    username: str
    email: EmailStr

class SuperAdminCreate(SuperAdminBase):
    password: str

class SuperAdmin(SuperAdminBase): # Schema for returning a SuperAdmin
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# --------------- Admin Schemas ---------------
class AdminBase(BaseModel):
    username: str
    email: EmailStr
    balance: float = 0.0
    is_active: bool = True

class AdminCreate(AdminBase):
    password: str
    created_by_super_admin_id: Optional[int] = None # Can be set by SuperAdmin

class AdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    balance: Optional[float] = None
    is_active: Optional[bool] = None
    # Password updates should be handled by a separate endpoint/schema for security

class Admin(AdminBase): # Schema for returning an Admin
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    # created_by_super_admin_id: Optional[int] = None # Decide if this should be exposed

    class Config:
        orm_mode = True

# Token Schemas for Authentication
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    # You can add more fields here like user_id, roles etc.

# Login Schema
class LoginRequest(BaseModel):
    username: str
    password: str


# Schemas for future models (will be defined later)
# VpnUser, PaymentLog etc.
