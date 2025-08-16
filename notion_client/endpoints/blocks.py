"""
Blocks endpoint for the Notion API client.

This module provides methods for interacting with Notion blocks API,
including retrieving, updating, deleting blocks and managing block children.
"""

import logging
from typing import Any, Dict, List, Optional, Generator

from .base import BaseEndpoint
from ..models.block import Block


logger = logging.getLogger(__name__)


class BlocksEndpoint(BaseEndpoint):
    """Blocks API endpoint handler."""
    
    def retrieve(self, block_id: str) -> Block:
        """Retrieve a block by ID.
        
        Args:
            block_id: Notion block ID
            
        Returns:
            Block object
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(block_id, "block")
        
        logger.info(f"Retrieving block: {block_id}")
        response = self.http_client.get(f"blocks/{block_id}")
        
        return Block(**response)
    
    def update(
        self,
        block_id: str,
        **block_data: Any,
    ) -> Block:
        """Update a block.
        
        Args:
            block_id: Notion block ID
            **block_data: Block-specific update data
            
        Returns:
            Updated block object
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionValidationError: If request data is invalid
            NotionAPIError: If API request fails
        """
        self._validate_id(block_id, "block")
        
        if not block_data:
            raise ValueError("Block update data must be provided")
        
        # Remove None values
        update_data = self._clean_dict(block_data)
        
        logger.info(f"Updating block: {block_id}")
        response = self.http_client.patch(f"blocks/{block_id}", data=update_data)
        
        return Block(**response)
    
    def delete(self, block_id: str) -> Block:
        """Delete a block.
        
        Args:
            block_id: Notion block ID
            
        Returns:
            Deleted block object (archived=True)
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(block_id, "block")
        
        logger.info(f"Deleting block: {block_id}")
        response = self.http_client.delete(f"blocks/{block_id}")
        
        return Block(**response)
    
    def get_children(
        self,
        block_id: str,
        start_cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Retrieve children of a block.
        
        Args:
            block_id: Notion block ID
            start_cursor: Pagination cursor
            page_size: Number of items per page
            
        Returns:
            List response with child blocks
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(block_id, "block")
        
        params = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size
        
        logger.info(f"Retrieving children for block: {block_id}")
        response = self.http_client.get(
            f"blocks/{block_id}/children",
            params=params or None,
        )
        
        return response
    
    def get_all_children(
        self,
        block_id: str,
        page_size: int = 100,
    ) -> List[Block]:
        """Get all children of a block.
        
        Args:
            block_id: Notion block ID
            page_size: Number of items per page
            
        Returns:
            List of all child blocks
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionAPIError: If API request fails
        """
        self._validate_id(block_id, "block")
        
        endpoint = f"blocks/{block_id}/children"
        children_data = self._get_all_paginated(endpoint, page_size=page_size)
        
        return [Block(**child) for child in children_data]
    
    def append_children(
        self,
        block_id: str,
        children: List[Dict[str, Any]],
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Append children to a block.
        
        Args:
            block_id: Notion block ID
            children: List of child blocks to append
            after: Block ID to insert after (optional)
            
        Returns:
            Response with created blocks
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionValidationError: If children data is invalid
            NotionAPIError: If API request fails
        """
        self._validate_id(block_id, "block")
        
        if not children:
            raise ValueError("Children list cannot be empty")
        
        request_data = {"children": children}
        
        if after:
            request_data["after"] = after
        
        logger.info(f"Appending {len(children)} children to block: {block_id}")
        response = self.http_client.patch(
            f"blocks/{block_id}/children",
            data=request_data,
        )
        
        return response
    
    def create_child_blocks(
        self,
        parent_id: str,
        blocks: List[Dict[str, Any]],
    ) -> List[Block]:
        """Create multiple child blocks at once.
        
        Args:
            parent_id: Parent block or page ID
            blocks: List of block definitions
            
        Returns:
            List of created blocks
            
        Raises:
            NotionValidationError: If block data is invalid
            NotionAPIError: If API request fails
        """
        response = self.append_children(parent_id, blocks)
        return [Block(**block) for block in response.get("results", [])]
    
    def archive(self, block_id: str) -> Block:
        """Archive a block.
        
        Args:
            block_id: Notion block ID
            
        Returns:
            Archived block object
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionAPIError: If API request fails
        """
        return self.update(block_id, archived=True)
    
    def unarchive(self, block_id: str) -> Block:
        """Unarchive a block.
        
        Args:
            block_id: Notion block ID
            
        Returns:
            Unarchived block object
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionAPIError: If API request fails
        """
        return self.update(block_id, archived=False)
    
    def move_to_trash(self, block_id: str) -> Block:
        """Move a block to trash.
        
        Args:
            block_id: Notion block ID
            
        Returns:
            Block object moved to trash
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionAPIError: If API request fails
        """
        return self.update(block_id, in_trash=True)
    
    def restore_from_trash(self, block_id: str) -> Block:
        """Restore a block from trash.
        
        Args:
            block_id: Notion block ID
            
        Returns:
            Restored block object
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionAPIError: If API request fails
        """
        return self.update(block_id, in_trash=False)
    
    def get_block_tree(
        self,
        block_id: str,
        max_depth: int = 10,
    ) -> Dict[str, Any]:
        """Get complete block tree with all nested children.
        
        Args:
            block_id: Root block ID
            max_depth: Maximum depth to traverse
            
        Returns:
            Block tree with nested children
            
        Raises:
            NotionNotFoundError: If block is not found
            NotionAPIError: If API request fails
        """
        def _get_children_recursive(parent_id: str, depth: int = 0) -> List[Dict[str, Any]]:
            """Recursively get all children."""
            if depth >= max_depth:
                return []
            
            children = self.get_all_children(parent_id)
            result = []
            
            for child in children:
                child_dict = child.dict()
                
                # Get nested children if block has children
                if child.has_children:
                    child_dict["children"] = _get_children_recursive(
                        child.id, depth + 1
                    )
                
                result.append(child_dict)
            
            return result
        
        # Get root block
        root_block = self.retrieve(block_id)
        root_dict = root_block.dict()
        
        # Get all nested children
        if root_block.has_children:
            root_dict["children"] = _get_children_recursive(block_id)
        
        return root_dict
