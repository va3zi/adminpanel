from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import decimal
import datetime

# --- Schemas for Admin interacting with OUR backend ---

# Properties for an Admin to request VPN user creation
class VPNUserCreateRequestByAdmin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_.-]+$") # Allowed characters for username
    plan_id: int # ID of the plan selected by the admin from our database

# Properties for an Admin to update a VPN user (e.g., notes, or trigger actions like reset)
# Specific actions like 'reset' might have dedicated endpoints for clarity.
class VPNUserUpdateRequestByAdmin(BaseModel):
    status_notes: Optional[str] = None
    # is_active: Optional[bool] = None # To enable/disable via our panel, syncing with Marzban's status

# Base properties for VPN User data returned by our API
class VPNUserBasePublic(BaseModel):
    id: int # Our database ID
    username: str
    plan_id: int
    created_by_admin_id: int
    expires_at: datetime.datetime
    is_active: bool # Status in our panel (may reflect Marzban status)
    status_notes: Optional[str] = None
    data_usage_gb: Optional[decimal.Decimal] = Field(None, max_digits=10, decimal_places=2) # From our DB, synced from Marzban

    class Config:
        from_attributes = True

# Full VPN User details returned by our API, including Marzban-specific info like links
class VPNUserPublic(VPNUserBasePublic):
    subscription_link: Optional[str] = None # From Marzban via our DB
    qr_code_link: Optional[str] = None # From Marzban via our DB
    # Potentially add more fields from Marzban if needed, like actual Marzban status, data_limit, etc.
    # marzban_user_details: Optional[Dict[str, Any]] = None # To embed raw Marzban response if useful

# --- Schemas for Marzban interaction (internal, used by MarzbanService) ---
# These are illustrative and depend heavily on actual Marzban API structure.

# Example: Data structure for creating a user in Marzban
class MarzbanUserCreate(BaseModel):
    username: str
    proxies: Optional[Dict[str, Any]] = {} # e.g., {"vmess": {"id": "some-uuid", ...}}
    data_limit: Optional[int] = None # Bytes
    expire: Optional[int] = None # Timestamp
    status: Optional[str] = "active" # "active" or "disabled"
    inbounds: Optional[Dict[str, List[str]]] = None # e.g. {"vless": ["VLESS TCP", "VLESS WS"]}
    # data_limit_reset_strategy: Optional[str] = "no_reset" # "no_reset", "daily", "weekly", "monthly"
    # note: Optional[str] = None

# Example: Data structure for updating a user in Marzban
class MarzbanUserUpdate(BaseModel):
    proxies: Optional[Dict[str, Any]] = None
    data_limit: Optional[int] = None
    expire: Optional[int] = None
    status: Optional[str] = None
    inbounds: Optional[Dict[str, List[str]]] = None
    # data_limit_reset_strategy: Optional[str] = None
    # note: Optional[str] = None
    used_traffic: Optional[int] = None # For resetting traffic

# Example: Data structure for user details received from Marzban
class MarzbanUser(BaseModel):
    username: str
    status: str # "active", "disabled", "expired", "limited"
    data_limit: int # Bytes
    expire: int # Timestamp
    used_traffic: int # Bytes
    online_at: Optional[datetime.datetime] = None
    on_hold_expire_duration: Optional[int] = None # seconds
    on_hold_data_limit: Optional[int] = None # bytes
    proxies: Dict[str, Any]
    inbounds: Optional[Dict[str, List[str]]]
    note: Optional[str] = None
    sub_updated_at: Optional[datetime.datetime] = None
    sub_last_user_agent: Optional[str] = None
    # Marzban also returns 'links' and 'subscription_url'
    links: Optional[List[str]] = []
    subscription_url: Optional[str] = None
    excluded_inbounds: Optional[Dict[str, List[str]]] = None

    class Config:
        from_attributes = True # If MarzbanService ever returns Pydantic models directly
        # extra = "ignore" # If Marzban API returns more fields than defined here

# Schema for our VPNUser model in DB (for CRUD operations)
class VPNUserInDBBase(VPNUserBasePublic): # Inherits fields from VPNUserBasePublic
    marzban_user_id: Optional[str] = None
    abresani_user_id: Optional[str] = None
    subscription_link: Optional[str] = None
    qr_code_link: Optional[str] = None
    # Hashed password is not stored for VPN users in our DB, managed by Marzban

    class Config:
        from_attributes = True

class VPNUserInDB(VPNUserInDBBase):
    pass
