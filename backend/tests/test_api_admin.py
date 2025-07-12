import pytest
from httpx import AsyncClient

# Add the parent directory to the path to allow imports from 'app'
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.security import get_current_admin
from app.models import Admin

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

# Create a mock admin user to be returned by the overridden dependency
mock_admin_user = Admin(
    id=1,
    username="testadmin",
    email="test@admin.com",
    balance=100.0,
    is_active=True
)

# This function will override the `get_current_admin` dependency in our tests
async def override_get_current_admin():
    return mock_admin_user

# Apply the dependency override to our app instance for the duration of these tests
app.dependency_overrides[get_current_admin] = override_get_current_admin


async def test_get_admin_me(async_client: AsyncClient):
    """
    Tests the /api/admin/me endpoint with a mocked authenticated admin.
    """
    response = await async_client.get("/api/v1/admin/me")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["username"] == mock_admin_user.username
    assert response_data["email"] == mock_admin_user.email
    assert response_data["id"] == mock_admin_user.id
    assert response_data["is_active"] is True

# It's good practice to clean up the override after the tests in this module are done.
# A more robust way is to use pytest fixtures to apply and clean up the override.
# For this example, this direct override is sufficient to demonstrate the concept.

@pytest.fixture(autouse=True, scope="module")
def cleanup_dependency_override():
    """
    This fixture ensures that the dependency override is removed after all tests
    in this module have run.
    """
    yield
    # Teardown: clean up the dependency override
    app.dependency_overrides.pop(get_current_admin, None)
