"""
Custom exceptions for the Notion Python client.

This module defines all custom exceptions used throughout the Notion client,
providing specific error types for different API scenarios.
"""

from typing import Any, Dict, Optional


class NotionAPIError(Exception):
    """Base exception for all Notion API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize NotionAPIError.
        
        Args:
            message: Error message describing what went wrong
            status_code: HTTP status code from the API response
            response_data: Raw response data from the API
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class NotionAuthError(NotionAPIError):
    """Authentication-related errors (401, 403)."""
    
    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize NotionAuthError.
        
        Args:
            message: Error message describing the authentication failure
        """
        super().__init__(message, status_code=401)


class NotionRateLimitError(NotionAPIError):
    """Rate limit exceeded error (429)."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ) -> None:
        """Initialize NotionRateLimitError.
        
        Args:
            message: Error message about rate limiting
            retry_after: Number of seconds to wait before retrying
        """
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class NotionValidationError(NotionAPIError):
    """Data validation errors (400)."""
    
    def __init__(self, message: str, validation_errors: Optional[list] = None) -> None:
        """Initialize NotionValidationError.
        
        Args:
            message: Error message about validation failure
            validation_errors: List of specific validation errors
        """
        super().__init__(message, status_code=400)
        self.validation_errors = validation_errors or []


class NotionConnectionError(NotionAPIError):
    """Network connection errors."""
    
    def __init__(self, message: str = "Connection error occurred") -> None:
        """Initialize NotionConnectionError.
        
        Args:
            message: Error message about the connection issue
        """
        super().__init__(message)


class NotionNotFoundError(NotionAPIError):
    """Resource not found error (404)."""
    
    def __init__(self, message: str = "Resource not found") -> None:
        """Initialize NotionNotFoundError.
        
        Args:
            message: Error message about the missing resource
        """
        super().__init__(message, status_code=404)


class NotionConflictError(NotionAPIError):
    """Resource conflict error (409)."""
    
    def __init__(self, message: str = "Resource conflict occurred") -> None:
        """Initialize NotionConflictError.
        
        Args:
            message: Error message about the resource conflict
        """
        super().__init__(message, status_code=409)
