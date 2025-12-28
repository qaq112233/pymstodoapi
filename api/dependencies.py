"""
Dependency injection for FastAPI routes
"""
from fastapi import Header, HTTPException, Request
from typing import Optional

from .graph_client import GraphAPIClient
from .config import settings
from .auth import AuthManager


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-KEY")) -> None:
    """
    Verify API key if enabled
    
    Args:
        x_api_key: API key from request header (X-API-KEY)
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not settings.enable_api_key:
        return
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-KEY header"
        )
    
    if x_api_key != settings.x_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )


async def get_auth_manager(request: Request) -> AuthManager:
    """
    Get auth manager from app state
    
    Args:
        request: FastAPI request object
        
    Returns:
        AuthManager instance
    """
    return request.app.state.auth_manager


async def get_todo_client(request: Request) -> GraphAPIClient:
    """
    Get authenticated GraphAPIClient
    
    Args:
        request: FastAPI request object
        
    Returns:
        GraphAPIClient instance
        
    Raises:
        HTTPException: If not authenticated
    """
    auth_manager: AuthManager = request.app.state.auth_manager
    
    if not auth_manager.is_authenticated():
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please login via /auth/login first."
        )
    
    try:
        client = auth_manager.get_client()
        # Update token if it was refreshed
        auth_manager.update_token_if_changed()
        return client
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Graph API client: {str(e)}"
        )
