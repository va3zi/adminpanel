from fastapi import APIRouter

# Import endpoint modules here
# from .endpoints import items, users # Example
from .endpoints import superadmin_auth, admins, plans # Will create these files next

api_router_v1 = APIRouter()

# Include routers from endpoint modules
# api_router_v1.include_router(items.router, prefix="/items", tags=["items"])
# api_router_v1.include_router(users.router, prefix="/users", tags=["users"])

api_router_v1.include_router(superadmin_auth.router, prefix="/superadmin", tags=["SuperAdmin Auth"])
api_router_v1.include_router(admins.router, prefix="/admins", tags=["Admins Management (SuperAdmin)"])
api_router_v1.include_router(plans.router, prefix="/plans", tags=["Plans Management (SuperAdmin)"])
