import httpx
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import time

load_dotenv()

MARZBAN_API_BASE_URL = os.getenv("MARZBAN_API_BASE_URL")
MARZBAN_SUDO_USERNAME = os.getenv("MARZBAN_SUDO_USERNAME")
MARZBAN_SUDO_PASSWORD = os.getenv("MARZBAN_SUDO_PASSWORD")

# This will store the token and its expiry time
_auth_cache: Dict[str, Any] = {"token": None, "expires_at": 0}

class MarzbanAPIError(Exception):
    """Custom exception for Marzban API errors."""
    def __init__(self, status_code: int, detail: Any):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Marzban API Error {status_code}: {detail}")

async def _get_marzban_auth_token() -> Optional[str]:
    """
    Authenticates with Marzban API and retrieves a token, caching it until it expires.
    The actual endpoint is /api/admin/token.
    """
    global _auth_cache

    # Check if token exists and is not expired (with a 60-second buffer)
    if _auth_cache["token"] and _auth_cache["expires_at"] > time.time() + 60:
        return _auth_cache["token"]

    if not MARZBAN_API_BASE_URL or not MARZBAN_SUDO_USERNAME or not MARZBAN_SUDO_PASSWORD:
        print("Marzban API credentials or URL not configured.")
        return None

    # Correct endpoint from openapi.json
    auth_url = f"{MARZBAN_API_BASE_URL.rstrip('/')}/api/admin/token"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                auth_url,
                data={"username": MARZBAN_SUDO_USERNAME, "password": MARZBAN_SUDO_PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()

            access_token = token_data.get("access_token")
            if not access_token:
                print("Failed to retrieve access_token from Marzban auth response.")
                _auth_cache = {"token": None, "expires_at": 0}
                return None

            # Cache the token and set an expiry time.
            # Marzban's JWT_ACCESS_TOKEN_EXPIRE_MINUTES defaults to 1440 (24 hours).
            # Let's assume this and cache it.
            # A more robust solution would decode the JWT to get the 'exp' claim.
            token_lifetime_seconds = int(os.getenv("MARZBAN_TOKEN_LIFETIME_MINUTES", 1440)) * 60
            _auth_cache["token"] = access_token
            _auth_cache["expires_at"] = time.time() + token_lifetime_seconds

            print("Successfully authenticated with Marzban and obtained token.")
            return access_token
        except httpx.HTTPStatusError as e:
            print(f"Marzban authentication HTTP error: {e.response.status_code} - {e.response.text}")
            _auth_cache = {"token": None, "expires_at": 0} # Clear cache on failure
            return None
        except Exception as e:
            print(f"Error during Marzban authentication: {e}")
            _auth_cache = {"token": None, "expires_at": 0}
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

    # Construct URL with /api/ prefix
    url = f"{MARZBAN_API_BASE_URL.rstrip('/')}/api/{endpoint.lstrip('/')}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.request(method, url, json=json_data, params=params, headers=headers)
            response.raise_for_status()
            # For DELETE requests with no content
            if response.status_code == 200 and not response.content:
                return {"status": "success"}
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Marzban API request error to {url}: {e.response.status_code} - {e.response.text}")
            detail = e.response.json() if e.response.content else e.response.text
            raise MarzbanAPIError(e.response.status_code, detail) from e
        except Exception as e:
            print(f"Generic error during Marzban API request to {url}: {e}")
            raise MarzbanAPIError(500, str(e)) from e

# --- Implemented User Management Functions ---

async def add_marzban_user(username: str, data_limit_gb: float, duration_days: int) -> Dict[str, Any]:
    """
    Add a new user to Marzban.
    Endpoint: POST /api/user
    """
    expire_timestamp = 0
    if duration_days > 0:
        # Marzban expects a timestamp, not a duration from now.
        expire_timestamp = int((datetime.utcnow() + timedelta(days=duration_days)).timestamp())

    data_limit_bytes = 0
    if data_limit_gb > 0:
        data_limit_bytes = int(data_limit_gb * 1024 * 1024 * 1024)

    # Based on UserCreate schema in openapi.json
    payload = {
        "username": username,
        "proxies": {
            "vmess": {},
            "vless": {}
            # Add other protocols if needed, empty object creates default settings.
        },
        "expire": expire_timestamp,
        "data_limit": data_limit_bytes,
        "data_limit_reset_strategy": "no_reset"
    }
    return await _make_marzban_request("POST", "user", json_data=payload)

async def get_marzban_user_details(username: str) -> Dict[str, Any]:
    """
    Get details for a specific user from Marzban.
    Endpoint: GET /api/user/{username}
    """
    return await _make_marzban_request("GET", f"user/{username}")

async def delete_marzban_user(username: str) -> Dict[str, Any]:
    """
    Delete a user from Marzban.
    Endpoint: DELETE /api/user/{username}
    """
    return await _make_marzban_request("DELETE", f"user/{username}")

async def reset_marzban_user_traffic(username: str) -> Dict[str, Any]:
    """
    Reset a user's data usage in Marzban.
    Endpoint: POST /api/user/{username}/reset
    """
    return await _make_marzban_request("POST", f"user/{username}/reset")

async def get_all_marzban_users(offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    Get a list of all users from Marzban.
    Endpoint: GET /api/users
    """
    return await _make_marzban_request("GET", "users", params={"offset": offset, "limit": limit})

# We don't need a separate subscription URL function, as it's part of the UserResponse schema
# fetched by get_marzban_user_details.
# The same goes for raw links.

# The modify_marzban_user function can be implemented if needed, but it's more complex
# as it requires sending the full UserModify payload. For now, reset is sufficient.
async def modify_marzban_user(username: str, modifications: Dict[str, Any]) -> Dict[str, Any]:
    """
    Modify a user in Marzban.
    Endpoint: PUT /api/user/{username}
    NOTE: This is a full update. `modifications` should be a valid UserModify payload.
    """
    # This function is more complex than just sending the modifications,
    # as the PUT endpoint might expect the full object.
    # The current panel logic doesn't require a general modify endpoint yet.
    # If it were to be implemented, it would look something like this:
    #
    # current_details = await get_marzban_user_details(username)
    # # The UserModify schema has many nullable fields.
    # # We can construct a payload with just the changes.
    # payload = {
    #     "status": modifications.get("status"),
    #     "expire": modifications.get("expire"),
    #     ...
    # }
    # payload = {k: v for k, v in payload.items() if v is not None} # remove None values
    # return await _make_marzban_request("PUT", f"user/{username}", json_data=payload)
    raise NotImplementedError("General user modification not implemented yet.")
