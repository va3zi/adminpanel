from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .... import schemas, models
from ....database import get_db
from ....security import get_current_admin
from ....services import marzban_service # Assuming marzban_service is in app.services

router = APIRouter(
    prefix="/vpnusers", # Prefix for all routes in this router
    tags=["Admin - VPN User Management"]
)

@router.post("/", response_model=schemas.VpnUser, status_code=status.HTTP_201_CREATED)
async def create_vpn_user(
    vpn_user_in: schemas.VpnUserCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new VPN user for the current admin.
    """
    # 1. Validate Plan
    plan = db.query(models.Plan).filter(models.Plan.id == vpn_user_in.plan_id, models.Plan.is_active == True).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active plan not found.")

    # 2. Check for existing Marzban username in our DB (globally unique for Marzban)
    existing_db_user = db.query(models.VpnUser).filter(models.VpnUser.marzban_username == vpn_user_in.marzban_username).first()
    if existing_db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username '{vpn_user_in.marzban_username}' already exists in our panel.")

    # (Future: Check admin balance against plan price if payments are implemented)

    # 3. Create user in Marzban
    try:
        # Note: marzban_service.add_marzban_user is a placeholder.
        # Its actual payload and response need to be confirmed with live Marzban API.
        # For now, it's assumed it takes username, data_limit_gb, and duration_days.
        # Marzban itself might handle data_limit and expiry differently (e.g. via node settings or subscription params)
        # The service function should abstract this.
        marzban_user = await marzban_service.add_marzban_user(
            username=vpn_user_in.marzban_username,
            data_limit_gb=plan.data_limit_gb,
            duration_days=plan.duration_days
        )
        # Assuming marzban_user response contains at least 'username'
        if not marzban_user or marzban_user.get("username") != vpn_user_in.marzban_username:
             raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to create user in Marzban or Marzban response inconsistent.")

    except marzban_service.MarzbanAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Marzban API error: {e.detail}")
    except Exception as e: # Catch any other unexpected errors from the service call
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred with Marzban service: {str(e)}")


    # 4. Create user in local database
    db_vpn_user = models.VpnUser(
        marzban_username=vpn_user_in.marzban_username, # Use the confirmed username from Marzban if it can differ
        admin_id=current_admin.id,
        plan_id=plan.id,
        notes=vpn_user_in.notes,
        is_active=True, # Default to active
        expires_at=datetime.utcnow() + timedelta(days=plan.duration_days) if plan.duration_days > 0 else None
    )
    db.add(db_vpn_user)
    db.commit()
    db.refresh(db_vpn_user)

    # (Future: Sync with Abresani API)

    return db_vpn_user


@router.get("/", response_model=List[schemas.VpnUser])
async def list_admin_vpn_users(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100
):
    """
    List all VPN users belonging to the current admin.
    """
    users = db.query(models.VpnUser)\
              .filter(models.VpnUser.admin_id == current_admin.id)\
              .offset(skip)\
              .limit(limit)\
              .all()
    return users

@router.get("/{marzban_username}", response_model=schemas.VpnUserWithMarzbanDetails)
async def get_vpn_user_details(
    marzban_username: str,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Get details for a specific VPN user, including live info from Marzban.
    """
    db_user = db.query(models.VpnUser)\
                .filter(models.VpnUser.marzban_username == marzban_username,
                        models.VpnUser.admin_id == current_admin.id)\
                .first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VPN user not found in your panel.")

    marzban_details_dict = None
    try:
        # marzban_user_data = await marzban_service.get_marzban_user_details(marzban_username)
        # This is a placeholder; real Marzban API might have different structure
        # For now, creating a mock structure for MarzbanUserDetail schema
        # In a real scenario, you'd map the actual Marzban response to MarzbanUserDetail
        raw_marzban_data = await marzban_service.get_marzban_user_details(marzban_username)
        marzban_details_dict = schemas.MarzbanUserDetail(
            username=raw_marzban_data.get("username", marzban_username),
            status=raw_marzban_data.get("status", "unknown"),
            used_traffic=raw_marzban_data.get("used_traffic", 0),
            data_limit=raw_marzban_data.get("data_limit", 0),
            expire=raw_marzban_data.get("expire"),
            subscription_url=raw_marzban_data.get("subscription_url"),
            links=raw_marzban_data.get("links", [])
        )

    except marzban_service.MarzbanAPIError as e:
        # Log the error but don't fail the whole request if Marzban is down, just return panel data
        print(f"Could not fetch live details from Marzban for {marzban_username}: {e.detail}")
    except Exception as e:
        print(f"Unexpected error fetching live details from Marzban for {marzban_username}: {str(e)}")

    response_user = schemas.VpnUser.from_orm(db_user)
    return schemas.VpnUserWithMarzbanDetails(**response_user.dict(), marzban_details=marzban_details_dict)


@router.delete("/{marzban_username}", status_code=status.HTTP_200_OK) # Or 204 No Content
async def delete_vpn_user(
    marzban_username: str,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Delete a VPN user. This removes the user from Marzban and our panel.
    """
    db_user = db.query(models.VpnUser)\
                .filter(models.VpnUser.marzban_username == marzban_username,
                        models.VpnUser.admin_id == current_admin.id)\
                .first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VPN user not found in your panel.")

    try:
        await marzban_service.delete_marzban_user(marzban_username)
    except marzban_service.MarzbanAPIError as e:
        # Decide on behavior: if Marzban delete fails, do we still delete from our panel?
        # For now, let's raise an error and not delete from our panel if Marzban fails.
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Marzban API error during delete: {e.detail}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred with Marzban service during delete: {str(e)}")

    db.delete(db_user)
    db.commit()

    # (Future: Sync deletion with Abresani API)

    return {"message": f"VPN user '{marzban_username}' deleted successfully."}


@router.post("/{marzban_username}/reset-traffic", response_model=schemas.VpnUserWithMarzbanDetails)
async def reset_vpn_user_traffic(
    marzban_username: str,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Reset traffic for a specific VPN user via Marzban.
    """
    db_user = db.query(models.VpnUser)\
                .filter(models.VpnUser.marzban_username == marzban_username,
                        models.VpnUser.admin_id == current_admin.id)\
                .first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VPN user not found in your panel.")

    try:
        # modify_marzban_user with reset_traffic=True calls the /reset endpoint in the service
        await marzban_service.modify_marzban_user(marzban_username, {"reset_traffic": True})
    except marzban_service.MarzbanAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Marzban API error during traffic reset: {e.detail}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred with Marzban service during traffic reset: {str(e)}")

    # Optionally, update local user's 'updated_at' or a specific field if needed
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)

    # Fetch updated details to return
    return await get_vpn_user_details(marzban_username, db, current_admin)


@router.get("/{marzban_username}/subscription-info", response_model=Dict[str, Any])
async def get_vpn_user_subscription_info(
    marzban_username: str,
    db: Session = Depends(get_db), # Not strictly needed if only hitting Marzban, but good for auth
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Get subscription URL and potentially other link info for a VPN user from Marzban.
    """
    # First, verify the user belongs to this admin in our DB, even if we only fetch from Marzban
    db_user = db.query(models.VpnUser)\
                .filter(models.VpnUser.marzban_username == marzban_username,
                        models.VpnUser.admin_id == current_admin.id)\
                .first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VPN user not found in your panel.")

    try:
        # This placeholder function in marzban_service currently just calls get_marzban_user_details
        # and extracts 'subscription_url'. A more direct Marzban endpoint might exist.
        # The get_marzban_user_details returns a dict, let's use that.
        user_marzban_data = await marzban_service.get_marzban_user_details(marzban_username)

        subscription_url = user_marzban_data.get("subscription_url")
        raw_links = user_marzban_data.get("links", []) # List of individual proxy links

        if not subscription_url and not raw_links:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription info not found in Marzban for this user.")

        return {
            "marzban_username": marzban_username,
            "subscription_url": subscription_url,
            "raw_links": raw_links
            # Frontend can generate QR code from subscription_url
        }
    except marzban_service.MarzbanAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Marzban API error getting subscription info: {e.detail}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred with Marzban service: {str(e)}")

# TODO:
# - Consider an endpoint to "sync" a user's status/usage from Marzban to our local DB.
# - Endpoint for Admin to modify a user in our panel (e.g., change plan, notes, is_active).
#   This would then also need to propagate relevant changes to Marzban (e.g., if plan change affects data_limit/expiry).
#   The current VpnUserUpdate schema is basic.
# - Add `cascade` options to ForeignKey relationships in models.VpnUser if needed,
#   e.g., what happens if a Plan is deleted? (Currently, ForeignKey constraint would prevent plan deletion if users are linked).
