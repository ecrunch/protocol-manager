"""
Basic usage examples for the Notion Python client.

This script demonstrates how to use the main features of the Notion client
including creating pages, working with blocks, and querying databases.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the Python path so we can import notion_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_client import NotionClient
from notion_client.utils import (
    create_rich_text,
    create_page_parent,
    create_database_parent,
    create_paragraph_block,
    create_heading_block,
    create_todo_block,
    create_bulleted_list_item,
)

# Load environment variables
load_dotenv()


def main():
    """Main example function."""
    # Initialize client from environment variables
    # Make sure to set NOTION_API_TOKEN in your .env file
    client = NotionClient.from_env()
    
    # Test connection
    print("Testing connection...")
    if client.test_connection():
        print("✅ Connected to Notion API")
    else:
        print("❌ Failed to connect to Notion API")
        return
    
    # Get workspace info
    print("\n📋 Workspace Info:")
    workspace_info = client.get_workspace_info()
    print(f"Bot User: {workspace_info.get('bot_user', {}).get('name', 'Unknown')}")
    print(f"Workspace: {workspace_info.get('workspace_name', 'Unknown')}")
    print(f"API Version: {workspace_info.get('api_version', 'Unknown')}")
    
    # Example 1: Search for pages and databases
    print("\n🔍 Searching for content...")
    try:
        search_results = client.search.search_all(query="test", page_size=5)
        print(f"Found {len(search_results)} items")
        
        for item in search_results:
            item_type = item.__class__.__name__
            if hasattr(item, 'title') and item.title:
                # Database
                title = "".join([t.plain_text for t in item.title])
            elif hasattr(item, 'properties') and item.properties:
                # Page - try to get title from properties
                title_prop = item.properties.get('title') or item.properties.get('Name')
                if title_prop and title_prop.get('title'):
                    title = "".join([t.get('plain_text', '') for t in title_prop['title']])
                else:
                    title = "Untitled"
            else:
                title = "Unknown"
            
            print(f"  - {item_type}: {title}")
    
    except Exception as e:
        print(f"Search error: {e}")
    
    # Example 2: List users
    print("\n👥 Workspace Users:")
    try:
        users = client.users.list_all()
        for user in users[:5]:  # Show first 5 users
            name = user.name or "Unknown"
            user_type = user.type
            print(f"  - {name} ({user_type})")
    
    except Exception as e:
        print(f"Users error: {e}")
    
    # Example 3: Create a simple page (if parent page ID is provided)
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    
    if parent_page_id:
        print(f"\n📄 Creating a new page...")
        try:
            # Create page content
            page_properties = {
                "title": {
                    "title": [create_rich_text("My Test Page")]
                }
            }
            
            # Create some blocks
            page_blocks = [
                create_heading_block("Welcome to my test page!", level=1),
                create_paragraph_block("This is a test page created using the Notion Python client."),
                create_todo_block("Complete the Notion client", checked=True),
                create_todo_block("Write documentation", checked=False),
                create_bulleted_list_item("Feature 1: Complete API coverage"),
                create_bulleted_list_item("Feature 2: Type safety with Pydantic"),
                create_bulleted_list_item("Feature 3: Rate limiting and retries"),
            ]
            
            # Create the page
            new_page = client.pages.create(
                parent=create_page_parent(parent_page_id),
                properties=page_properties,
                children=page_blocks
            )
            
            print(f"✅ Created page: {new_page.id}")
            print(f"   URL: {new_page.url}")
            
            # Example 4: Add more content to the page
            print("\n📝 Adding more content...")
            additional_blocks = [
                create_heading_block("Additional Section", level=2),
                create_paragraph_block("This content was added after page creation.", bold=True),
            ]
            
            client.blocks.append_children(new_page.id, additional_blocks)
            print("✅ Added additional content")
            
            # Example 5: Retrieve the page we just created
            print("\n📖 Retrieving the page...")
            retrieved_page = client.pages.retrieve(new_page.id)
            print(f"✅ Retrieved page: {retrieved_page.id}")
            print(f"   Created: {retrieved_page.created_time}")
            print(f"   Last edited: {retrieved_page.last_edited_time}")
        
        except Exception as e:
            print(f"Page creation error: {e}")
    
    else:
        print("\n💡 To test page creation, set NOTION_PARENT_PAGE_ID in your .env file")
    
    # Example 6: Query a database (if database ID is provided)
    database_id = os.getenv("NOTION_DATABASE_ID")
    
    if database_id:
        print(f"\n🗃️  Querying database...")
        try:
            # Get database info
            database = client.databases.retrieve(database_id)
            db_title = "".join([t.plain_text for t in database.title])
            print(f"Database: {db_title}")
            
            # Query first 5 pages
            pages = client.databases.query_all(
                database_id=database_id,
                page_size=5
            )
            
            print(f"Found {len(pages)} pages in database")
            for page in pages:
                # Try to get page title
                title_prop = None
                for prop_name, prop_data in page.properties.items():
                    if prop_data.get('type') == 'title':
                        title_prop = prop_data
                        break
                
                if title_prop and title_prop.get('title'):
                    title = "".join([t.get('plain_text', '') for t in title_prop['title']])
                else:
                    title = "Untitled"
                
                print(f"  - {title}")
        
        except Exception as e:
            print(f"Database query error: {e}")
    
    else:
        print("\n💡 To test database queries, set NOTION_DATABASE_ID in your .env file")
    
    print("\n✨ Example completed!")


if __name__ == "__main__":
    main()
