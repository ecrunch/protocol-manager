"""
Page-related models for the Notion API client.

This module contains Pydantic models for Notion pages and their properties.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .base import NotionObject, Parent, Icon, Cover, RichText


class PageProperty(BaseModel):
    """Base class for page properties."""
    
    id: str
    type: str
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class TitleProperty(PageProperty):
    """Title property for pages."""
    
    type: str = "title"
    title: List[RichText] = Field(default_factory=list)


class RichTextProperty(PageProperty):
    """Rich text property for pages."""
    
    type: str = "rich_text"
    rich_text: List[RichText] = Field(default_factory=list)


class NumberProperty(PageProperty):
    """Number property for pages."""
    
    type: str = "number"
    number: Optional[float] = None


class SelectProperty(PageProperty):
    """Select property for pages."""
    
    type: str = "select"
    select: Optional[Dict[str, Any]] = None


class MultiSelectProperty(PageProperty):
    """Multi-select property for pages."""
    
    type: str = "multi_select"
    multi_select: List[Dict[str, Any]] = Field(default_factory=list)


class DateProperty(PageProperty):
    """Date property for pages."""
    
    type: str = "date"
    date: Optional[Dict[str, Any]] = None


class CheckboxProperty(PageProperty):
    """Checkbox property for pages."""
    
    type: str = "checkbox"
    checkbox: bool = False


class UrlProperty(PageProperty):
    """URL property for pages."""
    
    type: str = "url"
    url: Optional[str] = None


class EmailProperty(PageProperty):
    """Email property for pages."""
    
    type: str = "email"
    email: Optional[str] = None


class PhoneNumberProperty(PageProperty):
    """Phone number property for pages."""
    
    type: str = "phone_number"
    phone_number: Optional[str] = None


class FilesProperty(PageProperty):
    """Files property for pages."""
    
    type: str = "files"
    files: List[Dict[str, Any]] = Field(default_factory=list)


class PeopleProperty(PageProperty):
    """People property for pages."""
    
    type: str = "people"
    people: List[Dict[str, Any]] = Field(default_factory=list)


class RelationProperty(PageProperty):
    """Relation property for pages."""
    
    type: str = "relation"
    relation: List[Dict[str, str]] = Field(default_factory=list)  # List of page references


class FormulaProperty(PageProperty):
    """Formula property for pages."""
    
    type: str = "formula"
    formula: Optional[Dict[str, Any]] = None


class RollupProperty(PageProperty):
    """Rollup property for pages."""
    
    type: str = "rollup"
    rollup: Optional[Dict[str, Any]] = None


class CreatedTimeProperty(PageProperty):
    """Created time property for pages."""
    
    type: str = "created_time"
    created_time: str


class CreatedByProperty(PageProperty):
    """Created by property for pages."""
    
    type: str = "created_by"
    created_by: Dict[str, Any]


class LastEditedTimeProperty(PageProperty):
    """Last edited time property for pages."""
    
    type: str = "last_edited_time"
    last_edited_time: str


class LastEditedByProperty(PageProperty):
    """Last edited by property for pages."""
    
    type: str = "last_edited_by"
    last_edited_by: Dict[str, Any]


class Page(NotionObject):
    """Notion page object."""
    
    object: str = "page"
    parent: Parent
    properties: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    icon: Optional[Icon] = None
    cover: Optional[Cover] = None
    archived: bool = False
    in_trash: bool = False
    url: str
    public_url: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class PageCreateRequest(BaseModel):
    """Request model for creating a new page."""
    
    parent: Parent
    properties: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    children: Optional[List[Dict[str, Any]]] = None
    icon: Optional[Icon] = None
    cover: Optional[Cover] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class PageUpdateRequest(BaseModel):
    """Request model for updating a page."""
    
    properties: Optional[Dict[str, Dict[str, Any]]] = None
    archived: Optional[bool] = None
    in_trash: Optional[bool] = None
    icon: Optional[Icon] = None
    cover: Optional[Cover] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
