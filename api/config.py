"""
Configuration management using environment variables
"""
import os
from pathlib import Path
from typing import Optional

# 允许 HTTP 传输（仅用于开发环境）
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # OAuth Configuration
        self.client_id: str = os.getenv("CLIENT_ID", "")
        self.client_secret: str = os.getenv("CLIENT_SECRET", "")
        
        # Microsoft Graph API Configuration
        self.graph_api_version: str = os.getenv("GRAPH_API_VERSION", "beta").lower()
        if self.graph_api_version not in ["v1.0", "beta"]:
            self.graph_api_version = "beta"
        
        # API Configuration
        self.api_prefix: str = os.getenv("API_PREFIX", "")
        self.enable_api_key: bool = os.getenv("ENABLE_API_KEY", "false").lower() == "true"
        self.x_api_key: str = os.getenv("X_API_KEY", "")
        
        # Token Management
        self.token_cache_path: Path = Path(os.getenv("TOKEN_CACHE_PATH", "./token_cache"))
        self.token_cache_path.mkdir(parents=True, exist_ok=True)
        self.token_file: Path = self.token_cache_path / "token.json"
        
        # Server Configuration
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        
    def validate(self) -> bool:
        """Validate required settings"""
        if not self.client_id or not self.client_secret:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be set")
        
        if self.enable_api_key and not self.x_api_key:
            raise ValueError("X_API_KEY must be set when ENABLE_API_KEY is true")
        
        return True


# Global settings instance
settings = Settings()
