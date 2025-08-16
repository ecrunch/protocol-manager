"""
Helper functions for working with Notion API data structures.

This module provides utility functions to create and manipulate common
Notion API objects like rich text, blocks, and properties.
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse


def create_rich_text(
    text: str,
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    underline: bool = False,
    code: bool = False,
    color: str = "default",
    url: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a rich text object.
    
    Args:
        text: The text content
        bold: Whether text should be bold
        italic: Whether text should be italic
        strikethrough: Whether text should have strikethrough
        underline: Whether text should be underlined
        code: Whether text should be formatted as code
        color: Text color
        url: Link URL if text should be a link
        
    Returns:
        Rich text object dictionary
    """
    rich_text = {
        "type": "text",
        "text": {
            "content": text,
        },
        "annotations": {
            "bold": bold,
            "italic": italic,
            "strikethrough": strikethrough,
            "underline": underline,
            "code": code,
            "color": color,
        },
        "plain_text": text,
        "href": url,
    }
    
    if url:
        rich_text["text"]["link"] = {"url": url}
    
    return rich_text


def create_page_parent(page_id: str) -> Dict[str, Any]:
    """Create a page parent object.
    
    Args:
        page_id: Notion page ID
        
    Returns:
        Parent object dictionary
    """
    return {
        "type": "page_id",
        "page_id": page_id,
    }


def create_database_parent(database_id: str) -> Dict[str, Any]:
    """Create a database parent object.
    
    Args:
        database_id: Notion database ID
        
    Returns:
        Parent object dictionary
    """
    return {
        "type": "database_id",
        "database_id": database_id,
    }


def create_workspace_parent() -> Dict[str, Any]:
    """Create a workspace parent object.
    
    Returns:
        Workspace parent object dictionary
    """
    return {
        "type": "workspace",
        "workspace": True,
    }


def create_text_block(
    text: str,
    block_type: str = "paragraph",
    color: str = "default",
    **text_formatting: Any,
) -> Dict[str, Any]:
    """Create a text-based block.
    
    Args:
        text: Block text content
        block_type: Type of block (paragraph, heading_1, etc.)
        color: Block color
        **text_formatting: Rich text formatting options
        
    Returns:
        Block object dictionary
    """
    rich_text = create_rich_text(text, **text_formatting)
    
    return {
        "type": block_type,
        block_type: {
            "rich_text": [rich_text],
            "color": color,
        },
    }


def create_paragraph_block(
    text: str,
    color: str = "default",
    **text_formatting: Any,
) -> Dict[str, Any]:
    """Create a paragraph block.
    
    Args:
        text: Paragraph text
        color: Block color
        **text_formatting: Rich text formatting options
        
    Returns:
        Paragraph block dictionary
    """
    return create_text_block(text, "paragraph", color, **text_formatting)


def create_heading_block(
    text: str,
    level: int = 1,
    color: str = "default",
    is_toggleable: bool = False,
    **text_formatting: Any,
) -> Dict[str, Any]:
    """Create a heading block.
    
    Args:
        text: Heading text
        level: Heading level (1, 2, or 3)
        color: Block color
        is_toggleable: Whether heading is toggleable
        **text_formatting: Rich text formatting options
        
    Returns:
        Heading block dictionary
        
    Raises:
        ValueError: If heading level is not 1, 2, or 3
    """
    if level not in [1, 2, 3]:
        raise ValueError("Heading level must be 1, 2, or 3")
    
    block_type = f"heading_{level}"
    rich_text = create_rich_text(text, **text_formatting)
    
    block_content = {
        "rich_text": [rich_text],
        "color": color,
    }
    
    if is_toggleable:
        block_content["is_toggleable"] = True
    
    return {
        "type": block_type,
        block_type: block_content,
    }


def create_code_block(
    code: str,
    language: str = "plain text",
    caption: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a code block.
    
    Args:
        code: Code content
        language: Programming language
        caption: Optional caption
        
    Returns:
        Code block dictionary
    """
    rich_text = create_rich_text(code)
    caption_rich_text = [create_rich_text(caption)] if caption else []
    
    return {
        "type": "code",
        "code": {
            "rich_text": [rich_text],
            "language": language,
            "caption": caption_rich_text,
        },
    }


def create_todo_block(
    text: str,
    checked: bool = False,
    color: str = "default",
    **text_formatting: Any,
) -> Dict[str, Any]:
    """Create a to-do block.
    
    Args:
        text: To-do text
        checked: Whether to-do is checked
        color: Block color
        **text_formatting: Rich text formatting options
        
    Returns:
        To-do block dictionary
    """
    rich_text = create_rich_text(text, **text_formatting)
    
    return {
        "type": "to_do",
        "to_do": {
            "rich_text": [rich_text],
            "checked": checked,
            "color": color,
        },
    }


def create_bulleted_list_item(
    text: str,
    color: str = "default",
    **text_formatting: Any,
) -> Dict[str, Any]:
    """Create a bulleted list item block.
    
    Args:
        text: List item text
        color: Block color
        **text_formatting: Rich text formatting options
        
    Returns:
        Bulleted list item block dictionary
    """
    rich_text = create_rich_text(text, **text_formatting)
    
    return {
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [rich_text],
            "color": color,
        },
    }


def create_numbered_list_item(
    text: str,
    color: str = "default",
    **text_formatting: Any,
) -> Dict[str, Any]:
    """Create a numbered list item block.
    
    Args:
        text: List item text
        color: Block color
        **text_formatting: Rich text formatting options
        
    Returns:
        Numbered list item block dictionary
    """
    rich_text = create_rich_text(text, **text_formatting)
    
    return {
        "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": [rich_text],
            "color": color,
        },
    }


def create_quote_block(
    text: str,
    color: str = "default",
    **text_formatting: Any,
) -> Dict[str, Any]:
    """Create a quote block.
    
    Args:
        text: Quote text
        color: Block color
        **text_formatting: Rich text formatting options
        
    Returns:
        Quote block dictionary
    """
    rich_text = create_rich_text(text, **text_formatting)
    
    return {
        "type": "quote",
        "quote": {
            "rich_text": [rich_text],
            "color": color,
        },
    }


def create_callout_block(
    text: str,
    icon: Optional[str] = None,
    color: str = "default",
    **text_formatting: Any,
) -> Dict[str, Any]:
    """Create a callout block.
    
    Args:
        text: Callout text
        icon: Emoji icon for callout
        color: Block color
        **text_formatting: Rich text formatting options
        
    Returns:
        Callout block dictionary
    """
    rich_text = create_rich_text(text, **text_formatting)
    
    callout_data = {
        "rich_text": [rich_text],
        "color": color,
    }
    
    if icon:
        callout_data["icon"] = {
            "type": "emoji",
            "emoji": icon,
        }
    
    return {
        "type": "callout",
        "callout": callout_data,
    }


def create_divider_block() -> Dict[str, Any]:
    """Create a divider block.
    
    Returns:
        Divider block dictionary
    """
    return {
        "type": "divider",
        "divider": {},
    }


def create_image_block(
    image_url: str,
    caption: Optional[str] = None,
    is_external: bool = True,
) -> Dict[str, Any]:
    """Create an image block.
    
    Args:
        image_url: URL of the image
        caption: Optional image caption
        is_external: Whether image is external (vs uploaded)
        
    Returns:
        Image block dictionary
    """
    caption_rich_text = [create_rich_text(caption)] if caption else []
    
    image_data = {
        "caption": caption_rich_text,
    }
    
    if is_external:
        image_data["type"] = "external"
        image_data["external"] = {"url": image_url}
    else:
        image_data["type"] = "file"
        image_data["file"] = {"url": image_url}
    
    return {
        "type": "image",
        "image": image_data,
    }


def create_bookmark_block(
    url: str,
    caption: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a bookmark block.
    
    Args:
        url: URL to bookmark
        caption: Optional caption
        
    Returns:
        Bookmark block dictionary
    """
    caption_rich_text = [create_rich_text(caption)] if caption else []
    
    return {
        "type": "bookmark",
        "bookmark": {
            "url": url,
            "caption": caption_rich_text,
        },
    }


def extract_plain_text(rich_text_list: List[Dict[str, Any]]) -> str:
    """Extract plain text from a list of rich text objects.
    
    Args:
        rich_text_list: List of rich text objects
        
    Returns:
        Combined plain text string
    """
    if not rich_text_list:
        return ""
    
    return "".join([
        item.get("plain_text", "") for item in rich_text_list
    ])


def format_notion_date(
    start_date: Union[str, datetime],
    end_date: Optional[Union[str, datetime]] = None,
    include_time: bool = False,
    timezone_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Format a date for Notion API.
    
    Args:
        start_date: Start date
        end_date: End date (for date ranges)
        include_time: Whether to include time information
        timezone_name: Timezone name (e.g., "America/New_York")
        
    Returns:
        Formatted date object
    """
    def format_single_date(date_obj: Union[str, datetime]) -> str:
        if isinstance(date_obj, str):
            return date_obj
        
        if include_time:
            return date_obj.isoformat()
        else:
            return date_obj.date().isoformat()
    
    date_data = {
        "start": format_single_date(start_date),
    }
    
    if end_date:
        date_data["end"] = format_single_date(end_date)
    
    if timezone_name:
        date_data["time_zone"] = timezone_name
    
    return date_data


def parse_notion_date(date_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a Notion date object.
    
    Args:
        date_data: Notion date object
        
    Returns:
        Parsed date information with datetime objects
    """
    result = {}
    
    if "start" in date_data:
        start_str = date_data["start"]
        if "T" in start_str:  # Has time
            result["start"] = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        else:  # Date only
            result["start"] = datetime.fromisoformat(start_str + "T00:00:00")
    
    if "end" in date_data and date_data["end"]:
        end_str = date_data["end"]
        if "T" in end_str:  # Has time
            result["end"] = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        else:  # Date only
            result["end"] = datetime.fromisoformat(end_str + "T00:00:00")
    
    if "time_zone" in date_data:
        result["time_zone"] = date_data["time_zone"]
    
    return result


def create_select_option(
    name: str,
    color: str = "default",
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a select option for select/multi-select properties.
    
    Args:
        name: Option name
        color: Option color
        description: Optional description
        
    Returns:
        Select option dictionary
    """
    option = {
        "name": name,
        "color": color,
    }
    
    if description:
        option["description"] = description
    
    return option


def create_icon(
    icon_type: str,
    value: str,
) -> Dict[str, Any]:
    """Create an icon object.
    
    Args:
        icon_type: Type of icon ("emoji", "external", or "file")
        value: Icon value (emoji or URL)
        
    Returns:
        Icon object dictionary
        
    Raises:
        ValueError: If icon_type is not valid
    """
    if icon_type not in ["emoji", "external", "file"]:
        raise ValueError("icon_type must be 'emoji', 'external', or 'file'")
    
    icon = {"type": icon_type}
    
    if icon_type == "emoji":
        icon["emoji"] = value
    elif icon_type == "external":
        icon["external"] = {"url": value}
    else:  # file
        icon["file"] = {"url": value}
    
    return icon


def create_cover(
    cover_type: str,
    url: str,
) -> Dict[str, Any]:
    """Create a cover object.
    
    Args:
        cover_type: Type of cover ("external" or "file")
        url: Cover image URL
        
    Returns:
        Cover object dictionary
        
    Raises:
        ValueError: If cover_type is not valid
    """
    if cover_type not in ["external", "file"]:
        raise ValueError("cover_type must be 'external' or 'file'")
    
    cover = {"type": cover_type}
    
    if cover_type == "external":
        cover["external"] = {"url": url}
    else:  # file
        cover["file"] = {"url": url}
    
    return cover


def normalize_notion_id(notion_id: str) -> str:
    """Normalize a Notion ID by removing dashes.
    
    Args:
        notion_id: Notion ID with or without dashes
        
    Returns:
        Normalized ID without dashes
    """
    return notion_id.replace("-", "")


def format_notion_id(notion_id: str) -> str:
    """Format a Notion ID with dashes in UUID format.
    
    Args:
        notion_id: Notion ID without dashes
        
    Returns:
        Formatted ID with dashes
        
    Raises:
        ValueError: If ID is not 32 characters
    """
    clean_id = normalize_notion_id(notion_id)
    
    if len(clean_id) != 32:
        raise ValueError(f"Invalid Notion ID length: {len(clean_id)}")
    
    return f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"
