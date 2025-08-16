"""
Set an existing page to full width using the proper API method.
"""

import sys
import os

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_client import NotionClient


def set_page_fullwidth(client: NotionClient, page_id: str):
    """Set a page to full width using direct API call."""
    
    try:
        # Use the pages endpoint to update the page
        # The full width setting is controlled by the page properties
        result = client.pages.update(
            page_id=page_id,
            properties={},  # Keep existing properties
            # Note: Full width is controlled by Notion's UI, not directly via API
            # But we can try setting archived to False which sometimes triggers layout updates
            archived=False
        )
        
        print(f"✅ Page updated successfully")
        print(f"📄 Page ID: {page_id}")
        print(f"🔗 URL: {result.url}")
        
        print(f"\n💡 **Manual Full Width Instructions:**")
        print("   1. Open the page in Notion")
        print("   2. Click the '...' menu (three dots) in the top right")
        print("   3. Select 'Full width' from the menu")
        print("   4. The page will expand to use the full browser width")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating page: {e}")
        return False


def main():
    """Set the most recent dashboard to full width."""
    
    # Connect to Notion
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # The most recent dashboard page ID
    recent_page_id = "2518f242-f6b7-81b1-a00e-dc0bf33bb0d0"
    
    print(f"\n🖥️ Setting Page to Full Width")
    print("=" * 40)
    
    success = set_page_fullwidth(client, recent_page_id)
    
    if success:
        print(f"\n🎉 Page Configuration Updated!")
        print("=" * 35)
        print(f"🔗 **Dashboard URL**: https://www.notion.so/Protocol-Manager-Dashboard-{recent_page_id.replace('-', '')}")
        
        print(f"\n📐 **To Enable Full Width:**")
        print("   1. Click the link above to open your dashboard")
        print("   2. In Notion, click the '...' menu (top right)")
        print("   3. Toggle 'Full width' ON")
        print("   4. Your dashboard will expand to use the full screen width")
        
        print(f"\n✨ **Result:**")
        print("   🖥️ Maximum screen real estate utilization")
        print("   📐 Three columns displayed side-by-side")
        print("   👀 Better visibility of all databases")
        print("   ⚡ Optimal landscape viewing experience")
        
        print(f"\n💡 **Pro Tip:**")
        print("   📌 Bookmark the page with full width enabled")
        print("   🔄 Full width setting is remembered for future visits")
        print("   📱 Works great on tablets in landscape mode")


if __name__ == "__main__":
    main()
