import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]

def test_readiness_check(client: TestClient):
    """Test readiness check endpoint"""
    response = client.get("/api/v1/health/ready")
    # Note: This might return 503 if services are not ready in test environment
    assert response.status_code in [200, 503]
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data
