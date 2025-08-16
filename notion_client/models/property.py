"""
Property-related models for the Notion API client.

This module contains Pydantic models for different property types
used in pages and databases.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

from .base import RichText, SelectOption, FormulaResult, RollupResult


class PropertyType(BaseModel):
    """Base class for property types."""
    
    id: str
    type: str
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class Property(BaseModel):
    """Base property model."""
    
    id: str
    type: str
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


# Page Property Values
class TitlePropertyValue(Property):
    """Title property value."""
    
    type: str = "title"
    title: List[RichText] = Field(default_factory=list)


class RichTextPropertyValue(Property):
    """Rich text property value."""
    
    type: str = "rich_text"
    rich_text: List[RichText] = Field(default_factory=list)


class NumberPropertyValue(Property):
    """Number property value."""
    
    type: str = "number"
    number: Optional[float] = None


class SelectPropertyValue(Property):
    """Select property value."""
    
    type: str = "select"
    select: Optional[SelectOption] = None


class MultiSelectPropertyValue(Property):
    """Multi-select property value."""
    
    type: str = "multi_select"
    multi_select: List[SelectOption] = Field(default_factory=list)


class DatePropertyValue(Property):
    """Date property value."""
    
    type: str = "date"
    date: Optional[Dict[str, Any]] = None


class CheckboxPropertyValue(Property):
    """Checkbox property value."""
    
    type: str = "checkbox"
    checkbox: bool = False


class UrlPropertyValue(Property):
    """URL property value."""
    
    type: str = "url"
    url: Optional[str] = None


class EmailPropertyValue(Property):
    """Email property value."""
    
    type: str = "email"
    email: Optional[str] = None


class PhoneNumberPropertyValue(Property):
    """Phone number property value."""
    
    type: str = "phone_number"
    phone_number: Optional[str] = None


class FilesPropertyValue(Property):
    """Files property value."""
    
    type: str = "files"
    files: List[Dict[str, Any]] = Field(default_factory=list)


class PeoplePropertyValue(Property):
    """People property value."""
    
    type: str = "people"
    people: List[Dict[str, Any]] = Field(default_factory=list)


class RelationPropertyValue(Property):
    """Relation property value."""
    
    type: str = "relation"
    relation: List[Dict[str, str]] = Field(default_factory=list)  # List of page references
    has_more: bool = False


class FormulaPropertyValue(Property):
    """Formula property value."""
    
    type: str = "formula"
    formula: Optional[FormulaResult] = None


class RollupPropertyValue(Property):
    """Rollup property value."""
    
    type: str = "rollup"
    rollup: Optional[RollupResult] = None


class CreatedTimePropertyValue(Property):
    """Created time property value."""
    
    type: str = "created_time"
    created_time: datetime


class CreatedByPropertyValue(Property):
    """Created by property value."""
    
    type: str = "created_by"
    created_by: Dict[str, Any]


class LastEditedTimePropertyValue(Property):
    """Last edited time property value."""
    
    type: str = "last_edited_time"
    last_edited_time: datetime


class LastEditedByPropertyValue(Property):
    """Last edited by property value."""
    
    type: str = "last_edited_by"
    last_edited_by: Dict[str, Any]


class StatusPropertyValue(Property):
    """Status property value."""
    
    type: str = "status"
    status: Optional[SelectOption] = None


class UniqueIdPropertyValue(Property):
    """Unique ID property value."""
    
    type: str = "unique_id"
    unique_id: Optional[Dict[str, Any]] = None


class VerificationPropertyValue(Property):
    """Verification property value."""
    
    type: str = "verification"
    verification: Optional[Dict[str, Any]] = None


# Database Property Configurations
class TitlePropertyConfig(Property):
    """Title property configuration."""
    
    type: str = "title"
    title: Dict[str, Any] = Field(default_factory=dict)


class RichTextPropertyConfig(Property):
    """Rich text property configuration."""
    
    type: str = "rich_text"
    rich_text: Dict[str, Any] = Field(default_factory=dict)


class NumberPropertyConfig(Property):
    """Number property configuration."""
    
    type: str = "number"
    number: Dict[str, str] = Field(default_factory=dict)  # Contains 'format'


class SelectPropertyConfig(Property):
    """Select property configuration."""
    
    type: str = "select"
    select: Dict[str, List[SelectOption]] = Field(default_factory=dict)


class MultiSelectPropertyConfig(Property):
    """Multi-select property configuration."""
    
    type: str = "multi_select"
    multi_select: Dict[str, List[SelectOption]] = Field(default_factory=dict)


class DatePropertyConfig(Property):
    """Date property configuration."""
    
    type: str = "date"
    date: Dict[str, Any] = Field(default_factory=dict)


class CheckboxPropertyConfig(Property):
    """Checkbox property configuration."""
    
    type: str = "checkbox"
    checkbox: Dict[str, Any] = Field(default_factory=dict)


class UrlPropertyConfig(Property):
    """URL property configuration."""
    
    type: str = "url"
    url: Dict[str, Any] = Field(default_factory=dict)


class EmailPropertyConfig(Property):
    """Email property configuration."""
    
    type: str = "email"
    email: Dict[str, Any] = Field(default_factory=dict)


class PhoneNumberPropertyConfig(Property):
    """Phone number property configuration."""
    
    type: str = "phone_number"
    phone_number: Dict[str, Any] = Field(default_factory=dict)


class FilesPropertyConfig(Property):
    """Files property configuration."""
    
    type: str = "files"
    files: Dict[str, Any] = Field(default_factory=dict)


class PeoplePropertyConfig(Property):
    """People property configuration."""
    
    type: str = "people"
    people: Dict[str, Any] = Field(default_factory=dict)


class RelationPropertyConfig(Property):
    """Relation property configuration."""
    
    type: str = "relation"
    relation: Dict[str, Any] = Field(default_factory=dict)


class FormulaPropertyConfig(Property):
    """Formula property configuration."""
    
    type: str = "formula"
    formula: Dict[str, str] = Field(default_factory=dict)  # Contains 'expression'


class RollupPropertyConfig(Property):
    """Rollup property configuration."""
    
    type: str = "rollup"
    rollup: Dict[str, Any] = Field(default_factory=dict)


class StatusPropertyConfig(Property):
    """Status property configuration."""
    
    type: str = "status"
    status: Dict[str, Any] = Field(default_factory=dict)


class UniqueIdPropertyConfig(Property):
    """Unique ID property configuration."""
    
    type: str = "unique_id"
    unique_id: Dict[str, Any] = Field(default_factory=dict)
