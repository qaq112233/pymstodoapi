"""
Authentication and Token Management
"""
import json
import logging
from typing import Optional
from pathlib import Path

from pymstodo.client import ToDoConnection, Token
from .config import settings

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages OAuth authentication and token lifecycle"""
    
    def __init__(self):
        self.client_id = settings.client_id
        self.client_secret = settings.client_secret
        self.token_file = settings.token_file
        self.token: Optional[Token] = None
        self.client: Optional[ToDoConnection] = None
    
    def get_authorization_url(self) -> str:
        """Generate Microsoft OAuth authorization URL"""
        auth_url = ToDoConnection.get_auth_url(self.client_id)
        logger.info("Generated authorization URL")
        return auth_url
    
    def exchange_code_for_token(self, redirect_response: str) -> Token:
        """
        Exchange authorization code for access token
        
        Args:
            redirect_response: The full redirect URL with authorization code
        
        Returns:
            Token object
        """
        try:
            token = ToDoConnection.get_token(
                self.client_id,
                self.client_secret,
                redirect_response
            )
            self.token = token
            self.save_token(token)
            self._initialize_client()
            logger.info("Successfully exchanged code for token")
            return token
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise
    
    def save_token(self, token: Token) -> None:
        """
        Save token to persistent storage
        
        Args:
            token: Token object to save
        """
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token, f, indent=2)
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
                token = json.load(f)
            
            self.token = token
            self._initialize_client()
            logger.info("Token loaded from cache")
            return True
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return False
    
    def clear_token(self) -> None:
        """Clear token from memory and storage"""
        self.token = None
        self.client = None
        
        if self.token_file.exists():
            self.token_file.unlink()
            logger.info("Token cache cleared")
    
    def _initialize_client(self) -> None:
        """Initialize ToDoConnection client with current token"""
        if self.token:
            self.client = ToDoConnection(
                self.client_id,
                self.client_secret,
                self.token
            )
            logger.debug("ToDoConnection client initialized")
    
    def get_client(self) -> ToDoConnection:
        """
        Get initialized ToDoConnection client
        
        Returns:
            ToDoConnection client
        
        Raises:
            ValueError: If not authenticated
        """
        if not self.client:
            raise ValueError("Not authenticated. Please login first.")
        
        # Token refresh is handled internally by pymstodo
        # But we need to save the refreshed token
        old_token = self.token.copy() if self.token else None
        
        # The client will refresh if needed
        # We can check if token changed after any operation
        
        return self.client
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.client is not None and self.token is not None
    
    def update_token_if_changed(self) -> None:
        """Save token if it was refreshed"""
        if self.client and self.token:
            current_token = self.client.token
            # Check if token has changed (was refreshed)
            if current_token != self.token:
                self.token = current_token
                self.save_token(current_token)
                logger.info("Token was refreshed and saved")
