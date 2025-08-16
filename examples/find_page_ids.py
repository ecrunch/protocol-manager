"""
Helper script to find page IDs in your Notion workspace.

This script helps you find page IDs that you can use as parent pages.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_client import NotionClient


def find_pages(client: NotionClient, query: str = ""):
    """Search for pages and display their IDs."""
    
    print(f"🔍 Searching for pages{' with query: ' + query if query else ''}...")
    
    try:
        # Search for pages
        if query:
            results = client.search.search_pages(query=query)
        else:
            # Get recent pages (search with no query often returns recent items)
            results = client.search.search_pages(query="")
        
        if not results:
            print("No pages found.")
            return []
        
        print(f"\nFound {len(results)} pages:")
        print("-" * 80)
        
        page_info = []
        for i, page in enumerate(results, 1):
            # Get page title
            title = "Untitled"
            if page.properties:
                for prop_name, prop_data in page.properties.items():
                    if prop_data.get('type') == 'title' and prop_data.get('title'):
                        title = "".join([
                            text.get('plain_text', '') 
                            for text in prop_data['title']
                        ])
                        break
            
            # Get parent info
            parent_type = page.parent.type if page.parent else "Unknown"
            parent_id = ""
            if page.parent:
                if parent_type == "page_id":
                    parent_id = page.parent.page_id
                elif parent_type == "database_id":
                    parent_id = page.parent.database_id
                elif parent_type == "workspace":
                    parent_id = "workspace"
            
            page_info.append({
                'title': title,
                'id': page.id,
                'url': page.url,
                'parent_type': parent_type,
                'parent_id': parent_id
            })
            
            print(f"{i:2d}. {title}")
            print(f"    ID: {page.id}")
            print(f"    URL: {page.url}")
            print(f"    Parent: {parent_type} ({parent_id})")
            print()
        
        return page_info
        
    except Exception as e:
        print(f"❌ Error searching pages: {e}")
        return []


def main():
    """Main function."""
    
    # Initialize client
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print("\n" + "="*60)
    print("NOTION PAGE ID FINDER")
    print("="*60)
    
    # Option 1: Search all pages
    print("\n1. Recent/All pages:")
    all_pages = find_pages(client)
    
    # Option 2: Search with query
    if all_pages:
        print("\n2. Search for specific pages:")
        query = input("Enter search term (or press Enter to skip): ").strip()
        if query:
            search_results = find_pages(client, query)
    
    # Show instructions
    print("\n" + "="*60)
    print("HOW TO USE THESE PAGE IDs:")
    print("="*60)
    print("""
To create a child page under any of these pages:

1. Copy the Page ID from above
2. Add it to your .env file:
   NOTION_PARENT_PAGE_ID=paste_page_id_here

3. Run the page creation example:
   C:\\Users\\casey\\Code\\protocol-manager\\.conda\\python.exe examples\\add_page_example.py

Or use it directly in your code:
    client.pages.create(
        parent={"type": "page_id", "page_id": "your_page_id_here"},
        properties={"title": {"title": [{"type": "text", "text": {"content": "New Page"}}]}},
        children=[...]
    )
""")


if __name__ == "__main__":
    main()
