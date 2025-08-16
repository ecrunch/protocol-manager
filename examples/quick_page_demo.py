"""
Quick demo: Create a page under Protocol Home
"""

import sys
import os
from datetime import datetime

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_client import NotionClient
from notion_client.utils import (
    create_rich_text,
    create_page_parent,
    create_paragraph_block,
    create_heading_block,
    create_todo_block,
    create_divider_block,
)

def main():
    # Connect to Notion
    client = NotionClient.from_env()
    
    # Your Protocol Home page ID (from the finder script)
    protocol_home_id = "2518f242-f6b7-80c6-ba3a-f6cae6f0809c"
    
    print(f"Creating a new page under Protocol Home...")
    
    # Create page properties
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    page_properties = {
        "title": {
            "title": [create_rich_text(f"New Project Page - {current_time}")]
        }
    }
    
    # Create content
    content_blocks = [
        create_heading_block("🚀 Welcome to My New Project", level=1),
        create_paragraph_block(
            "This page was created programmatically using the Notion Python client!"
        ),
        
        create_divider_block(),
        
        create_heading_block("📋 Project Tasks", level=2),
        create_todo_block("Define project scope", checked=False),
        create_todo_block("Set up development environment", checked=True),
        create_todo_block("Create initial documentation", checked=False),
        
        create_divider_block(),
        
        create_paragraph_block(
            "You can easily add more content, update properties, and organize your workspace!",
            italic=True,
            color="gray"
        )
    ]
    
    try:
        # Create the page
        new_page = client.pages.create(
            parent=create_page_parent(protocol_home_id),
            properties=page_properties,
            children=content_blocks
        )
        
        print(f"✅ Success! Created page:")
        print(f"   Title: {page_properties['title']['title'][0]['text']['content']}")
        print(f"   ID: {new_page.id}")
        print(f"   URL: {new_page.url}")
        
        # Add some additional content
        print(f"\n📝 Adding more content...")
        additional_blocks = [
            create_divider_block(),
            create_heading_block("✨ Additional Notes", level=2),
            create_paragraph_block("This content was added after page creation!", bold=True),
        ]
        
        client.blocks.append_children(new_page.id, additional_blocks)
        print(f"✅ Added additional content!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
