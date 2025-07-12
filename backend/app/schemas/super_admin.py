from typing import Optional
from pydantic import BaseModel, EmailStr

# Base properties for SuperAdmin
class SuperAdminBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None

# Properties to receive via API on creation
class SuperAdminCreate(SuperAdminBase):
    password: str

# Properties to return via API (excluding password)
class SuperAdminPublic(SuperAdminBase):
    id: int

    class Config:
        from_attributes = True # Formerly orm_mode = True

# Properties stored in DB (including hashed password)
class SuperAdminInDB(SuperAdminBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True
