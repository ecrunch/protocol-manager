"""
Validation functions for Notion API data.

This module provides validation functions to ensure data conforms
to Notion API requirements and constraints.
"""

import re
from typing import Any, List, Optional
from urllib.parse import urlparse


def validate_notion_id(notion_id: str, allow_dashes: bool = True) -> bool:
    """Validate a Notion ID format.
    
    Args:
        notion_id: ID to validate
        allow_dashes: Whether to allow dashes in the ID
        
    Returns:
        True if ID is valid, False otherwise
    """
    if not notion_id or not isinstance(notion_id, str):
        return False
    
    # Remove dashes for validation
    clean_id = notion_id.replace("-", "")
    
    # Should be 32 hexadecimal characters
    if len(clean_id) != 32:
        return False
    
    # Check if all characters are hexadecimal
    return bool(re.match(r"^[0-9a-fA-F]{32}$", clean_id))


def validate_email(email: str) -> bool:
    """Validate an email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email validation regex
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


def validate_url(url: str) -> bool:
    """Validate a URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_color(color: str) -> bool:
    """Validate a Notion color value.
    
    Args:
        color: Color name to validate
        
    Returns:
        True if color is valid, False otherwise
    """
    valid_colors = {
        "default", "gray", "brown", "orange", "yellow", 
        "green", "blue", "purple", "pink", "red",
        "gray_bg", "brown_bg", "orange_bg", "yellow_bg",
        "green_bg", "blue_bg", "purple_bg", "pink_bg", "red_bg"
    }
    
    return color in valid_colors


def validate_property_type(property_type: str) -> bool:
    """Validate a Notion property type.
    
    Args:
        property_type: Property type to validate
        
    Returns:
        True if property type is valid, False otherwise
    """
    valid_types = {
        "title", "rich_text", "number", "select", "multi_select",
        "date", "people", "files", "checkbox", "url", "email",
        "phone_number", "formula", "relation", "rollup",
        "created_time", "created_by", "last_edited_time",
        "last_edited_by", "status", "unique_id", "verification"
    }
    
    return property_type in valid_types


def validate_block_type(block_type: str) -> bool:
    """Validate a Notion block type.
    
    Args:
        block_type: Block type to validate
        
    Returns:
        True if block type is valid, False otherwise
    """
    valid_types = {
        "paragraph", "heading_1", "heading_2", "heading_3",
        "bulleted_list_item", "numbered_list_item", "to_do",
        "toggle", "code", "quote", "callout", "divider",
        "embed", "image", "video", "file", "pdf", "bookmark",
        "equation", "table_of_contents", "breadcrumb",
        "column_list", "column", "link_preview", "synced_block",
        "template", "table", "table_row"
    }
    
    return block_type in valid_types


def validate_rich_text(rich_text_data: Any) -> bool:
    """Validate rich text data structure.
    
    Args:
        rich_text_data: Rich text data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(rich_text_data, dict):
        return False
    
    # Check required fields
    required_fields = ["type", "plain_text"]
    if not all(field in rich_text_data for field in required_fields):
        return False
    
    # Validate type
    if rich_text_data["type"] not in ["text", "mention", "equation"]:
        return False
    
    # Validate annotations if present
    if "annotations" in rich_text_data:
        annotations = rich_text_data["annotations"]
        if not isinstance(annotations, dict):
            return False
        
        # Check annotation fields
        valid_annotation_fields = {
            "bold", "italic", "strikethrough", "underline", "code", "color"
        }
        
        for key in annotations:
            if key not in valid_annotation_fields:
                return False
            
            if key == "color":
                if not validate_color(annotations[key]):
                    return False
            elif not isinstance(annotations[key], bool):
                return False
    
    return True


def validate_parent(parent_data: Any) -> bool:
    """Validate parent object structure.
    
    Args:
        parent_data: Parent data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(parent_data, dict):
        return False
    
    # Check type field
    if "type" not in parent_data:
        return False
    
    parent_type = parent_data["type"]
    valid_types = ["database_id", "page_id", "workspace", "block_id"]
    
    if parent_type not in valid_types:
        return False
    
    # Validate type-specific fields
    if parent_type == "database_id":
        return "database_id" in parent_data and validate_notion_id(parent_data["database_id"])
    elif parent_type == "page_id":
        return "page_id" in parent_data and validate_notion_id(parent_data["page_id"])
    elif parent_type == "block_id":
        return "block_id" in parent_data and validate_notion_id(parent_data["block_id"])
    elif parent_type == "workspace":
        return "workspace" in parent_data and parent_data["workspace"] is True
    
    return False


def validate_icon(icon_data: Any) -> bool:
    """Validate icon object structure.
    
    Args:
        icon_data: Icon data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(icon_data, dict):
        return False
    
    if "type" not in icon_data:
        return False
    
    icon_type = icon_data["type"]
    valid_types = ["emoji", "external", "file"]
    
    if icon_type not in valid_types:
        return False
    
    # Validate type-specific fields
    if icon_type == "emoji":
        return "emoji" in icon_data and isinstance(icon_data["emoji"], str)
    elif icon_type == "external":
        return ("external" in icon_data 
                and isinstance(icon_data["external"], dict)
                and "url" in icon_data["external"]
                and validate_url(icon_data["external"]["url"]))
    elif icon_type == "file":
        return ("file" in icon_data
                and isinstance(icon_data["file"], dict)
                and "url" in icon_data["file"]
                and validate_url(icon_data["file"]["url"]))
    
    return False


def validate_cover(cover_data: Any) -> bool:
    """Validate cover object structure.
    
    Args:
        cover_data: Cover data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(cover_data, dict):
        return False
    
    if "type" not in cover_data:
        return False
    
    cover_type = cover_data["type"]
    valid_types = ["external", "file"]
    
    if cover_type not in valid_types:
        return False
    
    # Validate type-specific fields
    if cover_type == "external":
        return ("external" in cover_data
                and isinstance(cover_data["external"], dict)
                and "url" in cover_data["external"]
                and validate_url(cover_data["external"]["url"]))
    elif cover_type == "file":
        return ("file" in cover_data
                and isinstance(cover_data["file"], dict)
                and "url" in cover_data["file"]
                and validate_url(cover_data["file"]["url"]))
    
    return False


def validate_select_option(option_data: Any) -> bool:
    """Validate select option structure.
    
    Args:
        option_data: Select option data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(option_data, dict):
        return False
    
    # Name is required
    if "name" not in option_data or not isinstance(option_data["name"], str):
        return False
    
    # Color is optional but must be valid if present
    if "color" in option_data and not validate_color(option_data["color"]):
        return False
    
    # Description is optional but must be string if present
    if "description" in option_data and not isinstance(option_data["description"], str):
        return False
    
    return True


def validate_page_size(page_size: int) -> bool:
    """Validate page size for pagination.
    
    Args:
        page_size: Page size to validate
        
    Returns:
        True if page size is valid, False otherwise
    """
    return isinstance(page_size, int) and 1 <= page_size <= 100


def validate_sort_object(sort_data: Any) -> bool:
    """Validate sort object structure.
    
    Args:
        sort_data: Sort data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(sort_data, dict):
        return False
    
    # Must have either property or timestamp
    if "property" not in sort_data and "timestamp" not in sort_data:
        return False
    
    # Direction is optional but must be valid if present
    if "direction" in sort_data:
        if sort_data["direction"] not in ["ascending", "descending"]:
            return False
    
    # Timestamp must be valid if present
    if "timestamp" in sort_data:
        if sort_data["timestamp"] not in ["created_time", "last_edited_time"]:
            return False
    
    return True


def validate_database_query(query_data: Any) -> bool:
    """Validate database query structure.
    
    Args:
        query_data: Query data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(query_data, dict):
        return False
    
    # Validate page_size if present
    if "page_size" in query_data:
        if not validate_page_size(query_data["page_size"]):
            return False
    
    # Validate sorts if present
    if "sorts" in query_data:
        sorts = query_data["sorts"]
        if not isinstance(sorts, list):
            return False
        
        for sort_obj in sorts:
            if not validate_sort_object(sort_obj):
                return False
    
    # start_cursor should be string if present
    if "start_cursor" in query_data:
        if not isinstance(query_data["start_cursor"], str):
            return False
    
    return True
