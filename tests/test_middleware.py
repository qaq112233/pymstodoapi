"""
Tests for middleware
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.middleware import SecurityHeadersMiddleware, RateLimitMiddleware


@pytest.fixture
def app_with_security():
    """Create test app with security middleware"""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    return app


@pytest.fixture
def app_with_rate_limit():
    """Create test app with rate limiting"""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, requests_per_minute=5)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    @app.get("/health")
    async def health_endpoint():
        return {"status": "healthy"}
    
    return app


def test_security_headers(app_with_security):
    """Test that security headers are added"""
    client = TestClient(app_with_security)
    response = client.get("/test")
    
    assert response.status_code == 200
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "X-XSS-Protection" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers
    assert "Referrer-Policy" in response.headers


def test_rate_limit_allows_requests(app_with_rate_limit):
    """Test that rate limit allows requests within limit"""
    client = TestClient(app_with_rate_limit)
    
    # Make 5 requests (within limit)
    for i in range(5):
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers


def test_rate_limit_blocks_excessive_requests(app_with_rate_limit):
    """Test that rate limit blocks excessive requests"""
    client = TestClient(app_with_rate_limit)
    
    # Make 6 requests (exceeds limit of 5)
    for i in range(5):
        response = client.get("/test")
        assert response.status_code == 200
    
    # 6th request should be blocked
    response = client.get("/test")
    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_rate_limit_skips_health_check(app_with_rate_limit):
    """Test that rate limit doesn't apply to health check"""
    client = TestClient(app_with_rate_limit)
    
    # Make many requests to health endpoint
    for i in range(10):
        response = client.get("/health")
        assert response.status_code == 200
