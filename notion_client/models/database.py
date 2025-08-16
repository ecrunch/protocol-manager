"""
Database-related models for the Notion API client.

This module contains Pydantic models for Notion databases and their properties.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from .base import NotionObject, Parent, Icon, Cover, RichText, SelectOption


class DatabaseProperty(BaseModel):
    """Base class for database properties."""
    
    id: str
    name: str
    type: str
    description: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class TitleDatabaseProperty(DatabaseProperty):
    """Title property configuration."""
    
    type: str = "title"
    title: Dict[str, Any] = Field(default_factory=dict)


class RichTextDatabaseProperty(DatabaseProperty):
    """Rich text property configuration."""
    
    type: str = "rich_text"
    rich_text: Dict[str, Any] = Field(default_factory=dict)


class NumberDatabaseProperty(DatabaseProperty):
    """Number property configuration."""
    
    type: str = "number"
    number: Dict[str, str] = Field(default_factory=dict)  # Contains 'format'


class SelectDatabaseProperty(DatabaseProperty):
    """Select property configuration."""
    
    type: str = "select"
    select: Dict[str, List[SelectOption]] = Field(default_factory=dict)


class MultiSelectDatabaseProperty(DatabaseProperty):
    """Multi-select property configuration."""
    
    type: str = "multi_select"
    multi_select: Dict[str, List[SelectOption]] = Field(default_factory=dict)


class DateDatabaseProperty(DatabaseProperty):
    """Date property configuration."""
    
    type: str = "date"
    date: Dict[str, Any] = Field(default_factory=dict)


class CheckboxDatabaseProperty(DatabaseProperty):
    """Checkbox property configuration."""
    
    type: str = "checkbox"
    checkbox: Dict[str, Any] = Field(default_factory=dict)


class UrlDatabaseProperty(DatabaseProperty):
    """URL property configuration."""
    
    type: str = "url"
    url: Dict[str, Any] = Field(default_factory=dict)


class EmailDatabaseProperty(DatabaseProperty):
    """Email property configuration."""
    
    type: str = "email"
    email: Dict[str, Any] = Field(default_factory=dict)


class PhoneNumberDatabaseProperty(DatabaseProperty):
    """Phone number property configuration."""
    
    type: str = "phone_number"
    phone_number: Dict[str, Any] = Field(default_factory=dict)


class FilesDatabaseProperty(DatabaseProperty):
    """Files property configuration."""
    
    type: str = "files"
    files: Dict[str, Any] = Field(default_factory=dict)


class PeopleDatabaseProperty(DatabaseProperty):
    """People property configuration."""
    
    type: str = "people"
    people: Dict[str, Any] = Field(default_factory=dict)


class RelationDatabaseProperty(DatabaseProperty):
    """Relation property configuration."""
    
    type: str = "relation"
    relation: Dict[str, Any] = Field(default_factory=dict)  # Contains database_id, etc.


class FormulaDatabaseProperty(DatabaseProperty):
    """Formula property configuration."""
    
    type: str = "formula"
    formula: Dict[str, str] = Field(default_factory=dict)  # Contains 'expression'


class RollupDatabaseProperty(DatabaseProperty):
    """Rollup property configuration."""
    
    type: str = "rollup"
    rollup: Dict[str, Any] = Field(default_factory=dict)


class CreatedTimeDatabaseProperty(DatabaseProperty):
    """Created time property configuration."""
    
    type: str = "created_time"
    created_time: Dict[str, Any] = Field(default_factory=dict)


class CreatedByDatabaseProperty(DatabaseProperty):
    """Created by property configuration."""
    
    type: str = "created_by"
    created_by: Dict[str, Any] = Field(default_factory=dict)


class LastEditedTimeDatabaseProperty(DatabaseProperty):
    """Last edited time property configuration."""
    
    type: str = "last_edited_time"
    last_edited_time: Dict[str, Any] = Field(default_factory=dict)


class LastEditedByDatabaseProperty(DatabaseProperty):
    """Last edited by property configuration."""
    
    type: str = "last_edited_by"
    last_edited_by: Dict[str, Any] = Field(default_factory=dict)


class StatusDatabaseProperty(DatabaseProperty):
    """Status property configuration."""
    
    type: str = "status"
    status: Dict[str, Any] = Field(default_factory=dict)


class UniqueIdDatabaseProperty(DatabaseProperty):
    """Unique ID property configuration."""
    
    type: str = "unique_id"
    unique_id: Dict[str, Any] = Field(default_factory=dict)


class VerificationDatabaseProperty(DatabaseProperty):
    """Verification property configuration."""
    
    type: str = "verification"
    verification: Dict[str, Any] = Field(default_factory=dict)


class Database(NotionObject):
    """Notion database object."""
    
    object: str = "database"
    title: List[RichText] = Field(default_factory=list)
    description: List[RichText] = Field(default_factory=list)
    icon: Optional[Icon] = None
    cover: Optional[Cover] = None
    properties: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    parent: Parent
    url: str
    public_url: Optional[str] = None
    archived: bool = False
    in_trash: bool = False
    is_inline: bool = False
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class DatabaseCreateRequest(BaseModel):
    """Request model for creating a new database."""
    
    parent: Parent
    title: List[RichText] = Field(default_factory=list)
    description: Optional[List[RichText]] = None
    properties: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    icon: Optional[Icon] = None
    cover: Optional[Cover] = None
    is_inline: bool = False
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class DatabaseUpdateRequest(BaseModel):
    """Request model for updating a database."""
    
    title: Optional[List[RichText]] = None
    description: Optional[List[RichText]] = None
    properties: Optional[Dict[str, Dict[str, Any]]] = None
    icon: Optional[Icon] = None
    cover: Optional[Cover] = None
    archived: Optional[bool] = None
    in_trash: Optional[bool] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class DatabaseQueryFilter(BaseModel):
    """Filter for database queries."""
    
    property: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class DatabaseQuerySort(BaseModel):
    """Sort criteria for database queries."""
    
    property: Optional[str] = None
    direction: Literal["ascending", "descending"] = "ascending"
    timestamp: Optional[Literal["created_time", "last_edited_time"]] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class DatabaseQueryRequest(BaseModel):
    """Request model for querying a database."""
    
    filter: Optional[Dict[str, Any]] = None
    sorts: Optional[List[DatabaseQuerySort]] = None
    start_cursor: Optional[str] = None
    page_size: Optional[int] = Field(None, ge=1, le=100)
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
