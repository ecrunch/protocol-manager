"""
Base endpoint class for Notion API endpoints.

This module provides the base class that all endpoint classes inherit from,
providing common functionality for API operations.
"""

import logging
from typing import Any, Dict, List, Optional, Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http_client import NotionHTTPClient


logger = logging.getLogger(__name__)


class BaseEndpoint:
    """Base class for all API endpoints."""
    
    def __init__(self, http_client: "NotionHTTPClient") -> None:
        """Initialize base endpoint.
        
        Args:
            http_client: HTTP client instance for making requests
        """
        self.http_client = http_client
    
    def _paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        page_size: int = 100,
    ) -> Generator[Dict[str, Any], None, None]:
        """Paginate through API results.
        
        Args:
            endpoint: API endpoint to paginate
            params: Query parameters
            data: Request body data (for POST requests)
            method: HTTP method to use
            page_size: Number of items per page
            
        Yields:
            Individual items from paginated results
        """
        if params is None:
            params = {}
        
        if data is None:
            data = {}
        
        # Set page size
        if method == "POST":
            data["page_size"] = page_size
        else:
            params["page_size"] = page_size
        
        next_cursor = None
        
        while True:
            # Add cursor to request
            if next_cursor:
                if method == "POST":
                    data["start_cursor"] = next_cursor
                else:
                    params["start_cursor"] = next_cursor
            
            # Make request
            if method == "POST":
                response = self.http_client.post(endpoint, data=data, params=params)
            else:
                response = self.http_client.get(endpoint, params=params)
            
            # Yield results
            results = response.get("results", [])
            for item in results:
                yield item
            
            # Check if there are more pages
            if not response.get("has_more", False):
                break
            
            next_cursor = response.get("next_cursor")
            if not next_cursor:
                break
    
    def _get_all_paginated(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get all items from a paginated endpoint.
        
        Args:
            endpoint: API endpoint to query
            params: Query parameters
            data: Request body data (for POST requests)
            method: HTTP method to use
            page_size: Number of items per page
            
        Returns:
            List of all items from all pages
        """
        return list(self._paginate(
            endpoint=endpoint,
            params=params,
            data=data,
            method=method,
            page_size=page_size,
        ))
    
    def _validate_id(self, object_id: str, object_type: str = "object") -> None:
        """Validate that an ID is properly formatted.
        
        Args:
            object_id: ID to validate
            object_type: Type of object (for error messages)
            
        Raises:
            ValueError: If ID is invalid
        """
        if not object_id or not isinstance(object_id, str):
            raise ValueError(f"Invalid {object_type} ID: must be a non-empty string")
        
        # Remove dashes for length check
        clean_id = object_id.replace("-", "")
        
        # Notion IDs should be 32 characters (UUID format)
        if len(clean_id) != 32:
            raise ValueError(
                f"Invalid {object_type} ID format: expected 32 characters, "
                f"got {len(clean_id)}"
            )
    
    def _clean_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values from dictionary.
        
        Args:
            data: Dictionary to clean
            
        Returns:
            Dictionary with None values removed
        """
        return {k: v for k, v in data.items() if v is not None}
