import httpx
from typing import Optional, Dict, Any, List
import datetime
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class MarzbanServiceError(Exception):
    """Custom exception for Marzban service errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class MarzbanService:
    def __init__(self):
        self.base_url = settings.MARZBAN_API_URL.rstrip('/')
        self.username = settings.MARZBAN_USERNAME
        self.password = settings.MARZBAN_PASSWORD
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime.datetime] = None
        # Initialize an async client if making async calls, or sync client
        # For simplicity in a service class that might be instantiated per request or globally,
        # manage client lifecycle carefully. For now, creating client per request or short-lived.
        # A shared client is better for performance: https://www.python-httpx.org/advanced/#client-instances
        # self.client = httpx.AsyncClient() # If using async def methods

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        """
        Authenticates with Marzban and retrieves an API token.
        Caches the token until it's about to expire.
        """
        if self._token and self._token_expiry and self._token_expiry > datetime.datetime.now(datetime.timezone.utc):
            return self._token

        login_url = f"{self.base_url}/token"
        auth_data = {
            "username": self.username,
            "password": self.password,
        }
        try:
            response = await client.post(login_url, data=auth_data) # Marzban uses form data for token

            if response.status_code == 422: # Unprocessable Entity - often validation error
                logger.error(f"Marzban login validation error: {response.json()}")
                raise MarzbanServiceError("Marzban login validation error.", status_code=response.status_code)

            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            token_data = response.json()

            self._token = token_data.get("access_token")
            if not self._token:
                logger.error("Marzban login response did not include an access_token.")
                raise MarzbanServiceError("Marzban login failed: No access token in response.")

            # Assuming token has a standard expiry, e.g. 1 hour. Marzban docs would clarify.
            # For now, let's assume a fixed lifetime or that Marzban doesn't return expiry.
            # If it does, use it: e.g. expires_in = token_data.get("expires_in", 3600) # seconds
            # self._token_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in - 60) # 60s buffer

            # Simplified: refresh token more often if expiry is not known.
            # Or, rely on 401 to re-authenticate. For now, cache for a fixed short period.
            self._token_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=55) # Cache for 55 mins

            logger.info("Successfully obtained Marzban API token.")
            return self._token
        except httpx.HTTPStatusError as e:
            logger.error(f"Marzban login HTTP error: {e.response.status_code} - {e.response.text}")
            raise MarzbanServiceError(f"Marzban login failed: {e.response.status_code}", status_code=e.response.status_code)
        except httpx.RequestError as e:
            logger.error(f"Marzban login request error: {e}")
            raise MarzbanServiceError(f"Marzban login request failed: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during Marzban login: {e}")
            raise MarzbanServiceError(f"Unexpected error during Marzban login: {e}")


    async def _request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            token = await self._get_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{self.base_url}/{endpoint.lstrip('/')}"

            try:
                response = await client.request(method, url, json=data, params=params, headers=headers)

                if response.status_code == 401: # Token expired or invalid
                    logger.info("Marzban token likely expired, attempting to re-authenticate.")
                    self._token = None # Force re-authentication
                    token = await self._get_token(client)
                    headers["Authorization"] = f"Bearer {token}"
                    response = await client.request(method, url, json=data, params=params, headers=headers)

                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Marzban API request to {url} failed: {e.response.status_code} - {e.response.text}")
                raise MarzbanServiceError(
                    f"Marzban API error: {e.response.status_code} - {e.response.json().get('detail', e.response.text)}",
                    status_code=e.response.status_code
                )
            except httpx.RequestError as e:
                logger.error(f"Marzban API request to {url} failed: {e}")
                raise MarzbanServiceError(f"Marzban API request failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during Marzban API request to {url}: {e}")
                raise MarzbanServiceError(f"Unexpected error during Marzban API request: {e}")

    # --- User Management Methods ---
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new user in Marzban.
        user_data should conform to Marzban's API requirements for user creation.
        Example user_data:
        {
            "username": "testuser",
            "proxies": {"vmess": {"id": "uuid", ...}}, # This structure is highly dependent on Marzban API
            "data_limit": 10737418240,  # 10 GB in bytes
            "expire": 1677648000,  # Timestamp for expiry
            "status": "active",
            # "inbounds": {} # Optional: specific inbounds
        }
        """
        # Marzban API might use /api/user instead of /api/users
        # The official Marzban-Panel uses /api/user for POST to create
        return await self._request("POST", "user", data=user_data)

    async def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific user by username from Marzban."""
        try:
            return await self._request("GET", f"user/{username}")
        except MarzbanServiceError as e:
            if e.status_code == 404:
                return None # User not found
            raise e

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves all users from Marzban with pagination."""
        # Marzban API uses /api/users for GET to list users
        params = {"offset": skip, "limit": limit}
        return await self._request("GET", "users", params=params)

    async def update_user(self, username: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing user in Marzban.
        update_data can include fields like data_limit, expire, status, proxies, etc.
        """
        # Marzban API uses PUT /api/user/{username}
        return await self._request("PUT", f"user/{username}", data=update_data)

    async def delete_user(self, username: str) -> Dict[str, Any]: # Or bool
        """Deletes a user from Marzban."""
        # Marzban API uses DELETE /api/user/{username}
        return await self._request("DELETE", f"user/{username}")

    async def reset_user_traffic(self, username: str) -> Dict[str, Any]:
        """
        Resets a user's data usage.
        This might involve updating the user with data_limit and a new start date or specific API call.
        Marzban's panel seems to do this by modifying the user's data_limit_reset_strategy or similar.
        For simplicity, let's assume updating used_traffic to 0 or re-applying data_limit.
        Actual implementation depends heavily on Marzban API specifics.
        A common way is to re-set the `data_limit` and `expire` fields to trigger a reset.
        Alternatively, Marzban might have a dedicated endpoint like /api/user/{username}/reset
        """
        # This is a placeholder. The actual mechanism needs Marzban API docs.
        # Option 1: Update user with new data_limit and possibly start date for cycle
        # user_details = await self.get_user(username)
        # if not user_details:
        #     raise MarzbanServiceError(f"User {username} not found for traffic reset.", status_code=404)
        # update_payload = {
        #     "data_limit": user_details.get("data_limit"), # Keep original data_limit
        #     # Potentially adjust 'expire' or a 'reset_date' field if Marzban uses such.
        # }
        # return await self.update_user(username, update_payload)

        # Option 2: If there's a dedicated reset endpoint (more likely for specific actions)
        # return await self._request("POST", f"user/{username}/reset-traffic")

        # For now, let's assume it means re-applying the current data_limit,
        # which might or might not reset usage depending on Marzban's logic.
        # A more direct approach would be needed if Marzban tracks 'used_traffic' and allows setting it.
        # The Marzban panel seems to have a "Reset Usage" button which likely calls a specific API.
        # Without docs, this is speculative.
        # The panel source code (core/user.py -> reset_user_data_usage) suggests it sets `used_traffic` to 0.
        # So, the update_user payload should include "used_traffic": 0.
        logger.info(f"Attempting to reset traffic for user {username} by setting used_traffic to 0.")
        return await self.update_user(username, {"used_traffic": 0})


# Global instance (consider dependency injection for FastAPI)
marzban_service = MarzbanService()
