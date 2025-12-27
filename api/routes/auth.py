"""
API Routes - Authentication
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Optional
import logging

from ..models import LoginResponse, TokenResponse
from ..dependencies import get_auth_manager
from ..auth import AuthManager
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/login", response_model=LoginResponse)
async def login(auth_manager: AuthManager = Depends(get_auth_manager)):
    """
    Get Microsoft OAuth authorization URL
    
    Returns:
        Authorization URL for user to visit
    """
    try:
        auth_url = auth_manager.get_authorization_url()
        return LoginResponse(
            authorization_url=auth_url,
            message="Please visit this URL to authorize the application"
        )
    except Exception as e:
        logger.error(f"Failed to generate login URL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate login URL: {str(e)}"
        )


@router.get("/callback-simple")
async def callback_simple(
    url: str = Query(..., description="完整的重定向 URL"),
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """
    OAuth callback endpoint - 简化版（推荐）
    
    直接使用完整的重定向 URL，无需手动提取参数
    
    使用方法：
    1. 在浏览器完成授权后，复制地址栏的完整 URL
    2. 在浏览器访问: http://localhost:8000/auth/callback-simple?url=<完整URL>
    
    示例：
    http://localhost:8000/auth/callback-simple?url=https://localhost/login/authorized?code=xxx&state=yyy
    
    Args:
        url: Microsoft 重定向后的完整 URL
        
    Returns:
        Success HTML page or error page
    """
    # Construct URLs with API prefix (used in both success and error cases)
    api_prefix = settings.api_prefix if settings.api_prefix else ""
    lists_url = f"{api_prefix}/lists"
    docs_url = f"{api_prefix}/docs"
    login_url = f"{api_prefix}/auth/login"
    
    try:
        # Exchange code for token
        token = auth_manager.exchange_code_for_token(url)
        
        logger.info("Authentication successful")
        
        # Return a nice HTML page
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>认证成功</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                }}
                .success-icon {{
                    font-size: 64px;
                    color: #4CAF50;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 10px;
                }}
                p {{
                    color: #666;
                    line-height: 1.6;
                    margin: 10px 0;
                }}
                .button {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }}
                .button:hover {{
                    background: #5568d3;
                }}
                .code {{
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 15px 0;
                    font-family: monospace;
                    color: #333;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✓</div>
                <h1>认证成功！</h1>
                <p>您已成功连接到 Microsoft To Do API</p>
                <p>现在可以开始使用 API 管理您的任务了</p>
                <div class="code">
                    <strong>测试 API：</strong><br>
                    curl http://localhost:8000{lists_url}
                </div>
                <a href="{docs_url}" class="button">查看 API 文档</a>
            </div>
        </body>
        </html>
        """
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>认证失败</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                }}
                .error-icon {{
                    font-size: 64px;
                    color: #f44336;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 10px;
                }}
                p {{
                    color: #666;
                    line-height: 1.6;
                    margin: 10px 0;
                }}
                .error-detail {{
                    background: #ffebee;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    color: #c62828;
                    word-break: break-word;
                }}
                .button {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">✗</div>
                <h1>认证失败</h1>
                <p>无法完成 Microsoft 账户认证</p>
                <div class="error-detail">
                    {str(e)}
                </div>
                <a href="{login_url}" class="button">重新认证</a>
            </div>
        </body>
        </html>
        """
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=error_html, status_code=400)


@router.get("/callback", response_model=TokenResponse)
async def callback(
    code: str = Query(..., description="Authorization code from Microsoft"),
    state: Optional[str] = Query(None, description="State parameter"),
    request: Request = None,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """
    OAuth callback endpoint - 传统方式（使用查询参数）
    
    Args:
        code: Authorization code from Microsoft
        state: State parameter (optional)
        
    Returns:
        Success message
    """
    try:
        # Reconstruct the full redirect URL
        redirect_url = str(request.url)
        
        # Exchange code for token
        token = auth_manager.exchange_code_for_token(redirect_url)
        
        logger.info("Authentication successful")
        return TokenResponse(
            message="Authentication successful! You can now use the API.",
            authenticated=True
        )
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/callback", response_model=TokenResponse)
async def callback_post(
    redirect_url: str,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """
    OAuth callback endpoint - 方式2：直接提交完整 URL
    
    直接提交 Microsoft 重定向后的完整 URL
    
    Request Body:
    {
        "redirect_url": "https://localhost/login/authorized?code=xxx&state=yyy"
    }
    
    Args:
        redirect_url: 完整的重定向 URL
        
    Returns:
        Success message
    """
    try:
        # Exchange code for token using the provided URL
        token = auth_manager.exchange_code_for_token(redirect_url)
        
        logger.info("Authentication successful")
        return TokenResponse(
            message="Authentication successful! You can now use the API.",
            authenticated=True
        )
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Authentication failed: {str(e)}"
        )





@router.post("/logout", response_model=TokenResponse)
async def logout(auth_manager: AuthManager = Depends(get_auth_manager)):
    """
    Logout and clear token cache
    
    Returns:
        Success message
    """
    try:
        auth_manager.clear_token()
        logger.info("Logged out successfully")
        return TokenResponse(
            message="Logged out successfully. Token cache cleared.",
            authenticated=False
        )
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/status")
async def status(auth_manager: AuthManager = Depends(get_auth_manager)):
    """
    Check authentication status
    
    Returns:
        Authentication status
    """
    is_authenticated = auth_manager.is_authenticated()
    return {
        "authenticated": is_authenticated,
        "message": "Authenticated" if is_authenticated else "Not authenticated"
    }
