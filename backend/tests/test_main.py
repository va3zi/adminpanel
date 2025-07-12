import pytest
from httpx import AsyncClient

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

async def test_health_check(async_client: AsyncClient):
    """
    Tests the /health endpoint to ensure it returns a 200 OK status.
    """
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

async def test_root(async_client: AsyncClient):
    """
    Tests the root endpoint /.
    """
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
