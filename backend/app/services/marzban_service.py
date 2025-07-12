import httpx
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

load_dotenv()

MARZBAN_API_BASE_URL = os.getenv("MARZBAN_API_BASE_URL")
MARZBAN_SUDO_USERNAME = os.getenv("MARZBAN_SUDO_USERNAME")
MARZBAN_SUDO_PASSWORD = os.getenv("MARZBAN_SUDO_PASSWORD")
# MARZBAN_API_TOKEN = os.getenv("MARZBAN_API_TOKEN") # If using a direct token

# Placeholder for storing the auth token obtained from Marzban
# In a real app, this token management would need to be more robust (e.g., refresh, expiry handling)
_marzban_auth_token: Optional[str] = None

class MarzbanAPIError(Exception):
    """Custom exception for Marzban API errors."""
    def __init__(self, status_code: int, detail: Any):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Marzban API Error {status_code}: {detail}")

async def _get_marzban_auth_token() -> Optional[str]:
    """
    Authenticates with Marzban API and retrieves a token.
    This is a placeholder and needs to be adapted to Marzban's actual auth endpoint.
    Marzban's /api/admin/token endpoint is likely what's needed.
    """
    global _marzban_auth_token
    if _marzban_auth_token: # Basic caching, would need expiry check in real app
        # TODO: Add token expiry check and re-login if expired
        return _marzban_auth_token

    if not MARZBAN_API_BASE_URL or not MARZBAN_SUDO_USERNAME or not MARZBAN_SUDO_PASSWORD:
        print("Marzban API credentials or URL not configured.")
        # raise MarzbanAPIError(500, "Marzban service not configured")
        return None # Silently fail for now if not configured during dev

    # Assuming Marzban has an endpoint like /api/admin/token for sudo users (common in FastAPI apps)
    auth_url = f"{MARZBAN_API_BASE_URL.rstrip('/')}/admin/token"

    async with httpx.AsyncClient() as client:
        try:
            # Marzban uses OAuth2PasswordRequestForm for its /api/admin/token
            response = await client.post(
                auth_url,
                data={"username": MARZBAN_SUDO_USERNAME, "password": MARZBAN_SUDO_PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status() # Raise an exception for HTTP error codes
            token_data = response.json()
            _marzban_auth_token = token_data.get("access_token")
            if not _marzban_auth_token:
                print("Failed to retrieve access_token from Marzban auth response.")
                return None
            print("Successfully authenticated with Marzban and obtained token.")
            return _marzban_auth_token
        except httpx.HTTPStatusError as e:
            print(f"Marzban authentication HTTP error: {e.response.status_code} - {e.response.text}")
            # raise MarzbanAPIError(e.response.status_code, e.response.json()) from e
            return None
        except Exception as e:
            print(f"Error during Marzban authentication: {e}")
            # raise MarzbanAPIError(500, str(e)) from e
            return None

async def _make_marzban_request(
    method: str,
    endpoint: str,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Helper function to make authenticated requests to Marzban API."""
    token = await _get_marzban_auth_token()
    if not token:
        raise MarzbanAPIError(401, "Not authenticated with Marzban or Marzban service not configured.")

    if not MARZBAN_API_BASE_URL:
         raise MarzbanAPIError(500, "Marzban API base URL not configured.")

    url = f"{MARZBAN_API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, json=json_data, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Marzban API request error to {url}: {e.response.status_code} - {e.response.text}")
            raise MarzbanAPIError(e.response.status_code, e.response.json() if e.response.content else e.response.text) from e
        except Exception as e:
            print(f"Generic error during Marzban API request to {url}: {e}")
            raise MarzbanAPIError(500, str(e)) from e

# --- Placeholder User Management Functions ---
# These need to be verified and implemented based on actual Marzban API docs.

async def get_marzban_users(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Placeholder: Get a list of users from Marzban.
    Marzban API endpoint: /api/users
    """
    # TODO: Verify Marzban endpoint and parameters
    return await _make_marzban_request("GET", "users", params={"offset": skip, "limit": limit}) # Marzban uses offset/limit

async def add_marzban_user(username: str, data_limit_gb: float, duration_days: int) -> Dict[str, Any]:
    """
    Placeholder: Add a new user to Marzban.
    Marzban API endpoint: /api/user
    Converts GB to bytes and days to timestamp for Marzban.
    """
    # TODO: Verify Marzban endpoint and request payload structure.
    # Marzban expects data_limit in bytes and expire as a timestamp (seconds from epoch).
    # Marzban user creation payload example from its source:
    # {
    #   "username": "string",
    #   "proxies": { "vmess": {"id": "uuid string"} ... }, // Define which proxy types
    #   "inbounds": null, // Optional: specify inbounds for specific protocols
    #   "expire": 0, // Timestamp in seconds, 0 for no limit
    #   "data_limit": 0, // Bytes, 0 for no limit
    #   "data_limit_reset_strategy": "no_reset" // e.g., "no_reset", "daily", "weekly", "monthly"
    #   "status": "active" // "active", "disabled", "limited", "expired"
    #   "note": "string"
    #   "sub_updated_at": null
    #   "sub_last_user_agent": null
    #   "online_at": null
    #   "on_hold_expire_duration": 0 // if user on_hold
    #   "on_hold_data_limit": 0 // if user on_hold
    # }
    # We need to define default proxies. For now, let's assume VMess is standard.
    # This needs to be configurable or based on the plan.

    from datetime import datetime, timedelta

    expire_timestamp = 0
    if duration_days > 0:
        expire_date = datetime.utcnow() + timedelta(days=duration_days)
        expire_timestamp = int(expire_date.timestamp())

    data_limit_bytes = 0
    if data_limit_gb > 0:
        data_limit_bytes = int(data_limit_gb * 1024 * 1024 * 1024)

    payload = {
        "username": username,
        "proxies": {"vmess": {}}, # Simplistic default, assuming Marzban auto-configures details
        # "expire": expire_timestamp, # This might be set via subscription or node settings in Marzban
        # "data_limit": data_limit_bytes, # This might be set via subscription or node settings
        # For our panel, we'll likely manage these via the subscription settings for the user.
        # The core user creation might be simpler, and then we apply plan settings.
        # Let's assume for now user creation is just username + proxies,
        # and plan parameters (limit, expiry) are applied when getting subscription link or by Marzban itself.
        # This part is CRITICAL and needs actual Marzban API docs.
        #
        # Based on Marzban CLI user_add:
        # It seems `data_limit` and `expire` ARE part of the user creation.
        # `proxies` need to be specified.
    }
    # This is a simplified payload for now. A real one would need to specify proxy settings.
    # The Marzban API for creating user is POST /api/user
    # It seems the actual data limit and expiry are set when user is added to a node or via subscription settings.
    # For direct user creation:
    user_data = {
        "username": username,
        "proxies": {"vmess": {}}, # Example, this needs to be configured based on actual Marzban setup
        "data_limit": data_limit_bytes,
        "expire": expire_timestamp,
        "status": "active",
        # "data_limit_reset_strategy": "no_reset", # This is a common default
    }
    return await _make_marzban_request("POST", "user", json_data=user_data)


async def get_marzban_user_details(username: str) -> Dict[str, Any]:
    """
    Placeholder: Get details for a specific user from Marzban.
    Marzban API endpoint: /api/user/{username}
    """
    # TODO: Verify Marzban endpoint
    return await _make_marzban_request("GET", f"user/{username}")

async def delete_marzban_user(username: str) -> Dict[str, Any]:
    """
    Placeholder: Delete a user from Marzban.
    Marzban API endpoint: /api/user/{username}
    """
    # TODO: Verify Marzban endpoint
    return await _make_marzban_request("DELETE", f"user/{username}")

async def modify_marzban_user(username: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder: Modify a user in Marzban (e.g., reset traffic, change status).
    Marzban API endpoint: /api/user/{username} (PUT or PATCH)
    To reset traffic: set "used_traffic" to 0.
    Other modifiable fields: status, expire, data_limit, proxies etc.
    """
    # TODO: Verify Marzban endpoint and payload for modifications.
    # Example for resetting traffic: modifications = {"used_traffic": 0}
    # Marzban API seems to use PUT for user modification: PUT /api/user/{username}
    # The body should contain all fields of the user, not just the modified ones.
    # So, first GET the user, then modify, then PUT.
    #
    # Simpler: Marzban has a specific reset endpoint: POST /api/user/{username}/reset
    if modifications.get("reset_traffic"): # Special handling for reset
        return await _make_marzban_request("POST", f"user/{username}/reset")

    # For other modifications, you'd typically fetch the user, update fields, then PUT.
    # This is complex, let's assume for now only reset is implemented via this service.
    # A full update would look like:
    # current_user_data = await get_marzban_user_details(username)
    # updated_user_data = {**current_user_data, **modifications}
    # return await _make_marzban_request("PUT", f"user/{username}", json_data=updated_user_data)
    raise NotImplementedError("General user modification not fully implemented yet, only traffic reset.")


async def get_marzban_user_subscription_url(username: str) -> Optional[str]:
    """
    Placeholder: Get the subscription URL for a user.
    This might be part of the user details or a separate endpoint.
    Marzban's user object contains `subscription_url`.
    """
    user_details = await get_marzban_user_details(username)
    return user_details.get("subscription_url")

async def get_marzban_user_qr_code_url(username: str) -> Optional[str]:
    """
    Placeholder: Get a URL to the QR code image for the user's subscription.
    Marzban dashboard usually generates this. If API provides it directly, great.
    Otherwise, we might need to construct it or use a library if it's just the sub link.
    Marzban's user object contains `links` which are the raw proxy links.
    The main subscription_url is usually preferred for client compatibility.
    QR codes are typically generated client-side from the subscription_url.
    """
    # For now, let's assume the subscription URL is what we primarily need.
    # The frontend can generate a QR code from this URL.
    return await get_marzban_user_subscription_url(username)


# Test function (optional, for direct testing of this service file)
async def main_test():
    print("Attempting to authenticate with Marzban...")
    token = await _get_marzban_auth_token()
    if token:
        print(f"Auth token obtained: {token[:20]}...")
        try:
            print("\nAttempting to get users...")
            users = await get_marzban_users(limit=5)
            print(f"Found users: {users}")

            # Example: Add a user (ensure this username doesn't conflict or is testable)
            # print("\nAttempting to add a test user...")
            # new_user = await add_marzban_user("testserviceuser123", 1, 30)
            # print(f"New user created: {new_user}")
            # test_username = new_user.get("username")

            # if test_username:
            #     print(f"\nAttempting to get details for {test_username}...")
            #     details = await get_marzban_user_details(test_username)
            #     print(f"Details: {details}")

            #     print(f"\nAttempting to reset traffic for {test_username}...")
            #     reset_info = await modify_marzban_user(test_username, {"reset_traffic": True})
            #     print(f"Reset info: {reset_info}")

            #     print(f"\nAttempting to get subscription URL for {test_username}...")
            #     sub_url = await get_marzban_user_subscription_url(test_username)
            #     print(f"Subscription URL: {sub_url}")

            #     print(f"\nAttempting to delete {test_username}...")
            #     delete_info = await delete_marzban_user(test_username)
            #     print(f"Delete info: {delete_info}")

        except MarzbanAPIError as e:
            print(f"Marzban API Error during test operations: {e.status_code} - {e.detail}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("Could not obtain Marzban auth token. Ensure .env is configured correctly and Marzban is running.")

if __name__ == "__main__":
    # This allows running `python -m app.services.marzban_service` from `backend` directory
    import asyncio
    asyncio.run(main_test())
