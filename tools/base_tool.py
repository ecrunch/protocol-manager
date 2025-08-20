"""
Base tool class for Notion operations.

This module provides the foundational BaseNotionTool class that all
Notion-specific tools inherit from.
"""

from abc import ABC
from typing import Type, Optional, Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from notion_client.client import NotionClient
from notion_client.exceptions import NotionAPIError


class BaseNotionTool(BaseTool, ABC):
    """Base class for all Notion-related LangChain tools."""
    
    notion_client: NotionClient = Field(exclude=True)
    
    def __init__(self, notion_client: NotionClient, **kwargs):
        """
        Initialize the base Notion tool.
        
        Args:
            notion_client: Initialized Notion client instance
            **kwargs: Additional arguments for BaseTool
        """
        super().__init__(notion_client=notion_client, **kwargs)
        
    def _handle_notion_error(self, error: Exception, operation: str) -> str:
        """
        Handle Notion API errors with user-friendly messages.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation being performed
            
        Returns:
            User-friendly error message
        """
        if isinstance(error, NotionAPIError):
            return f"Notion API error during {operation}: {error.message}"
        else:
            return f"Error during {operation}: {str(error)}"
            
    def _format_notion_date(self, date_str: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Format a date string for Notion API.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            Notion-formatted date object or None
        """
        if not date_str:
            return None
            
        try:
            # Basic validation - could be enhanced with proper date parsing
            if len(date_str) == 10 and date_str.count('-') == 2:
                return {"start": date_str}
            else:
                return None
        except Exception:
            return None
            
    def _format_notion_select(self, value: str) -> Dict[str, str]:
        """
        Format a select value for Notion API.
        
        Args:
            value: Select option value
            
        Returns:
            Notion-formatted select object
        """
        return {"name": value}
        
    def _format_notion_title(self, text: str) -> List[Dict[str, Any]]:
        """
        Format text for Notion title property.
        
        Args:
            text: Title text
            
        Returns:
            Notion-formatted title array
        """
        return [{"text": {"content": text}}]
        
    def _format_notion_rich_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Format text for Notion rich text property.
        
        Args:
            text: Rich text content
            
        Returns:
            Notion-formatted rich text array
        """
        return [{"text": {"content": text}}]
        
    def _extract_page_title(self, page) -> str:
        """
        Extract the title from a Notion page object.
        
        Args:
            page: Notion page object (can be a model object or dict)
            
        Returns:
            Page title or fallback text
        """
        try:
            # Handle both page model objects and dictionaries
            if hasattr(page, 'properties'):
                properties = page.properties
            elif isinstance(page, dict):
                properties = page.get("properties", {})
            else:
                return "Untitled"
                
            for prop_name, prop_data in properties.items():
                if prop_data.get("type") == "title":
                    title_array = prop_data.get("title", [])
                    if title_array:
                        return title_array[0].get("text", {}).get("content", "Untitled")
            return "Untitled"
        except Exception:
            return "Untitled"
            
    def _extract_property_value(self, page, property_name: str) -> Any:
        """
        Extract a property value from a Notion page.
        
        Args:
            page: Notion page object (can be a model object or dict)
            property_name: Name of the property to extract
            
        Returns:
            Property value or None
        """
        try:
            # Handle both page model objects and dictionaries
            if hasattr(page, 'properties'):
                properties = page.properties
            elif isinstance(page, dict):
                properties = page.get("properties", {})
            else:
                return None
            prop_data = properties.get(property_name, {})
            prop_type = prop_data.get("type")
            
            if prop_type == "title":
                title_array = prop_data.get("title", [])
                return title_array[0].get("text", {}).get("content") if title_array else None
                
            elif prop_type == "rich_text":
                rich_text_array = prop_data.get("rich_text", [])
                return rich_text_array[0].get("text", {}).get("content") if rich_text_array else None
                
            elif prop_type == "select":
                select_obj = prop_data.get("select")
                return select_obj.get("name") if select_obj else None
                
            elif prop_type == "multi_select":
                multi_select_array = prop_data.get("multi_select", [])
                return [item.get("name") for item in multi_select_array]
                
            elif prop_type == "date":
                date_obj = prop_data.get("date")
                return date_obj.get("start") if date_obj else None
                
            elif prop_type == "checkbox":
                return prop_data.get("checkbox", False)
                
            elif prop_type == "number":
                return prop_data.get("number")
                
            elif prop_type == "url":
                return prop_data.get("url")
                
            elif prop_type == "email":
                return prop_data.get("email")
                
            elif prop_type == "phone_number":
                return prop_data.get("phone_number")
                
            else:
                return None
                
        except Exception:
            return None
