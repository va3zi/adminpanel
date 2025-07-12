from .crud_super_admin import super_admin
from .crud_admin import admin
from .crud_plan import plan
from .crud_vpn_user import vpn_user

# Will add other CRUD objects here as created
# from .crud_payment import payment_transaction

__all__ = [
    "super_admin",
    "admin",
    "plan",
    "vpn_user",
]
