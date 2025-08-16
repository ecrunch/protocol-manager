"""
Authentication handling for the Notion API client.

This module provides authentication mechanisms for both Integration Token
and OAuth 2.0 authentication methods.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import requests
from .exceptions import NotionAuthError


logger = logging.getLogger(__name__)


class NotionAuth:
    """Base authentication class."""
    
    def __init__(self) -> None:
        """Initialize base authentication."""
        pass
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests.
        
        Returns:
            Dictionary containing authentication headers
            
        Raises:
            NotionAuthError: If authentication is not properly configured
        """
        raise NotImplementedError("Subclasses must implement get_headers")
    
    def is_valid(self) -> bool:
        """Check if the current authentication is valid.
        
        Returns:
            True if authentication is valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement is_valid")


class IntegrationAuth(NotionAuth):
    """Integration token authentication."""
    
    def __init__(self, token: str) -> None:
        """Initialize integration authentication.
        
        Args:
            token: Notion integration token
            
        Raises:
            NotionAuthError: If token is empty or invalid format
        """
        super().__init__()
        if not token or not token.strip():
            raise NotionAuthError("Integration token cannot be empty")
        
        self.token = token.strip()
        
        # Validate token format (starts with secret_)
        if not self.token.startswith("secret_"):
            logger.warning("Integration token does not start with 'secret_'")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for integration token authentication.
        
        Returns:
            Dictionary containing Bearer token authorization header
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
    
    def is_valid(self) -> bool:
        """Check if integration token is valid format.
        
        Returns:
            True if token appears valid, False otherwise
        """
        return bool(self.token and len(self.token) > 10)


class OAuthAuth(NotionAuth):
    """OAuth 2.0 authentication."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[float] = None,
    ) -> None:
        """Initialize OAuth authentication.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: OAuth redirect URI
            access_token: Current access token
            refresh_token: Refresh token for renewing access
            token_expiry: Unix timestamp when token expires
            
        Raises:
            NotionAuthError: If required OAuth parameters are missing
        """
        super().__init__()
        
        if not all([client_id, client_secret, redirect_uri]):
            raise NotionAuthError(
                "OAuth requires client_id, client_secret, and redirect_uri"
            )
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry
        
        # Notion OAuth endpoints
        self.auth_base_url = "https://api.notion.com/v1/oauth"
        self.token_url = f"{self.auth_base_url}/token"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL for user to visit
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }
        
        if state:
            params["state"] = state
        
        return f"{self.auth_base_url}/authorize?{urlencode(params)}"
    
    def exchange_code(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token.
        
        Args:
            authorization_code: Code received from OAuth callback
            
        Returns:
            Token response containing access_token, refresh_token, etc.
            
        Raises:
            NotionAuthError: If token exchange fails
        """
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
        }
        
        try:
            response = requests.post(
                self.token_url,
                json=data,
                auth=(self.client_id, self.client_secret),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            # Store token information
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            
            # Calculate expiry time
            expires_in = token_data.get("expires_in")
            if expires_in:
                self.token_expiry = time.time() + expires_in
            
            return token_data
            
        except requests.RequestException as e:
            raise NotionAuthError(f"Failed to exchange authorization code: {e}")
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh the access token using refresh token.
        
        Returns:
            New token response
            
        Raises:
            NotionAuthError: If token refresh fails
        """
        if not self.refresh_token:
            raise NotionAuthError("No refresh token available")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        
        try:
            response = requests.post(
                self.token_url,
                json=data,
                auth=(self.client_id, self.client_secret),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            # Update token information
            self.access_token = token_data.get("access_token")
            if "refresh_token" in token_data:
                self.refresh_token = token_data["refresh_token"]
            
            # Calculate new expiry time
            expires_in = token_data.get("expires_in")
            if expires_in:
                self.token_expiry = time.time() + expires_in
            
            return token_data
            
        except requests.RequestException as e:
            raise NotionAuthError(f"Failed to refresh access token: {e}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for OAuth authentication.
        
        Returns:
            Dictionary containing Bearer token authorization header
            
        Raises:
            NotionAuthError: If no valid access token is available
        """
        # Check if token needs refresh
        if self.is_expired() and self.refresh_token:
            logger.info("Access token expired, refreshing...")
            self.refresh_access_token()
        
        if not self.access_token:
            raise NotionAuthError("No valid access token available")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    def is_valid(self) -> bool:
        """Check if OAuth authentication is valid.
        
        Returns:
            True if access token is available and not expired
        """
        return bool(
            self.access_token 
            and not self.is_expired()
        )
    
    def is_expired(self) -> bool:
        """Check if the access token is expired.
        
        Returns:
            True if token is expired, False otherwise
        """
        if not self.token_expiry:
            return False
        
        # Add small buffer (30 seconds) to account for request time
        return time.time() >= (self.token_expiry - 30)


def create_auth_from_env() -> NotionAuth:
    """Create authentication instance from environment variables.
    
    Looks for NOTION_API_TOKEN for integration auth, or OAuth parameters
    for OAuth authentication.
    
    Returns:
        Configured NotionAuth instance
        
    Raises:
        NotionAuthError: If no valid authentication configuration found
    """
    # Try integration token first
    token = os.getenv("NOTION_API_TOKEN")
    if token:
        return IntegrationAuth(token)
    
    # Try OAuth configuration
    client_id = os.getenv("NOTION_OAUTH_CLIENT_ID")
    client_secret = os.getenv("NOTION_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("NOTION_OAUTH_REDIRECT_URI")
    
    if all([client_id, client_secret, redirect_uri]):
        access_token = os.getenv("NOTION_OAUTH_ACCESS_TOKEN")
        refresh_token = os.getenv("NOTION_OAUTH_REFRESH_TOKEN")
        
        token_expiry_str = os.getenv("NOTION_OAUTH_TOKEN_EXPIRY")
        token_expiry = float(token_expiry_str) if token_expiry_str else None
        
        return OAuthAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=token_expiry,
        )
    
    raise NotionAuthError(
        "No valid authentication configuration found. "
        "Set NOTION_API_TOKEN for integration auth or OAuth parameters."
    )
