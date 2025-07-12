from fastapi import APIRouter

from .auth import router as auth_router
from .admins import router as admins_router
# from .plans import router as plans_router # To be added later
# from .users import router as vpn_users_router # To be added later
# from .payments import router as payments_router # To be added later

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(admins_router, prefix="/admins", tags=["Admins Management (by SuperAdmin)"])
# api_v1_router.include_router(plans_router, prefix="/plans", tags=["Plans Management"])
# api_v1_router.include_router(vpn_users_router, prefix="/users", tags=["VPN Users Management (by Admin)"])
# api_v1_router.include_router(payments_router, prefix="/payments", tags=["Payments (Admin Recharge)"])
