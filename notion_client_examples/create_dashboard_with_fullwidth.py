"""
Create a full-width dashboard using the built-in client functionality.

This demonstrates the new set_page_full_width method in the NotionClient.
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


def create_dashboard_with_built_in_fullwidth(client: NotionClient, parent_page_id: str, databases: dict):
    """Create a dashboard and set it to full width using the built-in client method."""
    
    print("🏠 Creating dashboard with built-in full width support...")
    
    # Page properties - Clean title without emoji
    page_properties = {
        "title": {
            "title": [create_rich_text("Protocol Manager - Full Width Dashboard")]
        }
    }
    
    # Header blocks
    header_blocks = [
        create_heading_block("Protocol Manager Dashboard", level=1),
        create_paragraph_block(
            f"Full-Width Productivity System • {date.today().strftime('%B %d, %Y')} • {len(databases)} Active Databases",
            color="gray"
        ),
        create_divider_block(),
    ]
    
    try:
        # Create the page first
        dashboard_page = client.pages.create(
            parent=create_page_parent(parent_page_id),
            properties=page_properties,
            children=header_blocks,
            icon=create_icon("emoji", "🖥️")
        )
        
        print(f"✅ Dashboard page created: {dashboard_page.id}")
        
        # Now try to set it to full width using the new client method
        print("🖥️ Attempting to set page to full width...")
        full_width_success = client.set_page_full_width(dashboard_page.id, full_width=True)
        
        if full_width_success:
            print("✅ Successfully set page to full width!")
        else:
            print("⚠️ Could not set full width via API - manual setting required")
        
        # Split databases into three columns for better full-width usage
        db_list = list(databases.items())
        col_size = max(1, len(db_list) // 3)
        
        left_dbs = db_list[:col_size]
        middle_dbs = db_list[col_size:col_size*2]
        right_dbs = db_list[col_size*2:]
        
        # Create left column content
        left_column_blocks = [
            {
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [create_rich_text("📅 Calendar & Planning")],
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
        
        # Create middle column content
        middle_column_blocks = [
            {
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [create_rich_text("🎯 Projects & Tasks")],
                    "color": "green"
                }
            }
        ]
        
        # Add middle column databases
        for db_name, db_info in middle_dbs:
            middle_column_blocks.append({
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
                    "rich_text": [create_rich_text("📊 Personal & Tracking")],
                    "color": "purple"
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
        
        # Create the three-column list block
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
                            "children": middle_column_blocks
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
        print(f"✅ Added three-column layout")
        
        # Add quick actions and status
        footer_blocks = [
            create_divider_block(),
            create_callout_block(
                f"⚡ Quick Actions: Plan priorities • Schedule time blocks • Update tasks • Review progress",
                icon="🎯",
                color="yellow"
            ),
            create_callout_block(
                f"📊 System Status: ✅ {len(databases)} databases active • 🔗 All systems connected • Full Width: {'✅ Enabled' if full_width_success else '⚠️ Manual setting required'}",
                icon="📊",
                color="green" if full_width_success else "orange"
            ),
            create_paragraph_block(
                f"Dashboard created: {datetime.now().strftime('%Y-%m-%d %H:%M')} • Full-width support built-in",
                color="gray",
                italic=True
            )
        ]
        
        client.blocks.append_children(dashboard_page.id, footer_blocks)
        print(f"✅ Added footer with full width status")
        
        return dashboard_page, full_width_success
        
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return None, False


def main():
    """Main function to create the dashboard with built-in full width support."""
    
    # Connect to Notion
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print(f"\n🖥️ Creating Dashboard with Built-in Full Width Support")
    print("=" * 60)
    
    # Get all database information
    databases = get_all_databases(client)
    
    if not databases:
        print("❌ No databases found.")
        return
    
    print(f"📊 Found {len(databases)} databases")
    
    # Use Protocol Home as parent
    protocol_home_id = "2518f242-f6b7-80c6-ba3a-f6cae6f0809c"
    
    # Create the dashboard with built-in full width
    dashboard_page, full_width_success = create_dashboard_with_built_in_fullwidth(client, protocol_home_id, databases)
    
    if dashboard_page:
        print(f"\n🎉 Dashboard Created with Full Width Support!")
        print("=" * 50)
        print(f"🔗 **URL**: {dashboard_page.url}")
        
        print(f"\n✨ **Features**:")
        print("   🖥️ Built-in full width support")
        print("   📐 Three-column layout for wide screens")
        print("   🔗 Clean clickable database links")
        print("   🎨 Proper icon placement")
        print("   ⚡ Integrated full width setting")
        
        print(f"\n🖥️ **Full Width Status**:")
        if full_width_success:
            print("   ✅ Automatically set to full width")
            print("   🎯 Ready for maximum screen utilization")
            print("   📐 Three columns will display side-by-side")
        else:
            print("   ⚠️ Full width requires manual setting")
            print("   📋 In Notion, click '...' menu → 'Full width'")
            print("   🔧 API limitation - manual toggle needed")
        
        print(f"\n💡 **Client Enhancement**:")
        print("   🔧 Added set_page_full_width() method to NotionClient")
        print("   📄 Added set_full_width() method to PagesEndpoint")
        print("   ⚡ Graceful handling of API limitations")
        print("   🛠️ Ready for future Notion API updates")
        
        print(f"\n🚀 **Usage Example**:")
        print("   ```python")
        print("   client = NotionClient.from_env()")
        print(f"   client.set_page_full_width('{dashboard_page.id}')")
        print("   ```")
        
    else:
        print("❌ Failed to create dashboard")


if __name__ == "__main__":
    main()
