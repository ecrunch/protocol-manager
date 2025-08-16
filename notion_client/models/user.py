"""
User-related models for the Notion API client.

This module contains Pydantic models for Notion users and user types.
"""

from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class UserType(BaseModel):
    """User type discriminator."""
    
    type: Literal["person", "bot"]
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class Person(BaseModel):
    """Person user details."""
    
    email: str
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class Bot(BaseModel):
    """Bot user details."""
    
    owner: Dict[str, Any] = Field(default_factory=dict)
    workspace_name: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class User(BaseModel):
    """Notion user object."""
    
    object: str = "user"
    id: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    type: Literal["person", "bot"]
    
    # Type-specific fields
    person: Optional[Person] = None
    bot: Optional[Bot] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class UserListResponse(BaseModel):
    """Response model for listing users."""
    
    object: str = "list"
    results: list[User] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    has_more: bool = False
    type: str = "user"
    user: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
