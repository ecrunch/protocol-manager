"""
Block-related models for the Notion API client.

This module contains Pydantic models for Notion blocks and their content types.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

from .base import NotionObject, Parent, RichText, File


class BlockType(BaseModel):
    """Base class for block type definitions."""
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class ParagraphBlock(BlockType):
    """Paragraph block content."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    color: str = "default"
    children: Optional[List[Dict[str, Any]]] = None


class HeadingBlock(BlockType):
    """Heading block content (h1, h2, h3)."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    color: str = "default"
    is_toggleable: bool = False
    children: Optional[List[Dict[str, Any]]] = None


class BulletedListItemBlock(BlockType):
    """Bulleted list item block content."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    color: str = "default"
    children: Optional[List[Dict[str, Any]]] = None


class NumberedListItemBlock(BlockType):
    """Numbered list item block content."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    color: str = "default"
    children: Optional[List[Dict[str, Any]]] = None


class ToDoBlock(BlockType):
    """To-do block content."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    checked: bool = False
    color: str = "default"
    children: Optional[List[Dict[str, Any]]] = None


class ToggleBlock(BlockType):
    """Toggle block content."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    color: str = "default"
    children: Optional[List[Dict[str, Any]]] = None


class CodeBlock(BlockType):
    """Code block content."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    language: str = "plain text"
    caption: List[RichText] = Field(default_factory=list)


class QuoteBlock(BlockType):
    """Quote block content."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    color: str = "default"
    children: Optional[List[Dict[str, Any]]] = None


class CalloutBlock(BlockType):
    """Callout block content."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    icon: Optional[Dict[str, Any]] = None
    color: str = "default"
    children: Optional[List[Dict[str, Any]]] = None


class DividerBlock(BlockType):
    """Divider block content."""
    
    pass  # Divider blocks have no content


class EmbedBlock(BlockType):
    """Embed block content."""
    
    url: str
    caption: List[RichText] = Field(default_factory=list)


class ImageBlock(BlockType):
    """Image block content."""
    
    type: Literal["external", "file"]
    external: Optional[Dict[str, str]] = None
    file: Optional[Dict[str, str]] = None
    caption: List[RichText] = Field(default_factory=list)


class VideoBlock(BlockType):
    """Video block content."""
    
    type: Literal["external", "file"]
    external: Optional[Dict[str, str]] = None
    file: Optional[Dict[str, str]] = None
    caption: List[RichText] = Field(default_factory=list)


class FileBlock(BlockType):
    """File block content."""
    
    type: Literal["external", "file"]
    external: Optional[Dict[str, str]] = None
    file: Optional[Dict[str, str]] = None
    caption: List[RichText] = Field(default_factory=list)
    name: Optional[str] = None


class PdfBlock(BlockType):
    """PDF block content."""
    
    type: Literal["external", "file"]
    external: Optional[Dict[str, str]] = None
    file: Optional[Dict[str, str]] = None
    caption: List[RichText] = Field(default_factory=list)


class BookmarkBlock(BlockType):
    """Bookmark block content."""
    
    url: str
    caption: List[RichText] = Field(default_factory=list)


class EquationBlock(BlockType):
    """Equation block content."""
    
    expression: str


class TableOfContentsBlock(BlockType):
    """Table of contents block content."""
    
    color: str = "default"


class BreadcrumbBlock(BlockType):
    """Breadcrumb block content."""
    
    pass  # Breadcrumb blocks have no content


class ColumnListBlock(BlockType):
    """Column list block content."""
    
    children: Optional[List[Dict[str, Any]]] = None


class ColumnBlock(BlockType):
    """Column block content."""
    
    children: Optional[List[Dict[str, Any]]] = None


class LinkPreviewBlock(BlockType):
    """Link preview block content."""
    
    url: str


class SyncedBlock(BlockType):
    """Synced block content."""
    
    synced_from: Optional[Dict[str, str]] = None  # Contains 'block_id'
    children: Optional[List[Dict[str, Any]]] = None


class TemplateBlock(BlockType):
    """Template block content."""
    
    rich_text: List[RichText] = Field(default_factory=list)
    children: Optional[List[Dict[str, Any]]] = None


class TableBlock(BlockType):
    """Table block content."""
    
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False
    children: Optional[List[Dict[str, Any]]] = None


class TableRowBlock(BlockType):
    """Table row block content."""
    
    cells: List[List[RichText]] = Field(default_factory=list)


class Block(NotionObject):
    """Notion block object."""
    
    object: str = "block"
    parent: Parent
    type: str
    has_children: bool = False
    archived: bool = False
    in_trash: bool = False
    
    # Block type content - only one will be populated based on type
    paragraph: Optional[ParagraphBlock] = None
    heading_1: Optional[HeadingBlock] = None
    heading_2: Optional[HeadingBlock] = None
    heading_3: Optional[HeadingBlock] = None
    bulleted_list_item: Optional[BulletedListItemBlock] = None
    numbered_list_item: Optional[NumberedListItemBlock] = None
    to_do: Optional[ToDoBlock] = None
    toggle: Optional[ToggleBlock] = None
    code: Optional[CodeBlock] = None
    quote: Optional[QuoteBlock] = None
    callout: Optional[CalloutBlock] = None
    divider: Optional[DividerBlock] = None
    embed: Optional[EmbedBlock] = None
    image: Optional[ImageBlock] = None
    video: Optional[VideoBlock] = None
    file: Optional[FileBlock] = None
    pdf: Optional[PdfBlock] = None
    bookmark: Optional[BookmarkBlock] = None
    equation: Optional[EquationBlock] = None
    table_of_contents: Optional[TableOfContentsBlock] = None
    breadcrumb: Optional[BreadcrumbBlock] = None
    column_list: Optional[ColumnListBlock] = None
    column: Optional[ColumnBlock] = None
    link_preview: Optional[LinkPreviewBlock] = None
    synced_block: Optional[SyncedBlock] = None
    template: Optional[TemplateBlock] = None
    table: Optional[TableBlock] = None
    table_row: Optional[TableRowBlock] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class BlockCreateRequest(BaseModel):
    """Request model for creating blocks."""
    
    type: str
    # Block content fields based on type
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class BlockUpdateRequest(BaseModel):
    """Request model for updating blocks."""
    
    archived: Optional[bool] = None
    in_trash: Optional[bool] = None
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
