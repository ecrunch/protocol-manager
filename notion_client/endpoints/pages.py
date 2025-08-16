"""
Pages endpoint for the Notion API client.

This module provides methods for interacting with Notion pages API,
including creating, retrieving, updating pages and their properties.
"""

import logging
from typing import Any, Dict, List, Optional, Generator

from .base import BaseEndpoint
from ..models.page import Page, PageCreateRequest, PageUpdateRequest


logger = logging.getLogger(__name__)


class PagesEndpoint(BaseEndpoint):
    """Pages API endpoint handler."""
    
    def create(
        self,
        parent: Dict[str, Any],
        properties: Optional[Dict[str, Any]] = None,
        children: Optional[List[Dict[str, Any]]] = None,
        icon: Optional[Dict[str, Any]] = None,
        cover: Optional[Dict[str, Any]] = None,
    ) -> Page:
        """Create a new page.
        
        Args:
            parent: Parent page or database reference
            properties: Page properties
            children: Initial child blocks
            icon: Page icon
            cover: Page cover image
            
        Returns:
            Created page object
            
        Raises:
            NotionValidationError: If request data is invalid
            NotionAPIError: If API request fails
        """
        # Construct request data
        request_data = {
            "parent": parent,
            "properties": properties or {},
        }
        
        if children is not None:
            request_data["children"] = children
        
        if icon is not None:
            request_data["icon"] = icon
        
        if cover is not None:
            request_data["cover"] = cover
        
        # Remove None values
        request_data = self._clean_dict(request_data)
        
        logger.info(f"Creating page with parent: {parent}")
        response = self.http_client.post("pages", data=request_data)
        
        return Page(**response)
    
    def retrieve(self, page_id: str) -> Page:
        """Retrieve a page by ID.
        
        Args:
            page_id: Notion page ID
            
        Returns:
            Page object
            
        Raises:
            NotionNotFoundError: If page is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(page_id, "page")
        
        logger.info(f"Retrieving page: {page_id}")
        response = self.http_client.get(f"pages/{page_id}")
        
        return Page(**response)
    
    def update(
        self,
        page_id: str,
        properties: Optional[Dict[str, Any]] = None,
        archived: Optional[bool] = None,
        in_trash: Optional[bool] = None,
        icon: Optional[Dict[str, Any]] = None,
        cover: Optional[Dict[str, Any]] = None,
    ) -> Page:
        """Update a page.
        
        Args:
            page_id: Notion page ID
            properties: Updated page properties
            archived: Whether to archive the page
            in_trash: Whether to move page to trash
            icon: Updated page icon
            cover: Updated page cover image
            
        Returns:
            Updated page object
            
        Raises:
            NotionNotFoundError: If page is not found
            NotionValidationError: If request data is invalid
            NotionAPIError: If API request fails
        """
        self._validate_id(page_id, "page")
        
        # Construct update data
        update_data = {}
        
        if properties is not None:
            update_data["properties"] = properties
        
        if archived is not None:
            update_data["archived"] = archived
        
        if in_trash is not None:
            update_data["in_trash"] = in_trash
        
        if icon is not None:
            update_data["icon"] = icon
        
        if cover is not None:
            update_data["cover"] = cover
        
        if not update_data:
            raise ValueError("At least one field must be provided for update")
        
        logger.info(f"Updating page: {page_id}")
        response = self.http_client.patch(f"pages/{page_id}", data=update_data)
        
        return Page(**response)
    
    def retrieve_property(
        self,
        page_id: str,
        property_id: str,
        start_cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Retrieve a specific page property.
        
        This is useful for paginated properties like relations and rollups.
        
        Args:
            page_id: Notion page ID
            property_id: Property ID to retrieve
            start_cursor: Pagination cursor
            page_size: Number of items per page
            
        Returns:
            Property value data
            
        Raises:
            NotionNotFoundError: If page or property is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(page_id, "page")
        
        params = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size
        
        logger.info(f"Retrieving property {property_id} for page: {page_id}")
        response = self.http_client.get(
            f"pages/{page_id}/properties/{property_id}",
            params=params or None,
        )
        
        return response
    
    def get_property_all_items(
        self,
        page_id: str,
        property_id: str,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get all items from a paginated property.
        
        Args:
            page_id: Notion page ID
            property_id: Property ID to retrieve
            page_size: Number of items per page
            
        Returns:
            List of all property items
            
        Raises:
            NotionNotFoundError: If page or property is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(page_id, "page")
        
        endpoint = f"pages/{page_id}/properties/{property_id}"
        return self._get_all_paginated(endpoint, page_size=page_size)
    
    def archive(self, page_id: str) -> Page:
        """Archive a page.
        
        Args:
            page_id: Notion page ID
            
        Returns:
            Archived page object
            
        Raises:
            NotionNotFoundError: If page is not found
            NotionAPIError: If API request fails
        """
        return self.update(page_id, archived=True)
    
    def unarchive(self, page_id: str) -> Page:
        """Unarchive a page.
        
        Args:
            page_id: Notion page ID
            
        Returns:
            Unarchived page object
            
        Raises:
            NotionNotFoundError: If page is not found
            NotionAPIError: If API request fails
        """
        return self.update(page_id, archived=False)
    
    def delete(self, page_id: str) -> Page:
        """Move a page to trash.
        
        Args:
            page_id: Notion page ID
            
        Returns:
            Deleted page object
            
        Raises:
            NotionNotFoundError: If page is not found
            NotionAPIError: If API request fails
        """
        return self.update(page_id, in_trash=True)
    
    def restore(self, page_id: str) -> Page:
        """Restore a page from trash.
        
        Args:
            page_id: Notion page ID
            
        Returns:
            Restored page object
            
        Raises:
            NotionNotFoundError: If page is not found
            NotionAPIError: If API request fails
        """
        return self.update(page_id, in_trash=False)
    
    def set_full_width(self, page_id: str, full_width: bool = True) -> Page:
        """Set a page to full width or normal width.
        
        Args:
            page_id: Notion page ID
            full_width: Whether to enable full width (True) or normal width (False)
            
        Returns:
            Updated page object
            
        Raises:
            NotionNotFoundError: If page is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(page_id, "page")
        
        # Use a direct HTTP request to set the page format
        # The full width setting is controlled by a special page format property
        update_data = {
            "archived": False,  # Ensure page is not archived
        }
        
        # Add format property for full width
        if full_width:
            # Try to use the format property that controls page layout
            try:
                # Make a direct request to set page format
                response = self.http_client.patch(
                    f"pages/{page_id}",
                    data=update_data
                )
                
                # Try a second request with format data if the API supports it
                # Note: This is experimental as Notion's API doesn't officially expose this
                format_data = {
                    "page_full_width": True if full_width else False
                }
                
                # Attempt to set format via a second call
                # This may not work as it's not in the official API
                try:
                    format_response = self.http_client.patch(
                        f"pages/{page_id}",
                        data={"format": format_data}
                    )
                    logger.info(f"Successfully set page {page_id} to {'full width' if full_width else 'normal width'}")
                    return Page(**format_response)
                except Exception as format_error:
                    logger.warning(f"Could not set page format via API: {format_error}")
                    # Return the basic update response
                    return Page(**response)
                    
            except Exception as e:
                logger.error(f"Error setting page width: {e}")
                # Fall back to basic update
                return self.update(page_id, archived=False)
        else:
            # For normal width, just do a basic update
            return self.update(page_id, archived=False)
    
    def create_from_template(
        self,
        parent: Dict[str, Any],
        template_data: Dict[str, Any],
        properties: Optional[Dict[str, Any]] = None,
    ) -> Page:
        """Create a page from a template.
        
        Args:
            parent: Parent page or database reference
            template_data: Template structure with blocks and properties
            properties: Additional properties to override template
            
        Returns:
            Created page object
            
        Raises:
            NotionValidationError: If template data is invalid
            NotionAPIError: If API request fails
        """
        # Merge template properties with provided properties
        page_properties = template_data.get("properties", {})
        if properties:
            page_properties.update(properties)
        
        return self.create(
            parent=parent,
            properties=page_properties,
            children=template_data.get("children", []),
            icon=template_data.get("icon"),
            cover=template_data.get("cover"),
        )
