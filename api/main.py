"""
Dockerized MS To Do API Gateway
RESTful API service for Microsoft To Do using pymstodo library
"""
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse, RedirectResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional

from .config import settings
from .auth import AuthManager
from .routes import auth_router, lists_router, tasks_router
from .dependencies import verify_api_key, get_todo_client
from .models import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting MS To Do API Gateway...")
    logger.info(f"API Prefix: {settings.api_prefix}")
    logger.info(f"API Key Protection: {'Enabled' if settings.enable_api_key else 'Disabled'}")
    logger.info(f"Token Cache Path: {settings.token_cache_path}")
    
    # Initialize auth manager
    auth_manager = AuthManager()
    app.state.auth_manager = auth_manager
    
    # Try to load existing token
    if auth_manager.load_token():
        logger.info("Token loaded successfully from cache")
    else:
        logger.warning("No valid token found. Please authenticate via /auth/login")
    
    yield
    
    logger.info("Shutting down MS To Do API Gateway...")


# Create FastAPI app
app = FastAPI(
    title="MS To Do API Gateway",
    description="RESTful API service for Microsoft To Do using pymstodo library",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{settings.api_prefix}/docs" if settings.api_prefix else "/docs",
    redoc_url=f"{settings.api_prefix}/redoc" if settings.api_prefix else "/redoc",
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc)
        }
    )


# Health check endpoint (no auth required)
@app.get(f"{settings.api_prefix}/health" if settings.api_prefix else "/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MS To Do API Gateway",
        "version": "1.0.0"
    }


# Include routers
app.include_router(
    auth_router,
    prefix=f"{settings.api_prefix}/auth" if settings.api_prefix else "/auth",
    tags=["Authentication"]
)

app.include_router(
    lists_router,
    prefix=f"{settings.api_prefix}/lists" if settings.api_prefix else "/lists",
    tags=["Task Lists"],
    dependencies=[Depends(verify_api_key)] if settings.enable_api_key else []
)

app.include_router(
    tasks_router,
    prefix=f"{settings.api_prefix}/tasks" if settings.api_prefix else "/tasks",
    tags=["Tasks"],
    dependencies=[Depends(verify_api_key)] if settings.enable_api_key else []
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
