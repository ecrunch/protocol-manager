"""
Create a true column-based dashboard for optimal landscape viewing.

This creates a dashboard with actual Notion columns for side-by-side layout.
"""

import sys
import os
from datetime import datetime, date

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_client import NotionClient
from notion_client.utils import (
    create_rich_text,
    create_page_parent,
    create_paragraph_block,
    create_heading_block,
    create_bulleted_list_item,
    create_callout_block,
    create_divider_block,
    create_icon,
)


def get_all_databases(client: NotionClient):
    """Get information about all databases in the workspace."""
    
    try:
        databases = client.search.search_databases()
        
        db_info = {}
        for db in databases:
            title = ""
            if db.title:
                title = "".join([t.plain_text for t in db.title])
            
            db_info[title] = {
                'id': db.id,
                'url': db.url,
                'icon': db.icon.emoji if db.icon and db.icon.type == 'emoji' else '📄'
            }
        
        return db_info
        
    except Exception as e:
        print(f"❌ Error gathering database info: {e}")
        return {}


def create_column_dashboard(client: NotionClient, parent_page_id: str, databases: dict):
    """Create a column-based dashboard."""
    
    print("🏠 Creating column-based dashboard...")
    
    # Page properties - Clean title without emoji
    page_properties = {
        "title": {
            "title": [create_rich_text("Protocol Manager Dashboard")]
        }
    }
    
    # Header blocks
    header_blocks = [
        create_heading_block("Protocol Manager Dashboard", level=1),
        create_paragraph_block(
            f"Productivity System • {date.today().strftime('%B %d, %Y')} • {len(databases)} Databases",
            color="gray"
        ),
        create_divider_block(),
    ]
    
    try:
        # Create the page first with header
        dashboard_page = client.pages.create(
            parent=create_page_parent(parent_page_id),
            properties=page_properties,
            children=header_blocks,
            icon=create_icon("emoji", "🏠")
        )
        
        print(f"✅ Dashboard page created: {dashboard_page.id}")
        
        # Now add column layout
        # Split databases into two groups
        db_list = list(databases.items())
        mid_point = len(db_list) // 2
        
        left_dbs = db_list[:mid_point]
        right_dbs = db_list[mid_point:]
        
        # Create left column content
        left_column_blocks = [
            {
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [create_rich_text("📅 Schedule & Planning")],
                    "color": "blue"
                }
            }
        ]
        
        # Add left column databases
        for db_name, db_info in left_dbs:
            left_column_blocks.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        create_rich_text(f"{db_info['icon']} "),
                        {
                            "type": "text",
                            "text": {
                                "content": db_name,
                                "link": {"url": db_info['url']}
                            },
                            "annotations": {"bold": True},
                            "plain_text": db_name
                        }
                    ]
                }
            })
        
        # Create right column content
        right_column_blocks = [
            {
                "type": "heading_3", 
                "heading_3": {
                    "rich_text": [create_rich_text("🎯 Projects & Tracking")],
                    "color": "green"
                }
            }
        ]
        
        # Add right column databases
        for db_name, db_info in right_dbs:
            right_column_blocks.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        create_rich_text(f"{db_info['icon']} "),
                        {
                            "type": "text",
                            "text": {
                                "content": db_name,
                                "link": {"url": db_info['url']}
                            },
                            "annotations": {"bold": True},
                            "plain_text": db_name
                        }
                    ]
                }
            })
        
        # Create the column list block
        column_list_block = {
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "type": "column",
                        "column": {
                            "children": left_column_blocks
                        }
                    },
                    {
                        "type": "column", 
                        "column": {
                            "children": right_column_blocks
                        }
                    }
                ]
            }
        }
        
        # Add the column layout to the page
        result = client.blocks.append_children(dashboard_page.id, [column_list_block])
        print(f"✅ Added column layout")
        
        # Add footer blocks
        footer_blocks = [
            create_divider_block(),
            create_callout_block(
                f"⚡ Quick Actions: Plan day • Schedule blocks • Update tasks • Review progress",
                icon="🎯",
                color="yellow"
            ),
            create_paragraph_block(
                f"System Status: ✅ {len(databases)} databases active • Last updated: {datetime.now().strftime('%H:%M')}",
                color="gray",
                italic=True
            )
        ]
        
        client.blocks.append_children(dashboard_page.id, footer_blocks)
        print(f"✅ Added footer section")
        
        return dashboard_page
        
    except Exception as e:
        print(f"❌ Error creating column dashboard: {e}")
        return None


def main():
    """Main function to create the column dashboard."""
    
    # Connect to Notion
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print(f"\n📐 Creating Column-Based Dashboard")
    print("=" * 40)
    
    # Get all database information
    databases = get_all_databases(client)
    
    if not databases:
        print("❌ No databases found.")
        return
    
    print(f"📊 Found {len(databases)} databases")
    
    # Use Protocol Home as parent
    protocol_home_id = "2518f242-f6b7-80c6-ba3a-f6cae6f0809c"
    
    # Create the column dashboard
    dashboard_page = create_column_dashboard(client, protocol_home_id, databases)
    
    if dashboard_page:
        print(f"\n🎉 Column Dashboard Created!")
        print("=" * 35)
        print(f"🔗 **URL**: {dashboard_page.url}")
        print(f"\n✨ **Features**:")
        print("   📐 True column layout for landscape viewing")
        print("   🔗 Clean clickable database links")
        print("   🎨 Proper icon placement (no duplicates)")
        print("   📱 Optimized for wide screens")
        print("   ⚡ Compact and professional design")
        
        print(f"\n📋 **Layout**:")
        print("   📅 Left: Schedule & Planning databases")
        print("   🎯 Right: Projects & Tracking databases")
        print("   ⚡ Bottom: Quick actions and status")
        
        print(f"\n🚀 **Perfect for**:")
        print("   💻 Desktop/laptop landscape viewing")
        print("   📱 Tablet horizontal orientation")
        print("   🖥️ Wide monitor setups")
        print("   ⚡ Quick daily access to all systems")
        
    else:
        print("❌ Failed to create column dashboard")


if __name__ == "__main__":
    main()
