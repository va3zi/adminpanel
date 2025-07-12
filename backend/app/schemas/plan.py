from typing import Optional
from pydantic import BaseModel, Field
import decimal

# Base properties for Plan
class PlanBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    duration_days: int = Field(..., gt=0) # e.g., 30 for a month
    data_limit_gb: int = Field(..., ge=0) # Data allowance in GB, 0 for unlimited (if Marzban supports)
    price: decimal.Decimal = Field(..., max_digits=10, decimal_places=2, ge=0)

# Properties to receive via API on creation (by SuperAdmin)
class PlanCreate(PlanBase):
    pass

# Properties to receive via API on update (by SuperAdmin)
class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    duration_days: Optional[int] = Field(None, gt=0)
    data_limit_gb: Optional[int] = Field(None, ge=0)
    price: Optional[decimal.Decimal] = Field(None, max_digits=10, decimal_places=2, ge=0)
    is_active: Optional[bool] = None

# Properties to return via API (e.g., when listing plans for Admins)
class PlanPublic(PlanBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True # orm_mode = True

# Properties stored in DB (matches the model)
class PlanInDB(PlanPublic): # PlanPublic already includes id and is_active
    pass
