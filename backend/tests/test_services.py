import pytest
import respx
from httpx import Response

# Add the parent directory to the path to allow imports from 'app'
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import zarinpal_service

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

@respx.mock
async def test_request_payment_success():
    """
    Tests the successful request of a payment from Zarinpal service.
    """
    # Mock the Zarinpal API endpoint
    request_route = respx.post(zarinpal_service.ZARINPAL_API_REQUEST).mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "code": 100,
                    "message": "Success",
                    "authority": "A00000000000000000000000000351072319",
                    "fee_type": "Merchant",
                    "fee": 1000
                },
                "errors": []
            }
        )
    )

    # Set environment variables for the service to use
    os.environ["ZARINPAL_MERCHANT_ID"] = "TEST_MERCHANT_ID"
    os.environ["ZARINPAL_CALLBACK_URL"] = "http://test.com/callback"

    authority = await zarinpal_service.request_payment(amount=50000, description="Test Payment")

    assert request_route.called
    assert authority == "A00000000000000000000000000351072319"

@respx.mock
async def test_verify_payment_success():
    """
    Tests the successful verification of a payment from Zarinpal service.
    """
    verify_route = respx.post(zarinpal_service.ZARINPAL_API_VERIFY).mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "code": 100,
                    "message": "Verified",
                    "card_hash": "string",
                    "card_pan": "string",
                    "ref_id": 123456,
                    "fee_type": "Merchant",
                    "fee": 1000
                },
                "errors": []
            }
        )
    )

    os.environ["ZARINPAL_MERCHANT_ID"] = "TEST_MERCHANT_ID"

    ref_id = await zarinpal_service.verify_payment(amount=50000, authority="TEST_AUTHORITY")

    assert verify_route.called
    assert ref_id == 123456

async def test_request_payment_failure_no_config():
    """
    Tests that requesting a payment fails if the service is not configured.
    """
    # Unset environment variables
    if "ZARINPAL_MERCHANT_ID" in os.environ:
        del os.environ["ZARINPAL_MERCHANT_ID"]

    with pytest.raises(zarinpal_service.ZarinpalError, match="Zarinpal service is not configured"):
        await zarinpal_service.request_payment(amount=50000, description="Test")
