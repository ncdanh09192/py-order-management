import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

@patch('app.cache.redis_client.redis_client.health_check')
def test_health_check(mock_redis_health, client: TestClient):
    """Test health check endpoint"""
    # Mock Redis health check to succeed
    mock_redis_health.return_value = True
    
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]

@patch('app.cache.redis_client.redis_client.health_check')
@patch('app.core.database.health_check_database')
def test_readiness_check_success(mock_db_health, mock_redis_health, client: TestClient):
    """Test readiness check endpoint when services are ready"""
    # Mock successful database health check
    mock_db_health.return_value = True
    
    # Mock successful Redis health check
    mock_redis_health.return_value = True
    
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

@patch('app.core.database.get_database')
def test_readiness_check_database_not_ready(mock_db, client: TestClient):
    """Test readiness check endpoint when database is not ready"""
    # Mock failed database connection
    mock_db.side_effect = Exception("Database connection failed")
    
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    
    data = response.json()
    assert "detail" in data
    assert "not ready" in data["detail"].lower()

def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data
