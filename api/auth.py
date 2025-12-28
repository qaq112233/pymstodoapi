"""
Authentication and Token Management using MSAL
"""
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

import msal
from .config import settings
from .graph_client import GraphAPIClient

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages OAuth authentication and token lifecycle using MSAL"""
    
    # Microsoft Graph API scopes for To Do
    SCOPES = [
        "Tasks.ReadWrite",
        "Tasks.ReadWrite.Shared",
        "User.Read",
        "offline_access"
    ]
    
    # OAuth endpoints
    AUTHORITY = "https://login.microsoftonline.com/common"
    REDIRECT_URI = "https://localhost/login/authorized"
    
    def __init__(self):
        self.client_id = settings.client_id
        self.client_secret = settings.client_secret
        self.token_file = settings.token_file
        self.api_version = settings.graph_api_version
        self.token_cache = msal.SerializableTokenCache()
        self.token_data: Optional[Dict[str, Any]] = None
        self.client: Optional[GraphAPIClient] = None
        self.msal_app: Optional[msal.ConfidentialClientApplication] = None
    
    def _get_msal_app(self) -> msal.ConfidentialClientApplication:
        """Lazy initialization of MSAL app to avoid network calls at startup"""
        if self.msal_app is None:
            self.msal_app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.AUTHORITY,
                token_cache=self.token_cache
            )
        return self.msal_app
    
    def get_authorization_url(self) -> str:
        """
        Generate Microsoft OAuth authorization URL
        
        Returns:
            Authorization URL for user to visit
        """
        auth_url = self._get_msal_app().get_authorization_request_url(
            scopes=self.SCOPES,
            redirect_uri=self.REDIRECT_URI
        )
        logger.info("Generated authorization URL")
        return auth_url
    
    def exchange_code_for_token(self, redirect_response: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            redirect_response: The full redirect URL with authorization code
        
        Returns:
            Token data dictionary
        """
        try:
            # Extract authorization code from redirect URL
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(redirect_response)
            query_params = parse_qs(parsed.query)
            
            if 'code' not in query_params:
                raise ValueError("No authorization code found in redirect URL")
            
            code = query_params['code'][0]
            
            # Exchange code for token
            result = self._get_msal_app().acquire_token_by_authorization_code(
                code=code,
                scopes=self.SCOPES,
                redirect_uri=self.REDIRECT_URI
            )
            
            if "error" in result:
                error_msg = result.get("error_description", result.get("error"))
                logger.error(f"Token exchange failed: {error_msg}")
                raise ValueError(f"Token exchange failed: {error_msg}")
            
            self.token_data = result
            self.save_token(result)
            self._initialize_client()
            logger.info("Successfully exchanged code for token")
            return result
            
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise
    
    def save_token(self, token: Dict[str, Any]) -> None:
        """
        Save token to persistent storage
        
        Args:
            token: Token data dictionary to save
        """
        try:
            # Save both token data and cache
            save_data = {
                'token': token,
                'cache': self.token_cache.serialize()
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            logger.info(f"Token saved to {self.token_file}")
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
            raise
    
    def load_token(self) -> bool:
        """
        Load token from persistent storage
        
        Returns:
            True if token loaded successfully, False otherwise
        """
        try:
            if not self.token_file.exists():
                logger.warning("Token file does not exist")
                return False
            
            with open(self.token_file, 'r') as f:
                save_data = json.load(f)
            
            # Load token data
            self.token_data = save_data.get('token')
            
            # Load token cache if available
            if 'cache' in save_data:
                self.token_cache.deserialize(save_data['cache'])
            
            # Try to get a valid token (will refresh if needed)
            accounts = self._get_msal_app().get_accounts()
            if accounts:
                # Try silent token acquisition
                result = self._get_msal_app().acquire_token_silent(
                    scopes=self.SCOPES,
                    account=accounts[0]
                )
                
                if result and "access_token" in result:
                    self.token_data = result
                    self.save_token(result)
                    self._initialize_client()
                    logger.info("Token loaded and refreshed from cache")
                    return True
            
            # If we have token data but silent acquisition failed, try to initialize anyway
            if self.token_data and 'access_token' in self.token_data:
                self._initialize_client()
                logger.info("Token loaded from cache")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return False
    
    def clear_token(self) -> None:
        """Clear token from memory and storage"""
        self.token_data = None
        self.client = None
        self.token_cache = msal.SerializableTokenCache()
        
        if self.token_file.exists():
            self.token_file.unlink()
            logger.info("Token cache cleared")
    
    def _initialize_client(self) -> None:
        """Initialize GraphAPIClient with current token"""
        if self.token_data and 'access_token' in self.token_data:
            self.client = GraphAPIClient(
                access_token=self.token_data['access_token'],
                api_version=self.api_version
            )
            logger.debug("GraphAPIClient initialized")
    
    def _refresh_token_if_needed(self) -> None:
        """Refresh token if it's expired or about to expire"""
        if not self.token_data:
            return
        
        # Check if we need to refresh
        accounts = self._get_msal_app().get_accounts()
        if accounts:
            result = self._get_msal_app().acquire_token_silent(
                scopes=self.SCOPES,
                account=accounts[0]
            )
            
            if result and "access_token" in result:
                # Token was refreshed
                if result.get('access_token') != self.token_data.get('access_token'):
                    logger.info("Token refreshed")
                    self.token_data = result
                    self.save_token(result)
                    self._initialize_client()
    
    def get_client(self) -> GraphAPIClient:
        """
        Get initialized GraphAPIClient
        
        Returns:
            GraphAPIClient instance
        
        Raises:
            ValueError: If not authenticated
        """
        if not self.client:
            raise ValueError("Not authenticated. Please login first.")
        
        # Refresh token if needed
        self._refresh_token_if_needed()
        
        return self.client
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.client is not None and self.token_data is not None
    
    def update_token_if_changed(self) -> None:
        """Check and save token if it was refreshed"""
        # This is now handled in _refresh_token_if_needed
        self._refresh_token_if_needed()

