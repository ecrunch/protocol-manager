"""
HTTP client for the Notion API with rate limiting and retry logic.

This module provides a robust HTTP client that handles rate limiting,
retries with exponential backoff, and proper error handling for the Notion API.
"""

import time
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import NotionAuth
from .exceptions import (
    NotionAPIError,
    NotionAuthError,
    NotionRateLimitError,
    NotionValidationError,
    NotionConnectionError,
    NotionNotFoundError,
    NotionConflictError,
)


logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests_per_second: float = 3.0) -> None:
        """Initialize rate limiter.
        
        Args:
            max_requests_per_second: Maximum requests per second allowed
        """
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0.0
    
    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.3f} seconds")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()


class NotionHTTPClient:
    """HTTP client for Notion API with rate limiting and retry logic."""
    
    def __init__(
        self,
        auth: NotionAuth,
        api_version: str = "2022-06-28",
        base_url: str = "https://api.notion.com/v1/",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_delay: float = 1.0,
    ) -> None:
        """Initialize HTTP client.
        
        Args:
            auth: Authentication instance
            api_version: Notion API version to use
            base_url: Base URL for Notion API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            rate_limit_delay: Base delay for rate limiting
        """
        self.auth = auth
        self.api_version = api_version
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(max_requests_per_second=3.0)
        
        # Create requests session with retry strategy
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PATCH", "DELETE"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including authentication.
        
        Returns:
            Dictionary of headers for API requests
        """
        headers = self.auth.get_headers()
        headers.update({
            "Notion-Version": self.api_version,
            "User-Agent": "notion-python-client/0.1.0",
        })
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions.
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed JSON response data
            
        Raises:
            NotionAPIError: For various API error conditions
        """
        try:
            response_data = response.json()
        except ValueError:
            response_data = {"message": response.text}
        
        # Handle successful responses
        if response.status_code < 400:
            return response_data
        
        # Extract error message
        error_message = response_data.get("message", "Unknown error occurred")
        
        # Handle specific error status codes
        if response.status_code == 400:
            validation_errors = response_data.get("details", {}).get("errors", [])
            raise NotionValidationError(error_message, validation_errors)
        
        elif response.status_code == 401:
            raise NotionAuthError(error_message)
        
        elif response.status_code == 403:
            raise NotionAuthError(f"Access forbidden: {error_message}")
        
        elif response.status_code == 404:
            raise NotionNotFoundError(error_message)
        
        elif response.status_code == 409:
            raise NotionConflictError(error_message)
        
        elif response.status_code == 429:
            # Extract retry-after header if available
            retry_after = response.headers.get("Retry-After")
            retry_after_seconds = int(retry_after) if retry_after else None
            raise NotionRateLimitError(error_message, retry_after_seconds)
        
        else:
            # Generic API error for other status codes
            raise NotionAPIError(
                error_message,
                status_code=response.status_code,
                response_data=response_data,
            )
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with rate limiting and error handling.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            data: JSON data for request body
            params: Query parameters
            
        Returns:
            Parsed response data
            
        Raises:
            NotionAPIError: For API errors
            NotionConnectionError: For connection errors
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Construct full URL
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        
        # Get headers
        headers = self._get_headers()
        
        # Log request details
        logger.debug(f"Making {method} request to {url}")
        if data:
            logger.debug(f"Request data: {data}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            
            # Handle response
            return self._handle_response(response)
            
        except requests.exceptions.ConnectionError as e:
            raise NotionConnectionError(f"Connection error: {e}")
        
        except requests.exceptions.Timeout as e:
            raise NotionConnectionError(f"Request timeout: {e}")
        
        except requests.exceptions.RequestException as e:
            raise NotionConnectionError(f"Request failed: {e}")
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make GET request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Parsed response data
        """
        return self._make_request("GET", endpoint, params=params)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make POST request.
        
        Args:
            endpoint: API endpoint path
            data: JSON data for request body
            params: Query parameters
            
        Returns:
            Parsed response data
        """
        return self._make_request("POST", endpoint, data=data, params=params)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make PATCH request.
        
        Args:
            endpoint: API endpoint path
            data: JSON data for request body
            params: Query parameters
            
        Returns:
            Parsed response data
        """
        return self._make_request("PATCH", endpoint, data=data, params=params)
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make DELETE request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Parsed response data
        """
        return self._make_request("DELETE", endpoint, params=params)
    
    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
