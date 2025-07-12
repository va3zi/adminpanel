from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from .... import schemas, models
from ....database import get_db
from ....security import get_current_admin
from ....services import zarinpal_service
import os

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")

@router.post("/admin/payments/request", response_model=schemas.PaymentRequestResponse)
async def request_payment_url(
    payment_request: schemas.PaymentRequest,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    An authenticated admin requests a Zarinpal payment URL for a given amount.
    """
    amount = int(payment_request.amount)
    if amount < 1000: # Zarinpal has a minimum amount, typically 1000 Toman (10000 IRR)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be at least 1000 Toman.")

    try:
        # Request a payment from Zarinpal
        authority = await zarinpal_service.request_payment(
            amount=amount,
            description=f"Charge admin panel account for user: {current_admin.username}",
            email=current_admin.email
        )

        # Log the pending transaction in the database
        new_log = models.PaymentLog(
            admin_id=current_admin.id,
            amount=amount,
            authority=authority,
            status='pending'
        )
        db.add(new_log)
        db.commit()

        # Construct the payment URL and return it
        payment_url = zarinpal_service.get_start_pay_url(authority)
        return {"payment_url": payment_url}

    except zarinpal_service.ZarinpalError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Zarinpal service error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal error occurred: {str(e)}")

@router.get("/payments/zarinpal/callback", include_in_schema=False) # Hide from public API docs
async def handle_zarinpal_callback(
    request: Request,
    db: Session = Depends(get_db),
    Status: str = Query(...),
    Authority: str = Query(...)
):
    """
    Callback endpoint for Zarinpal to redirect to after payment attempt.
    This endpoint verifies the payment and updates the admin's balance.
    """
    # Find the pending payment log using the authority token
    payment_log = db.query(models.PaymentLog).filter(models.PaymentLog.authority == Authority, models.PaymentLog.status == 'pending').first()

    if not payment_log:
        # This could happen if the authority is invalid or already processed.
        # Redirect to a failure page on the frontend.
        return RedirectResponse(url=f"{FRONTEND_URL}/payment/failed?error=transaction_not_found")

    if Status != 'OK':
        payment_log.status = 'failed'
        db.commit()
        return RedirectResponse(url=f"{FRONTEND_URL}/payment/failed?error=payment_cancelled")

    try:
        # Verify the payment with Zarinpal
        ref_id = await zarinpal_service.verify_payment(
            amount=int(payment_log.amount),
            authority=Authority
        )

        # Payment is successful
        payment_log.status = 'completed'
        payment_log.ref_id = ref_id
        payment_log.verified_at = datetime.utcnow()

        # Update the admin's balance
        admin_user = db.query(models.Admin).filter(models.Admin.id == payment_log.admin_id).first()
        if admin_user:
            admin_user.balance += payment_log.amount

        db.commit()

        # Redirect to success page on frontend
        return RedirectResponse(url=f"{FRONTEND_URL}/payment/success?ref_id={ref_id}")

    except zarinpal_service.ZarinpalError as e:
        payment_log.status = 'failed'
        db.commit()
        print(f"Zarinpal verification error: {e.message}")
        return RedirectResponse(url=f"{FRONTEND_URL}/payment/failed?error=verification_failed&code={e.code}")
    except Exception as e:
        payment_log.status = 'failed'
        db.commit()
        print(f"Internal error during callback handling: {str(e)}")
        return RedirectResponse(url=f"{FRONTEND_URL}/payment/failed?error=internal_error")


@router.get("/admin/payments/logs", response_model=List[schemas.PaymentLog])
async def get_admin_payment_logs(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 20
):
    """
    An authenticated admin retrieves their own payment history.
    """
    logs = db.query(models.PaymentLog)\
             .filter(models.PaymentLog.admin_id == current_admin.id)\
             .order_by(models.PaymentLog.created_at.desc())\
             .offset(skip)\
             .limit(limit)\
             .all()
    return logs
