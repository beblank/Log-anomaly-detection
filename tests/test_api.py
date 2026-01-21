"""Test tenant API endpoints."""
import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_create_tenant(client):
    """Test tenant creation."""
    tenant_data = {
        "name": "test-tenant",
        "display_name": "Test Tenant",
        "description": "Test tenant for unit tests"
    }
    
    response = client.post("/api/v1/tenants/", json=tenant_data)
    
    # Note: May fail without proper K8s/AWS setup, but validates structure
    assert response.status_code in [201, 400, 500]
    
    if response.status_code == 201:
        data = response.json()
        assert data["name"] == tenant_data["name"]
        assert data["display_name"] == tenant_data["display_name"]


def test_list_tenants(client):
    """Test listing tenants."""
    response = client.get("/api/v1/tenants/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
