"""
Utility functions and helpers for the Notion Python client.

This package contains utility functions, validators, and helper classes
to support the main client functionality.
"""

from .helpers import (
    create_rich_text,
    create_page_parent,
    create_database_parent,
    create_text_block,
    create_heading_block,
    create_paragraph_block,
    create_todo_block,
    create_bulleted_list_item,
    create_numbered_list_item,
    create_quote_block,
    create_callout_block,
    create_divider_block,
    create_code_block,
    create_image_block,
    create_bookmark_block,
    create_select_option,
    create_icon,
    create_cover,
    extract_plain_text,
    format_notion_date,
    parse_notion_date,
)
from .validators import (
    validate_notion_id,
    validate_email,
    validate_url,
    validate_color,
    validate_property_type,
)

__all__ = [
    "create_rich_text",
    "create_page_parent",
    "create_database_parent", 
    "create_text_block",
    "create_heading_block",
    "create_paragraph_block",
    "create_todo_block",
    "create_bulleted_list_item",
    "create_numbered_list_item",
    "create_quote_block",
    "create_callout_block",
    "create_divider_block",
    "create_code_block",
    "create_image_block",
    "create_bookmark_block",
    "create_select_option",
    "create_icon",
    "create_cover",
    "extract_plain_text",
    "format_notion_date",
    "parse_notion_date",
    "validate_notion_id",
    "validate_email",
    "validate_url",
    "validate_color",
    "validate_property_type",
]
