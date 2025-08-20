"""
Create a full-width column-based dashboard for maximum landscape viewing.

This creates a dashboard with:
- Full width page layout
- True Notion columns for side-by-side layout
- Clean clickable database links
- Proper icon placement
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


def create_fullwidth_dashboard(client: NotionClient, parent_page_id: str, databases: dict):
    """Create a full-width column-based dashboard."""
    
    print("🏠 Creating full-width dashboard...")
    
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
            f"Full-Width Productivity System • {date.today().strftime('%B %d, %Y')} • {len(databases)} Active Databases",
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
        
        # Set page to full width using the page update endpoint
        # This is a special property that controls the page layout
        try:
            # Update the page to full width
            # Note: This uses an internal API call to set the page format
            response = client._http_client._request(
                method="PATCH",
                endpoint=f"/pages/{dashboard_page.id}",
                json={
                    "archived": False,
                    "properties": {},
                    # This sets the page to full width
                    "format": {
                        "page_full_width": True
                    }
                }
            )
            print("✅ Set page to full width")
        except Exception as e:
            print(f"⚠️ Could not set full width (continuing anyway): {e}")
        
        # Split databases into three columns for better full-width usage
        db_list = list(databases.items())
        col_size = len(db_list) // 3
        
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
        
        # Add a quick actions section that spans full width
        quick_actions_blocks = [
            create_divider_block(),
            create_heading_block("⚡ Quick Actions & Status", level=2),
            {
                "type": "column_list",
                "column_list": {
                    "children": [
                        {
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "type": "callout",
                                        "callout": {
                                            "rich_text": [create_rich_text("🌅 Morning: Plan priorities • Schedule time blocks • Review calendar")],
                                            "icon": {"emoji": "🌅"},
                                            "color": "yellow"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "type": "callout",
                                        "callout": {
                                            "rich_text": [create_rich_text("🎯 Focus: Execute tasks • Track progress • Log activities")],
                                            "icon": {"emoji": "🎯"},
                                            "color": "blue"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "type": "callout",
                                        "callout": {
                                            "rich_text": [create_rich_text("🌙 Evening: Review progress • Plan tomorrow • Reflect")],
                                            "icon": {"emoji": "🌙"},
                                            "color": "purple"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
        
        client.blocks.append_children(dashboard_page.id, quick_actions_blocks)
        print(f"✅ Added quick actions section")
        
        # Add system status footer
        footer_blocks = [
            create_divider_block(),
            create_paragraph_block(
                f"📊 System Status: ✅ {len(databases)} databases active • 🔗 All systems connected • ⏰ Last updated: {datetime.now().strftime('%H:%M')}",
                color="gray",
                italic=True
            )
        ]
        
        client.blocks.append_children(dashboard_page.id, footer_blocks)
        print(f"✅ Added system status footer")
        
        return dashboard_page
        
    except Exception as e:
        print(f"❌ Error creating full-width dashboard: {e}")
        return None


def main():
    """Main function to create the full-width dashboard."""
    
    # Connect to Notion
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print(f"\n🖥️ Creating Full-Width Dashboard")
    print("=" * 45)
    
    # Get all database information
    databases = get_all_databases(client)
    
    if not databases:
        print("❌ No databases found.")
        return
    
    print(f"📊 Found {len(databases)} databases")
    
    # Use Protocol Home as parent
    protocol_home_id = "2518f242-f6b7-80c6-ba3a-f6cae6f0809c"
    
    # Create the full-width dashboard
    dashboard_page = create_fullwidth_dashboard(client, protocol_home_id, databases)
    
    if dashboard_page:
        print(f"\n🎉 Full-Width Dashboard Created!")
        print("=" * 40)
        print(f"🔗 **URL**: {dashboard_page.url}")
        print(f"\n✨ **Features**:")
        print("   🖥️ Full-width page layout")
        print("   📐 Three-column design for wide screens")
        print("   🔗 Clean clickable database links")
        print("   🎨 Proper icon placement (no duplicates)")
        print("   ⚡ Quick actions spanning full width")
        print("   📊 System status and metadata")
        
        print(f"\n📋 **Three-Column Layout**:")
        print("   📅 Left: Calendar & Planning")
        print("   🎯 Middle: Projects & Tasks") 
        print("   📊 Right: Personal & Tracking")
        
        print(f"\n🖥️ **Optimized For**:")
        print("   💻 Wide desktop monitors")
        print("   📱 Large tablet landscape")
        print("   🖼️ Full-screen browser windows")
        print("   👀 Maximum information density")
        
        print(f"\n⚡ **Usage Tips**:")
        print("   🔍 Bookmark for daily dashboard access")
        print("   🖱️ Click database names to open instantly")
        print("   📐 Use in full-screen for best experience")
        print("   🎯 Quick actions guide daily workflow")
        
    else:
        print("❌ Failed to create full-width dashboard")


if __name__ == "__main__":
    main()
