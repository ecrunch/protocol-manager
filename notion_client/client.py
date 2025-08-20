"""
Main NotionClient class for the Notion API Python client.

This module provides the primary interface for interacting with the Notion API,
bringing together all endpoint classes and providing a unified client interface.
"""

import os
import logging
from typing import Optional, Union
from dotenv import load_dotenv

from .auth import NotionAuth, IntegrationAuth, OAuthAuth, create_auth_from_env
from .http_client import NotionHTTPClient
from .endpoints import (
    PagesEndpoint,
    BlocksEndpoint,
    DatabasesEndpoint,
    UsersEndpoint,
    SearchEndpoint,
)
from .exceptions import NotionAPIError, NotionAuthError


logger = logging.getLogger(__name__)


class NotionClient:
    """Main Notion API client.
    
    This class provides access to all Notion API endpoints through a unified interface.
    It handles authentication, HTTP requests, rate limiting, and error handling.
    
    Example:
        Basic usage with integration token:
        
        >>> client = NotionClient(auth_token="ntn_...")
        >>> page = client.pages.retrieve("page_id")
        >>> databases = client.search.search_databases("My Database")
        
        Using environment variables:
        
        >>> client = NotionClient.from_env()
        >>> page = client.pages.create(...)
    """
    
    def __init__(
        self,
        auth: Optional[NotionAuth] = None,
        auth_token: Optional[str] = None,
        api_version: str = "2022-06-28",
        base_url: str = "https://api.notion.com/v1/",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_delay: float = 1.0,
        auto_load_env: bool = True,
    ) -> None:
        """Initialize Notion client.
        
        Args:
            auth: NotionAuth instance for authentication
            auth_token: Integration token (alternative to auth parameter)
            api_version: Notion API version to use
            base_url: Base URL for Notion API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            rate_limit_delay: Base delay for rate limiting
            auto_load_env: Whether to automatically load .env file
            
        Raises:
            NotionAuthError: If no valid authentication is provided
        """
        # Load environment variables if requested
        if auto_load_env:
            load_dotenv()
        
        # Set up authentication
        if auth is not None:
            self.auth = auth
        elif auth_token is not None:
            self.auth = IntegrationAuth(auth_token)
        else:
            # Try to create auth from environment
            try:
                self.auth = create_auth_from_env()
            except NotionAuthError:
                raise NotionAuthError(
                    "No authentication provided. Pass auth, auth_token, or set "
                    "environment variables (NOTION_API_TOKEN or OAuth config)."
                )
        
        # Initialize HTTP client
        self.http_client = NotionHTTPClient(
            auth=self.auth,
            api_version=api_version,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_delay=rate_limit_delay,
        )
        
        # Initialize endpoint classes
        self._pages = None
        self._blocks = None
        self._databases = None
        self._users = None
        self._search = None
        
        logger.info(f"NotionClient initialized with API version {api_version}")
    
    @classmethod
    def from_env(
        cls,
        api_version: str = "2022-06-28",
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        rate_limit_delay: Optional[float] = None,
    ) -> "NotionClient":
        """Create NotionClient from environment variables.
        
        Args:
            api_version: Notion API version to use
            timeout: Request timeout in seconds (from env: NOTION_REQUEST_TIMEOUT)
            max_retries: Max retries (from env: NOTION_MAX_RETRIES)
            rate_limit_delay: Rate limit delay (from env: NOTION_RATE_LIMIT_DELAY)
            
        Returns:
            Configured NotionClient instance
            
        Raises:
            NotionAuthError: If no valid authentication found in environment
        """
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment with defaults
        timeout = timeout or int(os.getenv("NOTION_REQUEST_TIMEOUT", "30"))
        max_retries = max_retries or int(os.getenv("NOTION_MAX_RETRIES", "3"))
        rate_limit_delay = rate_limit_delay or float(os.getenv("NOTION_RATE_LIMIT_DELAY", "1.0"))
        api_version = os.getenv("NOTION_API_VERSION", api_version)
        
        return cls(
            api_version=api_version,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_delay=rate_limit_delay,
            auto_load_env=False,  # Already loaded above
        )
    
    @classmethod
    def from_token(
        cls,
        token: str,
        **kwargs,
    ) -> "NotionClient":
        """Create NotionClient with integration token.
        
        Args:
            token: Notion integration token
            **kwargs: Additional client configuration
            
        Returns:
            Configured NotionClient instance
            
        Raises:
            NotionAuthError: If token is invalid
        """
        return cls(auth_token=token, **kwargs)
    
    @classmethod
    def from_oauth(
        cls,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        **kwargs,
    ) -> "NotionClient":
        """Create NotionClient with OAuth authentication.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: OAuth redirect URI
            access_token: Current access token
            refresh_token: Refresh token
            **kwargs: Additional client configuration
            
        Returns:
            Configured NotionClient instance
            
        Raises:
            NotionAuthError: If OAuth configuration is invalid
        """
        auth = OAuthAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        
        return cls(auth=auth, **kwargs)
    
    @property
    def pages(self) -> PagesEndpoint:
        """Access to Pages API endpoints.
        
        Returns:
            PagesEndpoint instance for page operations
        """
        if self._pages is None:
            self._pages = PagesEndpoint(self.http_client)
        return self._pages
    
    @property
    def blocks(self) -> BlocksEndpoint:
        """Access to Blocks API endpoints.
        
        Returns:
            BlocksEndpoint instance for block operations
        """
        if self._blocks is None:
            self._blocks = BlocksEndpoint(self.http_client)
        return self._blocks
    
    @property
    def databases(self) -> DatabasesEndpoint:
        """Access to Databases API endpoints.
        
        Returns:
            DatabasesEndpoint instance for database operations
        """
        if self._databases is None:
            self._databases = DatabasesEndpoint(self.http_client)
        return self._databases
    
    @property
    def users(self) -> UsersEndpoint:
        """Access to Users API endpoints.
        
        Returns:
            UsersEndpoint instance for user operations
        """
        if self._users is None:
            self._users = UsersEndpoint(self.http_client)
        return self._users
    
    @property
    def search(self) -> SearchEndpoint:
        """Access to Search API endpoints.
        
        Returns:
            SearchEndpoint instance for search operations
        """
        if self._search is None:
            self._search = SearchEndpoint(self.http_client)
        return self._search
    
    def test_connection(self) -> bool:
        """Test the connection to Notion API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.users.me()
            logger.info("Connection test successful")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_workspace_info(self) -> dict:
        """Get information about the current workspace.
        
        Returns:
            Dictionary with workspace information
            
        Raises:
            NotionAPIError: If API request fails
        """
        try:
            bot_user = self.users.me()
            workspace_name = None
            
            if bot_user.type == "bot" and bot_user.bot:
                workspace_name = bot_user.bot.workspace_name
            
            return {
                "bot_user": bot_user.dict(),
                "workspace_name": workspace_name,
                "api_version": self.http_client.api_version,
                "connection_status": "connected",
            }
        except Exception as e:
            return {
                "error": str(e),
                "connection_status": "failed",
            }
    
    def set_page_full_width(self, page_id: str, full_width: bool = True) -> bool:
        """Set a page to full width or normal width.
        
        This is a convenience method that attempts to set a page to full width.
        Note: Due to Notion API limitations, this may not always work and manual
        setting in the Notion UI might be required.
        
        Args:
            page_id: Notion page ID
            full_width: Whether to enable full width (True) or normal width (False)
            
        Returns:
            True if the operation completed without errors, False otherwise
            
        Raises:
            NotionAPIError: If API request fails
        """
        try:
            self.pages.set_full_width(page_id, full_width)
            logger.info(f"Set page {page_id} to {'full width' if full_width else 'normal width'}")
            return True
        except Exception as e:
            logger.error(f"Could not set page width: {e}")
            return False
    
    def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        if hasattr(self, 'http_client'):
            self.http_client.close()
        logger.info("NotionClient closed")
    
    def __enter__(self) -> "NotionClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation of the client."""
        auth_type = type(self.auth).__name__
        return f"NotionClient(auth={auth_type}, api_version={self.http_client.api_version})"
