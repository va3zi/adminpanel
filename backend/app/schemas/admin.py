from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import decimal

# Base properties for Admin
class AdminBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None

# Properties to receive via API on creation by SuperAdmin
class AdminCreate(AdminBase):
    password: str

# Properties for Admin update (e.g., by SuperAdmin)
class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    # Password updates would require a separate flow or schema for security (e.g. AdminUpdatePassword)
    # Balance updates are handled by payment system, not direct API update here.

# Properties to return via API (excluding password)
class AdminPublic(AdminBase):
    id: int
    balance: decimal.Decimal = Field(max_digits=10, decimal_places=2)
    is_active: bool

    class Config:
        from_attributes = True

# Properties stored in DB
class AdminInDB(AdminBase):
    id: int
    hashed_password: str
    balance: decimal.Decimal = Field(max_digits=10, decimal_places=2)
    is_active: bool
    created_by_super_admin_id: Optional[int] = None

    class Config:
        from_attributes = True
