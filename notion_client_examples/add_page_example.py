"""
Example of how to add a page to a parent page using the Notion Python client.

This script demonstrates different ways to create pages with various content.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the Python path so we can import notion_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_client import NotionClient
from notion_client.utils import (
    create_rich_text,
    create_page_parent,
    create_paragraph_block,
    create_heading_block,
    create_todo_block,
    create_bulleted_list_item,
    create_numbered_list_item,
    create_quote_block,
    create_callout_block,
    create_divider_block,
    create_code_block,
)


def create_sample_page(client: NotionClient, parent_page_id: str):
    """Create a sample page with various content types."""
    
    print(f"Creating a new page under parent: {parent_page_id}")
    
    # Define page properties (title is required)
    page_properties = {
        "title": {
            "title": [create_rich_text(f"My New Page - {datetime.now().strftime('%Y-%m-%d %H:%M')}")]
        }
    }
    
    # Create content blocks
    page_blocks = [
        create_heading_block("Welcome to My New Page!", level=1),
        create_paragraph_block(
            "This page was created using the Notion Python client. "
            "It demonstrates various types of content you can add.",
            color="gray"
        ),
        
        create_divider_block(),
        
        create_heading_block("Task List", level=2),
        create_todo_block("Set up Notion client", checked=True),
        create_todo_block("Create my first page", checked=True),
        create_todo_block("Add more content", checked=False),
        create_todo_block("Explore advanced features", checked=False),
        
        create_divider_block(),
        
        create_heading_block("Key Features", level=2),
        create_bulleted_list_item("Complete API coverage"),
        create_bulleted_list_item("Type safety with Pydantic"),
        create_bulleted_list_item("Rate limiting and error handling"),
        create_bulleted_list_item("Easy-to-use helper functions"),
        
        create_divider_block(),
        
        create_heading_block("Code Example", level=2),
        create_paragraph_block("Here's how easy it is to create content:"),
        create_code_block(
            '''from notion_client import NotionClient
from notion_client.utils import create_paragraph_block

client = NotionClient.from_env()
block = create_paragraph_block("Hello, Notion!")
client.blocks.append_children(page_id, [block])''',
            language="python"
        ),
        
        create_divider_block(),
        
        create_quote_block(
            "The best way to predict the future is to create it. - Peter Drucker"
        ),
        
        create_callout_block(
            "💡 Pro tip: You can customize colors, add links, and create complex layouts!",
            icon="💡",
            color="blue"
        ),
    ]
    
    try:
        # Create the page
        new_page = client.pages.create(
            parent=create_page_parent(parent_page_id),
            properties=page_properties,
            children=page_blocks
        )
        
        print(f"✅ Page created successfully!")
        print(f"   Page ID: {new_page.id}")
        print(f"   URL: {new_page.url}")
        
        return new_page
        
    except Exception as e:
        print(f"❌ Error creating page: {e}")
        return None


def add_more_content(client: NotionClient, page_id: str):
    """Add additional content to an existing page."""
    
    print(f"\nAdding more content to page: {page_id}")
    
    additional_blocks = [
        create_divider_block(),
        create_heading_block("Additional Content", level=2),
        create_paragraph_block(
            "This content was added after the page was created. "
            "You can dynamically add blocks to any page!",
            bold=True
        ),
        create_numbered_list_item("First step: Create the page"),
        create_numbered_list_item("Second step: Add initial content"),
        create_numbered_list_item("Third step: Add more content as needed"),
        create_callout_block(
            "🎉 You can keep adding content indefinitely!",
            icon="🎉",
            color="green"
        )
    ]
    
    try:
        result = client.blocks.append_children(page_id, additional_blocks)
        print(f"✅ Added {len(additional_blocks)} new blocks")
        return True
        
    except Exception as e:
        print(f"❌ Error adding content: {e}")
        return False


def main():
    """Main function to demonstrate page creation."""
    
    # Initialize the client
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\nMake sure you have NOTION_API_TOKEN in your .env file")
        return
    
    # Get parent page ID from environment or prompt user
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    
    if not parent_page_id:
        print("\n📝 To create a page, you need a parent page ID.")
        print("You can:")
        print("1. Add NOTION_PARENT_PAGE_ID to your .env file")
        print("2. Or enter a page ID now")
        
        parent_page_id = input("\nEnter parent page ID (or press Enter to skip): ").strip()
        
        if not parent_page_id:
            print("Skipping page creation. Set NOTION_PARENT_PAGE_ID to try this example.")
            return
    
    # Create the sample page
    new_page = create_sample_page(client, parent_page_id)
    
    if new_page:
        # Add more content to demonstrate dynamic updates
        add_more_content(client, new_page.id)
        
        print(f"\n🎉 All done! Check out your new page:")
        print(f"   {new_page.url}")
    
    print("\n💡 Tips:")
    print("- You can create pages under any page you have access to")
    print("- Use different block types to create rich content")
    print("- Pages can be organized hierarchically")
    print("- You can update page properties and content anytime")


if __name__ == "__main__":
    main()
