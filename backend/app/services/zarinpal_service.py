import httpx
import os
from dotenv import load_dotenv

load_dotenv()

ZARINPAL_MERCHANT_ID = os.getenv("ZARINPAL_MERCHANT_ID")
ZARINPAL_CALLBACK_URL = os.getenv("ZARINPAL_CALLBACK_URL")

# Zarinpal API URLs (as per general documentation)
ZARINPAL_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZARINPAL_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/"

class ZarinpalError(Exception):
    """Custom exception for Zarinpal service errors."""
    def __init__(self, message: str, code: int = -1):
        self.message = message
        self.code = code
        super().__init__(f"Zarinpal Error {code}: {message}")

async def request_payment(amount: int, description: str, email: str = None, mobile: str = None) -> str:
    """
    Requests a new payment from Zarinpal.
    Returns the payment URL to redirect the user to.
    """
    if not ZARINPAL_MERCHANT_ID or not ZARINPAL_CALLBACK_URL:
        raise ZarinpalError("Zarinpal service is not configured in the environment.", -1)

    payload = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "callback_url": ZARINPAL_CALLBACK_URL,
        "description": description,
        "metadata": {"email": email, "mobile": mobile}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(ZARINPAL_API_REQUEST, json=payload)
            response.raise_for_status()
            response_data = response.json()

            if response_data.get("errors") and len(response_data["errors"]) > 0:
                error_code = response_data["errors"]["code"]
                error_message = response_data["errors"]["message"]
                raise ZarinpalError(f"Failed to request payment: {error_message}", error_code)

            if response_data.get("data") and response_data["data"].get("authority"):
                authority = response_data["data"]["authority"]
                return authority
            else:
                raise ZarinpalError("Invalid response from Zarinpal on payment request.", -1)

        except httpx.HTTPStatusError as e:
            raise ZarinpalError(f"HTTP error during payment request: {e.response.status_code}", e.response.status_code) from e
        except Exception as e:
            raise ZarinpalError(f"An unexpected error occurred during payment request: {str(e)}", -1) from e


async def verify_payment(amount: int, authority: str) -> str:
    """
    Verifies a payment with Zarinpal after the user returns from the gateway.
    Returns the reference ID (ref_id) if successful.
    """
    if not ZARINPAL_MERCHANT_ID:
        raise ZarinpalError("Zarinpal service is not configured in the environment.", -1)

    payload = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "authority": authority,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(ZARINPAL_API_VERIFY, json=payload)
            response.raise_for_status()
            response_data = response.json()

            if response_data.get("errors") and len(response_data["errors"]) > 0:
                error_code = response_data["errors"]["code"]
                error_message = response_data["errors"]["message"]
                raise ZarinpalError(f"Payment verification failed: {error_message}", error_code)

            if response_data.get("data") and response_data["data"].get("code") == 100:
                # Payment is successful
                return response_data["data"]["ref_id"]
            elif response_data.get("data") and response_data["data"].get("code") == 101:
                # Payment was already verified, this can happen if user refreshes the callback page
                # It's often safe to treat this as a success, but check your logs to be sure.
                print(f"Warning: Zarinpal reported payment with authority {authority} was already verified.")
                return response_data["data"]["ref_id"]
            else:
                # Any other code is a failure
                error_code = response_data.get("data", {}).get("code", -1)
                error_message = response_data.get("data", {}).get("message", "Unknown verification error")
                raise ZarinpalError(f"Payment verification failed: {error_message}", error_code)

        except httpx.HTTPStatusError as e:
            raise ZarinpalError(f"HTTP error during payment verification: {e.response.status_code}", e.response.status_code) from e
        except Exception as e:
            raise ZarinpalError(f"An unexpected error occurred during payment verification: {str(e)}", -1) from e

def get_start_pay_url(authority: str) -> str:
    """
    Constructs the URL to redirect the user to for payment.
    """
    return f"{ZARINPAL_API_STARTPAY}{authority}"
