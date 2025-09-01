import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_database
from app.cache.redis_client import redis_client

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
async def db():
    """Get database connection for testing."""
    return await get_database()

@pytest.fixture
async def redis():
    """Get Redis client for testing."""
    return redis_client
