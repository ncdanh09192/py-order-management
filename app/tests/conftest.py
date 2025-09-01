import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app
from app.core.database import get_database
from app.cache.redis_client import redis_client
from unittest.mock import AsyncMock

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

@pytest.fixture(autouse=True)
def mock_jwt_auth():
    """Mock JWT authentication for all tests"""
    # Mock the security module at the module level
    with patch('app.core.security.verify_access_token') as mock_verify, \
         patch('app.core.auth.get_current_user') as mock_current_user, \
         patch('app.core.auth.get_current_customer_id') as mock_customer_id, \
         patch('app.core.auth.check_order_ownership') as mock_ownership, \
         patch('app.core.security.jwt.decode') as mock_jwt_decode, \
         patch('app.core.config.settings.SECRET_KEY') as mock_secret_key:
        
        # Mock verify_access_token
        mock_verify.return_value = {
            "sub": "123",
            "customer_id": 123,
            "type": "access",
            "exp": 1735716800
        }
        
        # Mock jwt.decode directly
        mock_jwt_decode.return_value = {
            "sub": "123",
            "customer_id": 123,
            "type": "access",
            "exp": 1735716800
        }
        
        # Mock SECRET_KEY to avoid signature verification issues
        mock_secret_key.return_value = "test_secret_key"
        
        # Mock get_current_user
        mock_current_user.return_value = {
            "sub": "123",
            "customer_id": 123,
            "type": "access",
            "exp": 1735716800
        }
        
        # Mock get_current_customer_id
        mock_customer_id.return_value = 123
        
        # Mock check_order_ownership
        mock_ownership.return_value = True
        
        yield mock_verify

@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external services that might be called during tests"""
    with patch('app.core.database.get_database') as mock_db, \
         patch('app.cache.redis_client.redis_client') as mock_redis_client, \
         patch('app.core.database.health_check_database') as mock_db_health, \
         patch('app.events.event_bus.EventBus') as mock_event_bus_class, \
         patch('app.services.order_service.EventBus') as mock_order_event_bus, \
         patch('app.api.orders.event_bus') as mock_api_event_bus, \
         patch('app.api.orders.order_service') as mock_api_order_service, \
         patch('app.api.auth.AuthService') as mock_auth_service_class:
        
        # Mock database for health check
        mock_db_instance = Mock()
        mock_db_instance.execute = AsyncMock(return_value=True)
        mock_db_instance.execute_raw = AsyncMock(return_value=True)
        mock_db.return_value = mock_db_instance
        
        # Mock health_check_database function
        mock_db_health.return_value = True
        
        # Mock EventBus class and instance
        mock_event_bus = Mock()
        mock_event_bus.publish = AsyncMock()
        mock_event_bus_class.return_value = mock_event_bus
        mock_order_event_bus.return_value = mock_event_bus
        mock_api_event_bus.publish = AsyncMock()
        
        # Mock OrderService instance at API level to prevent actual service calls
        mock_api_order_service.create_order = AsyncMock(return_value={
            "id": 1,
            "customerId": 123,
            "orderDate": "2025-01-20T10:00:00",
            "status": "PENDING",
            "totalAmount": 66.00,
            "createdAt": "2025-01-20T10:00:00",
            "updatedAt": "2025-01-20T10:00:00",
            "lines": [
                {
                    "id": 1,
                    "productId": 1001,
                    "quantity": 2,
                    "unitPrice": 25.50,
                    "createdAt": "2025-01-20T10:00:00"
                },
                {
                    "id": 2,
                    "productId": 1002,
                    "quantity": 1,
                    "unitPrice": 15.00,
                    "createdAt": "2025-01-20T10:00:00"
                }
            ]
        })
        mock_api_order_service.get_order_by_id = AsyncMock(return_value={
            "id": 1,
            "customerId": 123,
            "orderDate": "2025-01-20T10:00:00",
            "status": "PENDING",
            "totalAmount": 66.00,
            "createdAt": "2025-01-20T10:00:00",
            "updatedAt": "2025-01-20T10:00:00",
            "lines": [
                {
                    "id": 1,
                    "productId": 1001,
                    "quantity": 2,
                    "unitPrice": 25.50,
                    "createdAt": "2025-01-20T10:00:00"
                }
            ]
        })
        mock_api_order_service.update_order = AsyncMock(return_value={
            "id": 1,
            "customerId": 123,
            "orderDate": "2025-01-20T10:00:00",
            "status": "SHIPPED",
            "totalAmount": 66.00,
            "createdAt": "2025-01-20T10:00:00",
            "updatedAt": "2025-01-20T10:00:00",
            "lines": [
                {
                    "id": 1,
                    "productId": 1001,
                    "quantity": 2,
                    "unitPrice": 25.50,
                    "createdAt": "2025-01-20T10:00:00"
                }
            ]
        })
        mock_api_order_service.delete_order = AsyncMock(return_value=True)
        mock_api_order_service.list_orders = AsyncMock(return_value={
            "orders": [
                {
                    "id": 1,
                    "customerId": 123,
                    "orderDate": "2025-01-20T10:00:00",
                    "status": "PENDING",
                    "totalAmount": 66.00,
                    "createdAt": "2025-01-20T10:00:00",
                    "updatedAt": "2025-01-20T10:00:00",
                    "lines": [
                        {
                            "id": 1,
                            "productId": 1001,
                            "quantity": 2,
                            "unitPrice": 25.50,
                            "createdAt": "2025-01-20T10:00:00"
                        }
                    ]
                }
            ],
            "total": 1,
            "page": 1,
            "size": 10,
            "hasNext": False,
            "hasPrev": False
        })
        
        # Mock AuthService class at API level where it's instantiated
        mock_auth_service = Mock()
        mock_auth_service.login_test = AsyncMock(return_value={
            "accessToken": "mock_access_token",
            "refreshToken": "mock_refresh_token",
            "tokenType": "bearer",
            "expiresIn": 1800,
            "customerId": 123
        })
        mock_auth_service.refresh_token = AsyncMock(return_value={
            "accessToken": "new_access_token",
            "refreshToken": "new_refresh_token",
            "tokenType": "bearer",
            "expiresIn": 1800
        })
        mock_auth_service_class.return_value = mock_auth_service
        
        # Mock Redis client methods including health_check
        mock_redis_client.get = AsyncMock(return_value=None)
        mock_redis_client.set = AsyncMock()
        mock_redis_client.delete = AsyncMock()
        mock_redis_client.exists = AsyncMock(return_value=False)
        mock_redis_client.health_check = AsyncMock(return_value=True)
        
        yield mock_db, mock_db_health, mock_redis_client
