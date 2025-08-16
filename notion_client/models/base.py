"""
Base models and common data structures for the Notion API client.

This module contains the foundational Pydantic models that are used across
all other model types in the Notion API.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class NotionObject(BaseModel):
    """Base class for all Notion objects."""
    
    object: str
    id: str
    created_time: datetime
    last_edited_time: datetime
    created_by: Optional[Dict[str, Any]] = None
    last_edited_by: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
        validate_assignment = True


class RichTextAnnotations(BaseModel):
    """Text formatting annotations."""
    
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"


class RichText(BaseModel):
    """Rich text object used throughout Notion."""
    
    type: Literal["text", "mention", "equation"]
    annotations: RichTextAnnotations = Field(default_factory=RichTextAnnotations)
    plain_text: str
    href: Optional[str] = None
    
    # Type-specific fields
    text: Optional[Dict[str, Any]] = None
    mention: Optional[Dict[str, Any]] = None
    equation: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class Parent(BaseModel):
    """Parent reference for pages and blocks."""
    
    type: Literal["database_id", "page_id", "workspace", "block_id"]
    database_id: Optional[str] = None
    page_id: Optional[str] = None
    block_id: Optional[str] = None
    workspace: Optional[bool] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class File(BaseModel):
    """File object for file properties and block content."""
    
    type: Literal["external", "file"]
    name: Optional[str] = None
    
    # Type-specific fields
    external: Optional[Dict[str, str]] = None  # Contains 'url'
    file: Optional[Dict[str, str]] = None      # Contains 'url' and 'expiry_time'
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class Icon(BaseModel):
    """Icon object for pages and databases."""
    
    type: Literal["emoji", "external", "file"]
    emoji: Optional[str] = None
    external: Optional[Dict[str, str]] = None  # Contains 'url'
    file: Optional[Dict[str, str]] = None      # Contains 'url' and 'expiry_time'
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class Cover(BaseModel):
    """Cover image object for pages."""
    
    type: Literal["external", "file"]
    external: Optional[Dict[str, str]] = None  # Contains 'url'
    file: Optional[Dict[str, str]] = None      # Contains 'url' and 'expiry_time'
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class SelectOption(BaseModel):
    """Option for select and multi-select properties."""
    
    id: Optional[str] = None
    name: str
    color: str = "default"
    description: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class FormulaResult(BaseModel):
    """Result of a formula property."""
    
    type: Literal["string", "number", "boolean", "date"]
    string: Optional[str] = None
    number: Optional[float] = None
    boolean: Optional[bool] = None
    date: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class RollupResult(BaseModel):
    """Result of a rollup property."""
    
    type: Literal["number", "date", "array", "unsupported", "incomplete"]
    number: Optional[float] = None
    date: Optional[Dict[str, Any]] = None
    array: Optional[List[Dict[str, Any]]] = None
    function: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
