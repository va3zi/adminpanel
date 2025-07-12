from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .... import schemas, models
from ....database import get_db
from ....security import get_current_admin

router = APIRouter()

@router.get("/plans", response_model=List[schemas.Plan])
async def admin_read_active_plans(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin) # Protected
):
    """
    Fetch all active plans. Accessible by authenticated Admins.
    """
    active_plans = db.query(models.Plan).filter(models.Plan.is_active == True).all()
    if not active_plans:
        # It's not an error if there are no active plans, just return an empty list.
        # If you want to signal "no content" specifically, you could use status.HTTP_204_NO_CONTENT
        # but that usually means the response body is empty. Here, an empty list is valid JSON.
        return []
    return active_plans

# More admin-specific, non-CRUD features can be added here later.
# For example, dashboard summary, account balance, etc.
# The /admin/me endpoint in admin_auth.py already returns balance.
