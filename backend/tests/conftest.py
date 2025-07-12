import pytest
from httpx import AsyncClient
import asyncio

# Import your FastAPI app
# We need to adjust the path to import from the 'app' module
import sys
import os

# Add the parent directory to the path to allow imports from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.database import get_db, Base, engine

# To run tests on a separate, temporary database, you would configure a test database URL
# and override the get_db dependency. For this example, we'll test against the configured dev DB,
# but a separate test DB is best practice.
#
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # Use an in-memory SQLite DB for tests
# test_engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
#
# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()
#
# app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # This fixture will run once per test session.
    # It creates all tables before tests run and drops them after.
    # Best practice is to use a separate test database.
    print("\nSetting up test database...")
    Base.metadata.create_all(bind=engine)
    yield
    print("\nTearing down test database...")
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def async_client() -> AsyncClient:
    """
    A fixture that provides an httpx.AsyncClient for making requests to the test app.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
