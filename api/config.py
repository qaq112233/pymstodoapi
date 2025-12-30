"""
Configuration management using environment variables
"""
import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # OAuth Configuration
        self.client_id: str = os.getenv("CLIENT_ID", "")
        self.client_secret: str = os.getenv("CLIENT_SECRET", "")
        self.redirect_uri: str = os.getenv("REDIRECT_URI", "https://localhost/login/authorized")
        
        # Microsoft Graph API Configuration
        self.graph_api_version: str = os.getenv("GRAPH_API_VERSION", "beta").lower()
        if self.graph_api_version not in ["v1.0", "beta"]:
            self.graph_api_version = "beta"
        
        # API Configuration
        self.api_prefix: str = self._normalize_api_prefix(os.getenv("API_PREFIX", ""))
        self.enable_api_key: bool = os.getenv("ENABLE_API_KEY", "false").lower() == "true"
        self.x_api_key: str = os.getenv("X_API_KEY", "")
        
        # Token Management
        self.token_cache_path: Path = Path(os.getenv("TOKEN_CACHE_PATH", "./token_cache"))
        self.token_cache_path.mkdir(parents=True, exist_ok=True)
        self.token_file: Path = self.token_cache_path / "token.json"
        
        # Server Configuration
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # HTML Rendering Configuration
        self.enable_query_auth: bool = os.getenv("ENABLE_QUERY_AUTH", "false").lower() == "true"
        self.query_passwd: str = os.getenv("QUERY_PASSWD", "")
    
    def _normalize_api_prefix(self, prefix: str) -> str:
        """
        Normalize API prefix to ensure consistent format:
        - Remove leading/trailing slashes
        - Add leading slash if prefix is not empty
        - Return empty string if prefix is empty
        """
        if not prefix:
            return ""
        # Remove leading and trailing slashes
        prefix = prefix.strip().strip('/')
        if not prefix:
            return ""
        # Add leading slash
        return f"/{prefix}"
        
    def validate(self) -> bool:
        """Validate required settings"""
        errors = []
        
        if not self.client_id or not self.client_secret:
            errors.append("CLIENT_ID and CLIENT_SECRET must be set")
        
        # Validate client_id format (should be a GUID)
        if self.client_id and len(self.client_id) < 32:
            errors.append("CLIENT_ID appears to be invalid (too short)")
        
        # Validate client_secret (should be reasonably long)
        if self.client_secret and len(self.client_secret) < 10:
            errors.append("CLIENT_SECRET appears to be invalid (too short)")
        
        if self.enable_api_key:
            if not self.x_api_key:
                errors.append("X_API_KEY must be set when ENABLE_API_KEY is true")
            elif len(self.x_api_key) < 16:
                errors.append("X_API_KEY is too short (minimum 16 characters recommended)")
        
        if self.enable_query_auth:
            if not self.query_passwd:
                errors.append("QUERY_PASSWD must be set when ENABLE_QUERY_AUTH is true")
            elif len(self.query_passwd) < 8:
                errors.append("QUERY_PASSWD is too short (minimum 8 characters recommended)")
        
        if errors:
            raise ValueError("Configuration validation failed:\n  - " + "\n  - ".join(errors))
        
        return True


# Global settings instance
settings = Settings()
