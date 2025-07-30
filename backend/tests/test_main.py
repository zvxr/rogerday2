import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Patient Dashboard API", "version": "1.0.0"}


def test_status_endpoint():
    """Test the status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "Patient Dashboard API is running"}


def test_login_endpoint():
    """Test the login endpoint"""
    response = client.post("/auth/login", json={"username": "test", "password": "test"})
    assert response.status_code == 401  # Should fail with invalid credentials


def test_patients_endpoint_unauthorized():
    """Test the patients endpoint without authentication"""
    response = client.get("/patients")
    assert response.status_code == 401  # Should require authentication 