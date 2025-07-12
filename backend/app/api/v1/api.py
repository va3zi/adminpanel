from fastapi import APIRouter

# Import endpoint modules
from .endpoints import superadmin_auth, admins, plans, admin_auth, admin_features

api_router_v1 = APIRouter()

# SuperAdmin Endpoints
api_router_v1.include_router(superadmin_auth.router, prefix="/superadmin", tags=["SuperAdmin Auth"])
api_router_v1.include_router(admins.router, prefix="/admins", tags=["SuperAdmin - Admins Management"])
api_router_v1.include_router(plans.router, prefix="/plans", tags=["SuperAdmin - Plans Management"]) # This is for SA to manage all plans

from .endpoints import superadmin_auth, admins, plans, admin_auth, admin_features, vpn_users, payment

# Admin Endpoints
api_router_v1.include_router(admin_auth.router, prefix="/admin", tags=["Admin Auth"])
api_router_v1.include_router(admin_features.router, prefix="/admin", tags=["Admin Features"]) # e.g., viewing active plans for themselves
api_router_v1.include_router(vpn_users.router, prefix="/admin", tags=["Admin - VPN User Management"]) # Added VPN users router under /admin
api_router_v1.include_router(payment.router, tags=["Payment"]) # Payment endpoints (some admin, some public callback)
