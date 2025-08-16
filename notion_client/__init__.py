"""
Notion Python Client

A comprehensive Python client for the Notion API that provides access to all 
Notion API endpoints with proper error handling, rate limiting, and data validation.
"""

from .client import NotionClient
from .exceptions import (
    NotionAPIError,
    NotionAuthError,
    NotionRateLimitError,
    NotionValidationError,
    NotionConnectionError,
    NotionNotFoundError,
    NotionConflictError,
)

__version__ = "0.1.0"
__all__ = [
    "NotionClient",
    "NotionAPIError",
    "NotionAuthError", 
    "NotionRateLimitError",
    "NotionValidationError",
    "NotionConnectionError",
    "NotionNotFoundError",
    "NotionConflictError",
]
