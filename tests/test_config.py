"""
Tests for configuration module
"""
import pytest
import os
from api.config import Settings


def test_settings_default_values(monkeypatch):
    """Test default configuration values"""
    monkeypatch.setenv("CLIENT_ID", "test_client_id_12345678901234567890")
    monkeypatch.setenv("CLIENT_SECRET", "test_client_secret_1234567890")
    
    settings = Settings()
    assert settings.client_id == "test_client_id_12345678901234567890"
    assert settings.client_secret == "test_client_secret_1234567890"
    assert settings.api_prefix == ""
    assert settings.enable_api_key is False
    assert settings.graph_api_version == "beta"


def test_settings_api_prefix_normalization(monkeypatch):
    """Test API prefix normalization"""
    monkeypatch.setenv("CLIENT_ID", "test_client_id_12345678901234567890")
    monkeypatch.setenv("CLIENT_SECRET", "test_client_secret_1234567890")
    
    # Test with leading slash
    monkeypatch.setenv("API_PREFIX", "/api/v1")
    settings = Settings()
    assert settings.api_prefix == "/api/v1"
    
    # Test without leading slash
    monkeypatch.setenv("API_PREFIX", "api/v1")
    settings = Settings()
    assert settings.api_prefix == "/api/v1"
    
    # Test with trailing slash
    monkeypatch.setenv("API_PREFIX", "/api/v1/")
    settings = Settings()
    assert settings.api_prefix == "/api/v1"
    
    # Test empty prefix
    monkeypatch.setenv("API_PREFIX", "")
    settings = Settings()
    assert settings.api_prefix == ""


def test_settings_validation_success(monkeypatch):
    """Test successful validation"""
    monkeypatch.setenv("CLIENT_ID", "test_client_id_12345678901234567890")
    monkeypatch.setenv("CLIENT_SECRET", "test_client_secret_1234567890")
    
    settings = Settings()
    assert settings.validate() is True


def test_settings_validation_missing_client_id(monkeypatch):
    """Test validation fails with missing client ID"""
    monkeypatch.setenv("CLIENT_ID", "")
    monkeypatch.setenv("CLIENT_SECRET", "test_client_secret_1234567890")
    
    settings = Settings()
    with pytest.raises(ValueError) as exc_info:
        settings.validate()
    assert "CLIENT_ID and CLIENT_SECRET must be set" in str(exc_info.value)


def test_settings_validation_api_key_enabled(monkeypatch):
    """Test validation with API key enabled"""
    monkeypatch.setenv("CLIENT_ID", "test_client_id_12345678901234567890")
    monkeypatch.setenv("CLIENT_SECRET", "test_client_secret_1234567890")
    monkeypatch.setenv("ENABLE_API_KEY", "true")
    monkeypatch.setenv("X_API_KEY", "")
    
    settings = Settings()
    with pytest.raises(ValueError) as exc_info:
        settings.validate()
    assert "X_API_KEY must be set" in str(exc_info.value)


def test_settings_validation_api_key_too_short(monkeypatch):
    """Test validation fails with short API key"""
    monkeypatch.setenv("CLIENT_ID", "test_client_id_12345678901234567890")
    monkeypatch.setenv("CLIENT_SECRET", "test_client_secret_1234567890")
    monkeypatch.setenv("ENABLE_API_KEY", "true")
    monkeypatch.setenv("X_API_KEY", "short")
    
    settings = Settings()
    with pytest.raises(ValueError) as exc_info:
        settings.validate()
    assert "X_API_KEY is too short" in str(exc_info.value)


def test_graph_api_version_validation(monkeypatch):
    """Test Graph API version validation"""
    monkeypatch.setenv("CLIENT_ID", "test_client_id_12345678901234567890")
    monkeypatch.setenv("CLIENT_SECRET", "test_client_secret_1234567890")
    
    # Test valid version
    monkeypatch.setenv("GRAPH_API_VERSION", "v1.0")
    settings = Settings()
    assert settings.graph_api_version == "v1.0"
    
    # Test invalid version defaults to beta
    monkeypatch.setenv("GRAPH_API_VERSION", "invalid")
    settings = Settings()
    assert settings.graph_api_version == "beta"
