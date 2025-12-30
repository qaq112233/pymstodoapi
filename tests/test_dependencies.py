"""
Tests for dependencies module
"""
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from api.dependencies import verify_api_key
from api.config import settings


@pytest.fixture
def app_with_api_key():
    """Create test app with API key protection"""
    app = FastAPI()
    
    @app.get("/protected")
    async def protected_endpoint(_: None = Depends(verify_api_key)):
        return {"message": "protected"}
    
    return app


def test_verify_api_key_disabled(app_with_api_key, monkeypatch):
    """Test that API key verification is skipped when disabled"""
    monkeypatch.setattr(settings, "enable_api_key", False)
    
    client = TestClient(app_with_api_key)
    response = client.get("/protected")
    assert response.status_code == 200


def test_verify_api_key_missing(app_with_api_key, monkeypatch):
    """Test that missing API key returns 401"""
    monkeypatch.setattr(settings, "enable_api_key", True)
    monkeypatch.setattr(settings, "x_api_key", "test_key_1234567890")
    
    client = TestClient(app_with_api_key)
    response = client.get("/protected")
    assert response.status_code == 401
    assert "Missing X-API-KEY header" in response.json()["detail"]


def test_verify_api_key_invalid(app_with_api_key, monkeypatch):
    """Test that invalid API key returns 403"""
    monkeypatch.setattr(settings, "enable_api_key", True)
    monkeypatch.setattr(settings, "x_api_key", "correct_key_1234567890")
    
    client = TestClient(app_with_api_key)
    response = client.get("/protected", headers={"X-API-KEY": "wrong_key"})
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]


def test_verify_api_key_valid(app_with_api_key, monkeypatch):
    """Test that valid API key allows access"""
    api_key = "correct_key_1234567890"
    monkeypatch.setattr(settings, "enable_api_key", True)
    monkeypatch.setattr(settings, "x_api_key", api_key)
    
    client = TestClient(app_with_api_key)
    response = client.get("/protected", headers={"X-API-KEY": api_key})
    assert response.status_code == 200
