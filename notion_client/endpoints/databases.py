"""
Databases endpoint for the Notion API client.

This module provides methods for interacting with Notion databases API,
including creating, retrieving, updating databases and querying database contents.
"""

import logging
from typing import Any, Dict, List, Optional, Generator

from .base import BaseEndpoint
from ..models.database import Database, DatabaseCreateRequest, DatabaseUpdateRequest
from ..models.page import Page


logger = logging.getLogger(__name__)


class DatabasesEndpoint(BaseEndpoint):
    """Databases API endpoint handler."""
    
    def create(
        self,
        parent: Dict[str, Any],
        title: List[Dict[str, Any]],
        properties: Dict[str, Any],
        description: Optional[List[Dict[str, Any]]] = None,
        icon: Optional[Dict[str, Any]] = None,
        cover: Optional[Dict[str, Any]] = None,
        is_inline: bool = False,
    ) -> Database:
        """Create a new database.
        
        Args:
            parent: Parent page reference
            title: Database title as rich text
            properties: Database property schema
            description: Database description as rich text
            icon: Database icon
            cover: Database cover image
            is_inline: Whether database should be inline
            
        Returns:
            Created database object
            
        Raises:
            NotionValidationError: If request data is invalid
            NotionAPIError: If API request fails
        """
        # Construct request data
        request_data = {
            "parent": parent,
            "title": title,
            "properties": properties,
            "is_inline": is_inline,
        }
        
        if description is not None:
            request_data["description"] = description
        
        if icon is not None:
            request_data["icon"] = icon
        
        if cover is not None:
            request_data["cover"] = cover
        
        # Remove None values
        request_data = self._clean_dict(request_data)
        
        logger.info(f"Creating database with title: {title}")
        response = self.http_client.post("databases", data=request_data)
        
        return Database(**response)
    
    def retrieve(self, database_id: str) -> Database:
        """Retrieve a database by ID.
        
        Args:
            database_id: Notion database ID
            
        Returns:
            Database object
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(database_id, "database")
        
        logger.info(f"Retrieving database: {database_id}")
        response = self.http_client.get(f"databases/{database_id}")
        
        return Database(**response)
    
    def update(
        self,
        database_id: str,
        title: Optional[List[Dict[str, Any]]] = None,
        description: Optional[List[Dict[str, Any]]] = None,
        properties: Optional[Dict[str, Any]] = None,
        icon: Optional[Dict[str, Any]] = None,
        cover: Optional[Dict[str, Any]] = None,
        archived: Optional[bool] = None,
        in_trash: Optional[bool] = None,
    ) -> Database:
        """Update a database.
        
        Args:
            database_id: Notion database ID
            title: Updated database title
            description: Updated database description
            properties: Updated property schema
            icon: Updated database icon
            cover: Updated database cover
            archived: Whether to archive the database
            in_trash: Whether to move database to trash
            
        Returns:
            Updated database object
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionValidationError: If request data is invalid
            NotionAPIError: If API request fails
        """
        self._validate_id(database_id, "database")
        
        # Construct update data
        update_data = {}
        
        if title is not None:
            update_data["title"] = title
        
        if description is not None:
            update_data["description"] = description
        
        if properties is not None:
            update_data["properties"] = properties
        
        if icon is not None:
            update_data["icon"] = icon
        
        if cover is not None:
            update_data["cover"] = cover
        
        if archived is not None:
            update_data["archived"] = archived
        
        if in_trash is not None:
            update_data["in_trash"] = in_trash
        
        if not update_data:
            raise ValueError("At least one field must be provided for update")
        
        logger.info(f"Updating database: {database_id}")
        response = self.http_client.patch(f"databases/{database_id}", data=update_data)
        
        return Database(**response)
    
    def query(
        self,
        database_id: str,
        filter_criteria: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        start_cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Query a database.
        
        Args:
            database_id: Notion database ID
            filter_criteria: Filter conditions
            sorts: Sort criteria
            start_cursor: Pagination cursor
            page_size: Number of items per page
            
        Returns:
            Query results with pages
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionValidationError: If query parameters are invalid
            NotionAPIError: If API request fails
        """
        self._validate_id(database_id, "database")
        
        # Construct query data
        query_data = {}
        
        if filter_criteria is not None:
            query_data["filter"] = filter_criteria
        
        if sorts is not None:
            query_data["sorts"] = sorts
        
        if start_cursor is not None:
            query_data["start_cursor"] = start_cursor
        
        if page_size is not None:
            query_data["page_size"] = page_size
        
        logger.info(f"Querying database: {database_id}")
        response = self.http_client.post(
            f"databases/{database_id}/query",
            data=query_data or {},
        )
        
        return response
    
    def query_all(
        self,
        database_id: str,
        filter_criteria: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        page_size: int = 100,
    ) -> List[Page]:
        """Query all pages from a database.
        
        Args:
            database_id: Notion database ID
            filter_criteria: Filter conditions
            sorts: Sort criteria
            page_size: Number of items per page
            
        Returns:
            List of all matching pages
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(database_id, "database")
        
        # Prepare query data
        query_data = {}
        if filter_criteria is not None:
            query_data["filter"] = filter_criteria
        if sorts is not None:
            query_data["sorts"] = sorts
        
        endpoint = f"databases/{database_id}/query"
        pages_data = self._get_all_paginated(
            endpoint, data=query_data, method="POST", page_size=page_size
        )
        
        return [Page(**page) for page in pages_data]
    
    def iterate_pages(
        self,
        database_id: str,
        filter_criteria: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        page_size: int = 100,
    ) -> Generator[Page, None, None]:
        """Iterate through database pages.
        
        Args:
            database_id: Notion database ID
            filter_criteria: Filter conditions
            sorts: Sort criteria
            page_size: Number of items per page
            
        Yields:
            Individual pages from the database
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(database_id, "database")
        
        # Prepare query data
        query_data = {}
        if filter_criteria is not None:
            query_data["filter"] = filter_criteria
        if sorts is not None:
            query_data["sorts"] = sorts
        
        endpoint = f"databases/{database_id}/query"
        
        for page_data in self._paginate(
            endpoint, data=query_data, method="POST", page_size=page_size
        ):
            yield Page(**page_data)
    
    def archive(self, database_id: str) -> Database:
        """Archive a database.
        
        Args:
            database_id: Notion database ID
            
        Returns:
            Archived database object
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionAPIError: If API request fails
        """
        return self.update(database_id, archived=True)
    
    def unarchive(self, database_id: str) -> Database:
        """Unarchive a database.
        
        Args:
            database_id: Notion database ID
            
        Returns:
            Unarchived database object
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionAPIError: If API request fails
        """
        return self.update(database_id, archived=False)
    
    def delete(self, database_id: str) -> Database:
        """Move a database to trash.
        
        Args:
            database_id: Notion database ID
            
        Returns:
            Deleted database object
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionAPIError: If API request fails
        """
        return self.update(database_id, in_trash=True)
    
    def restore(self, database_id: str) -> Database:
        """Restore a database from trash.
        
        Args:
            database_id: Notion database ID
            
        Returns:
            Restored database object
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionAPIError: If API request fails
        """
        return self.update(database_id, in_trash=False)
    
    def add_property(
        self,
        database_id: str,
        property_name: str,
        property_config: Dict[str, Any],
    ) -> Database:
        """Add a new property to a database.
        
        Args:
            database_id: Notion database ID
            property_name: Name of the new property
            property_config: Property configuration
            
        Returns:
            Updated database object
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionValidationError: If property config is invalid
            NotionAPIError: If API request fails
        """
        return self.update(
            database_id,
            properties={property_name: property_config},
        )
    
    def remove_property(
        self,
        database_id: str,
        property_name: str,
    ) -> Database:
        """Remove a property from a database.
        
        Args:
            database_id: Notion database ID
            property_name: Name of the property to remove
            
        Returns:
            Updated database object
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionAPIError: If API request fails
        """
        return self.update(
            database_id,
            properties={property_name: None},
        )
    
    def rename_property(
        self,
        database_id: str,
        property_name: str,
        new_name: str,
    ) -> Database:
        """Rename a property in a database.
        
        Args:
            database_id: Notion database ID
            property_name: Current name of the property
            new_name: New name for the property
            
        Returns:
            Updated database object
            
        Raises:
            NotionNotFoundError: If database is not found
            NotionAPIError: If API request fails
        """
        return self.update(
            database_id,
            properties={property_name: {"name": new_name}},
        )
