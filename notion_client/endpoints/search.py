"""
Search endpoint for the Notion API client.

This module provides methods for searching pages and databases
across the Notion workspace.
"""

import logging
from typing import Any, Dict, List, Optional, Literal, Generator, Union

from .base import BaseEndpoint
from ..models.page import Page
from ..models.database import Database


logger = logging.getLogger(__name__)


class SearchEndpoint(BaseEndpoint):
    """Search API endpoint handler."""
    
    def search(
        self,
        query: Optional[str] = None,
        sort: Optional[Dict[str, str]] = None,
        filter_criteria: Optional[Dict[str, Any]] = None,
        start_cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Search for pages and databases.
        
        Args:
            query: Search query text
            sort: Sort criteria (e.g., {"direction": "ascending", "timestamp": "last_edited_time"})
            filter_criteria: Filter criteria to narrow search
            start_cursor: Pagination cursor
            page_size: Number of items per page
            
        Returns:
            Search results with pages and databases
            
        Raises:
            NotionValidationError: If search parameters are invalid
            NotionAPIError: If API request fails
        """
        # Construct search data
        search_data = {}
        
        if query is not None:
            search_data["query"] = query
        
        if sort is not None:
            search_data["sort"] = sort
        
        if filter_criteria is not None:
            search_data["filter"] = filter_criteria
        
        if start_cursor is not None:
            search_data["start_cursor"] = start_cursor
        
        if page_size is not None:
            search_data["page_size"] = page_size
        
        logger.info(f"Searching with query: {query}")
        response = self.http_client.post("search", data=search_data)
        
        return response
    
    def search_all(
        self,
        query: Optional[str] = None,
        sort: Optional[Dict[str, str]] = None,
        filter_criteria: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
    ) -> List[Union[Page, Database]]:
        """Search all pages and databases (all pages).
        
        Args:
            query: Search query text
            sort: Sort criteria
            filter_criteria: Filter criteria
            page_size: Number of items per page
            
        Returns:
            List of all matching pages and databases
            
        Raises:
            NotionAPIError: If API request fails
        """
        search_data = {}
        if query is not None:
            search_data["query"] = query
        if sort is not None:
            search_data["sort"] = sort
        if filter_criteria is not None:
            search_data["filter"] = filter_criteria
        
        results_data = self._get_all_paginated(
            "search", data=search_data, method="POST", page_size=page_size
        )
        
        results = []
        for item in results_data:
            if item.get("object") == "page":
                results.append(Page(**item))
            elif item.get("object") == "database":
                results.append(Database(**item))
        
        return results
    
    def iterate_results(
        self,
        query: Optional[str] = None,
        sort: Optional[Dict[str, str]] = None,
        filter_criteria: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
    ) -> Generator[Union[Page, Database], None, None]:
        """Iterate through search results.
        
        Args:
            query: Search query text
            sort: Sort criteria
            filter_criteria: Filter criteria
            page_size: Number of items per page
            
        Yields:
            Individual pages and databases from search results
            
        Raises:
            NotionAPIError: If API request fails
        """
        search_data = {}
        if query is not None:
            search_data["query"] = query
        if sort is not None:
            search_data["sort"] = sort
        if filter_criteria is not None:
            search_data["filter"] = filter_criteria
        
        for item in self._paginate(
            "search", data=search_data, method="POST", page_size=page_size
        ):
            if item.get("object") == "page":
                yield Page(**item)
            elif item.get("object") == "database":
                yield Database(**item)
    
    def search_pages(
        self,
        query: Optional[str] = None,
        sort: Optional[Dict[str, str]] = None,
        page_size: int = 100,
    ) -> List[Page]:
        """Search for pages only.
        
        Args:
            query: Search query text
            sort: Sort criteria
            page_size: Number of items per page
            
        Returns:
            List of matching pages
            
        Raises:
            NotionAPIError: If API request fails
        """
        filter_criteria = {"value": "page", "property": "object"}
        
        results = self.search_all(
            query=query,
            sort=sort,
            filter_criteria=filter_criteria,
            page_size=page_size,
        )
        
        return [result for result in results if isinstance(result, Page)]
    
    def search_databases(
        self,
        query: Optional[str] = None,
        sort: Optional[Dict[str, str]] = None,
        page_size: int = 100,
    ) -> List[Database]:
        """Search for databases only.
        
        Args:
            query: Search query text
            sort: Sort criteria
            page_size: Number of items per page
            
        Returns:
            List of matching databases
            
        Raises:
            NotionAPIError: If API request fails
        """
        filter_criteria = {"value": "database", "property": "object"}
        
        results = self.search_all(
            query=query,
            sort=sort,
            filter_criteria=filter_criteria,
            page_size=page_size,
        )
        
        return [result for result in results if isinstance(result, Database)]
    
    def search_by_title(
        self,
        title: str,
        object_type: Optional[Literal["page", "database"]] = None,
        exact_match: bool = False,
    ) -> List[Union[Page, Database]]:
        """Search for pages/databases by title.
        
        Args:
            title: Title to search for
            object_type: Limit search to pages or databases
            exact_match: Whether to match title exactly
            
        Returns:
            List of matching pages and/or databases
            
        Raises:
            NotionAPIError: If API request fails
        """
        # Use title as query
        query = title
        
        # Set up filter if object type specified
        filter_criteria = None
        if object_type:
            filter_criteria = {"value": object_type, "property": "object"}
        
        results = self.search_all(
            query=query,
            filter_criteria=filter_criteria,
        )
        
        if not exact_match:
            return results
        
        # Filter for exact title matches
        exact_matches = []
        for result in results:
            if isinstance(result, Page):
                # For pages, we need to check the title property
                title_prop = result.properties.get("title") or result.properties.get("Name")
                if title_prop and title_prop.get("title"):
                    page_title = "".join([
                        text.get("plain_text", "") 
                        for text in title_prop["title"]
                    ])
                    if page_title == title:
                        exact_matches.append(result)
            elif isinstance(result, Database):
                # For databases, check the title field
                if result.title:
                    db_title = "".join([
                        text.plain_text for text in result.title
                    ])
                    if db_title == title:
                        exact_matches.append(result)
        
        return exact_matches
    
    def find_page_by_id_or_title(
        self,
        identifier: str,
    ) -> Optional[Page]:
        """Find a page by ID or title.
        
        Args:
            identifier: Page ID or title
            
        Returns:
            Page object if found, None otherwise
            
        Raises:
            NotionAPIError: If API request fails
        """
        # First try to treat as ID
        try:
            if len(identifier.replace("-", "")) == 32:
                from ..endpoints.pages import PagesEndpoint
                pages_endpoint = PagesEndpoint(self.http_client)
                return pages_endpoint.retrieve(identifier)
        except Exception:
            pass
        
        # Try searching by title
        pages = self.search_pages(query=identifier)
        for page in pages:
            title_prop = page.properties.get("title") or page.properties.get("Name")
            if title_prop and title_prop.get("title"):
                page_title = "".join([
                    text.get("plain_text", "") 
                    for text in title_prop["title"]
                ])
                if page_title == identifier:
                    return page
        
        return None
    
    def find_database_by_id_or_title(
        self,
        identifier: str,
    ) -> Optional[Database]:
        """Find a database by ID or title.
        
        Args:
            identifier: Database ID or title
            
        Returns:
            Database object if found, None otherwise
            
        Raises:
            NotionAPIError: If API request fails
        """
        # First try to treat as ID
        try:
            if len(identifier.replace("-", "")) == 32:
                from ..endpoints.databases import DatabasesEndpoint
                databases_endpoint = DatabasesEndpoint(self.http_client)
                return databases_endpoint.retrieve(identifier)
        except Exception:
            pass
        
        # Try searching by title
        databases = self.search_databases(query=identifier)
        for database in databases:
            if database.title:
                db_title = "".join([
                    text.plain_text for text in database.title
                ])
                if db_title == identifier:
                    return database
        
        return None
