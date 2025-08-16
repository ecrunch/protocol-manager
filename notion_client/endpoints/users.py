"""
Users endpoint for the Notion API client.

This module provides methods for interacting with Notion users API,
including listing and retrieving user information.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseEndpoint
from ..models.user import User, UserListResponse


logger = logging.getLogger(__name__)


class UsersEndpoint(BaseEndpoint):
    """Users API endpoint handler."""
    
    def list(
        self,
        start_cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> UserListResponse:
        """List all users in the workspace.
        
        Args:
            start_cursor: Pagination cursor
            page_size: Number of items per page
            
        Returns:
            User list response
            
        Raises:
            NotionAPIError: If API request fails
        """
        params = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size
        
        logger.info("Listing users")
        response = self.http_client.get("users", params=params or None)
        
        return UserListResponse(**response)
    
    def list_all(self, page_size: int = 100) -> List[User]:
        """List all users in the workspace (all pages).
        
        Args:
            page_size: Number of items per page
            
        Returns:
            List of all users
            
        Raises:
            NotionAPIError: If API request fails
        """
        users_data = self._get_all_paginated("users", page_size=page_size)
        return [User(**user) for user in users_data]
    
    def retrieve(self, user_id: str) -> User:
        """Retrieve a user by ID.
        
        Args:
            user_id: Notion user ID
            
        Returns:
            User object
            
        Raises:
            NotionNotFoundError: If user is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(user_id, "user")
        
        logger.info(f"Retrieving user: {user_id}")
        response = self.http_client.get(f"users/{user_id}")
        
        return User(**response)
    
    def me(self) -> User:
        """Retrieve the current bot user.
        
        Returns:
            Current bot user object
            
        Raises:
            NotionAuthError: If authentication fails
            NotionAPIError: If API request fails
        """
        logger.info("Retrieving current bot user")
        response = self.http_client.get("users/me")
        
        return User(**response)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by email address.
        
        Args:
            email: User email address
            
        Returns:
            User object if found, None otherwise
            
        Raises:
            NotionAPIError: If API request fails
        """
        users = self.list_all()
        
        for user in users:
            if (user.type == "person" 
                and user.person 
                and user.person.email.lower() == email.lower()):
                return user
        
        return None
    
    def find_by_name(self, name: str, exact_match: bool = False) -> List[User]:
        """Find users by name.
        
        Args:
            name: User name to search for
            exact_match: Whether to do exact name matching
            
        Returns:
            List of matching users
            
        Raises:
            NotionAPIError: If API request fails
        """
        users = self.list_all()
        matching_users = []
        
        for user in users:
            if not user.name:
                continue
            
            if exact_match:
                if user.name == name:
                    matching_users.append(user)
            else:
                if name.lower() in user.name.lower():
                    matching_users.append(user)
        
        return matching_users
    
    def get_workspace_members(self) -> List[User]:
        """Get all workspace members (excluding bots).
        
        Returns:
            List of workspace member users
            
        Raises:
            NotionAPIError: If API request fails
        """
        users = self.list_all()
        return [user for user in users if user.type == "person"]
    
    def get_bots(self) -> List[User]:
        """Get all bot users in the workspace.
        
        Returns:
            List of bot users
            
        Raises:
            NotionAPIError: If API request fails
        """
        users = self.list_all()
        return [user for user in users if user.type == "bot"]
