"""
Create a comprehensive main dashboard page that combines all project databases and functionality.

This script creates a central hub page with:
- Overview of all databases
- Quick action buttons
- Recent activity summary
- Key metrics and insights
- Navigation to all subsystems
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add path for imports
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
    create_bookmark_block,
)


def get_all_databases(client: NotionClient):
    """Get information about all databases in the workspace."""
    
    print("📊 Gathering database information...")
    
    try:
        databases = client.search.search_databases()
        
        db_info = {}
        for db in databases:
            title = ""
            if db.title:
                title = "".join([t.plain_text for t in db.title])
            
            # Categorize databases
            if any(keyword in title.lower() for keyword in ['project', 'tracker']):
                category = 'productivity'
            elif any(keyword in title.lower() for keyword in ['calendar', 'event', 'time', 'todo', 'task', 'planning']):
                category = 'calendar'
            elif any(keyword in title.lower() for keyword in ['habit', 'expense', 'contact']):
                category = 'tracking'
            else:
                category = 'other'
            
            db_info[title] = {
                'id': db.id,
                'url': db.url,
                'category': category,
                'icon': db.icon.emoji if db.icon and db.icon.type == 'emoji' else '📄'
            }
        
        return db_info
        
    except Exception as e:
        print(f"❌ Error gathering database info: {e}")
        return {}


def create_dashboard_content(client: NotionClient, databases: dict):
    """Create the content blocks for the main dashboard."""
    
    # Header section
    content_blocks = [
        create_heading_block("🏠 Protocol Manager Dashboard", level=1),
        create_paragraph_block(
            f"Welcome to your comprehensive productivity system! Last updated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            italic=True,
            color="gray"
        ),
        
        create_divider_block(),
        
        # Quick Stats Section
        create_heading_block("📊 Quick Overview", level=2),
        create_callout_block(
            f"🗃️ Total Databases: {len(databases)} | 📅 Today: {date.today().strftime('%A, %B %d, %Y')}",
            icon="📊",
            color="blue"
        ),
    ]
    
    # Calendar & Time Management Section
    calendar_dbs = {k: v for k, v in databases.items() if v['category'] == 'calendar'}
    if calendar_dbs:
        content_blocks.extend([
            create_divider_block(),
            create_heading_block("📅 Calendar & Time Management", level=2),
            create_paragraph_block("Manage your schedule, time blocks, and daily planning"),
        ])
        
        for db_name, db_info in calendar_dbs.items():
            content_blocks.append(
                create_bulleted_list_item(f"{db_info['icon']} **{db_name}** - [Open Database]({db_info['url']})")
            )
        
        content_blocks.extend([
            create_callout_block(
                "💡 Quick Actions: Schedule a meeting • Plan time blocks • Add daily goals • Review weekly progress",
                icon="⚡",
                color="yellow"
            )
        ])
    
    # Productivity & Projects Section
    productivity_dbs = {k: v for k, v in databases.items() if v['category'] == 'productivity'}
    if productivity_dbs:
        content_blocks.extend([
            create_divider_block(),
            create_heading_block("🎯 Projects & Productivity", level=2),
            create_paragraph_block("Track projects, tasks, and productivity metrics"),
        ])
        
        for db_name, db_info in productivity_dbs.items():
            content_blocks.append(
                create_bulleted_list_item(f"{db_info['icon']} **{db_name}** - [Open Database]({db_info['url']})")
            )
        
        content_blocks.extend([
            create_callout_block(
                "🚀 Quick Actions: Create new project • Add urgent task • Update project status • Review completed work",
                icon="🎯",
                color="green"
            )
        ])
    
    # Personal Tracking Section
    tracking_dbs = {k: v for k, v in databases.items() if v['category'] == 'tracking'}
    if tracking_dbs:
        content_blocks.extend([
            create_divider_block(),
            create_heading_block("📈 Personal Tracking", level=2),
            create_paragraph_block("Monitor habits, expenses, and personal connections"),
        ])
        
        for db_name, db_info in tracking_dbs.items():
            content_blocks.append(
                create_bulleted_list_item(f"{db_info['icon']} **{db_name}** - [Open Database]({db_info['url']})")
            )
        
        content_blocks.extend([
            create_callout_block(
                "📊 Quick Actions: Log daily habits • Record expenses • Add new contacts • Review monthly progress",
                icon="📈",
                color="purple"
            )
        ])
    
    # System Information Section
    content_blocks.extend([
        create_divider_block(),
        create_heading_block("🔧 System Information", level=2),
        create_paragraph_block("Technical details and automation capabilities"),
        
        create_bulleted_list_item("**API Client**: Notion Python Client v0.1.0"),
        create_bulleted_list_item("**Total Databases**: " + str(len(databases))),
        create_bulleted_list_item("**Authentication**: Integration Token"),
        create_bulleted_list_item("**Rate Limiting**: 3 requests/second with automatic retry"),
        create_bulleted_list_item("**Error Handling**: Comprehensive exception management"),
        
        create_callout_block(
            "🤖 This system supports full automation via Python scripts. You can create, update, and query all data programmatically!",
            icon="⚙️",
            color="gray"
        )
    ])
    
    # Quick Start Guide
    content_blocks.extend([
        create_divider_block(),
        create_heading_block("🚀 Quick Start Guide", level=2),
        
        create_heading_block("Daily Workflow", level=3),
        create_numbered_list_item("Check **Daily Planning** for today's priorities"),
        create_numbered_list_item("Review **Calendar Events** for upcoming meetings"),
        create_numbered_list_item("Update **Time Blocks** for focused work sessions"),
        create_numbered_list_item("Process **Todos & Tasks** by priority and energy level"),
        create_numbered_list_item("Log progress in **Habit Tracker** and other systems"),
        
        create_heading_block("Weekly Review", level=3),
        create_numbered_list_item("Review completed projects and tasks"),
        create_numbered_list_item("Analyze time blocking effectiveness"),
        create_numbered_list_item("Update long-term project status"),
        create_numbered_list_item("Plan next week's priorities and time blocks"),
        
        create_heading_block("Monthly Planning", level=3),
        create_numbered_list_item("Review habit consistency and trends"),
        create_numbered_list_item("Analyze expense patterns and budget"),
        create_numbered_list_item("Update contact relationships and networking"),
        create_numbered_list_item("Set goals for the upcoming month"),
    ])
    
    # Automation Examples
    content_blocks.extend([
        create_divider_block(),
        create_heading_block("🤖 Automation Examples", level=2),
        create_paragraph_block("You can automate your workflow using the Python client:"),
        
        create_code_block(
            '''# Daily automation example
from notion_client import NotionClient
from datetime import date

client = NotionClient.from_env()

# Get today's tasks
today_tasks = client.databases.query_all(
    database_id="todos_db_id",
    filter_criteria={
        "property": "Due Date",
        "date": {"equals": date.today().isoformat()}
    }
)

# Create daily planning entry
daily_plan = client.pages.create(
    parent={"type": "database_id", "database_id": "daily_planning_db_id"},
    properties={
        "Date": {"title": [{"type": "text", "text": {"content": date.today().isoformat()}}]},
        "Top 3 Priorities": {"rich_text": [{"type": "text", "text": {"content": "Generated from urgent tasks"}}]}
    }
)''',
            language="python"
        ),
        
        create_callout_block(
            "💻 See the examples/ directory for complete automation scripts and usage patterns!",
            icon="💡",
            color="blue"
        )
    ])
    
    # Footer
    content_blocks.extend([
        create_divider_block(),
        create_quote_block(
            "Productivity is not about doing more things—it's about doing the right things efficiently. "
            "This system helps you focus on what matters most."
        ),
        create_paragraph_block(
            f"Dashboard created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"System Version: 1.0 | "
            f"Databases: {len(databases)}",
            color="gray",
            italic=True
        )
    ])
    
    return content_blocks


def create_main_dashboard(client: NotionClient, parent_page_id: str, databases: dict):
    """Create the main dashboard page."""
    
    print("🏠 Creating main dashboard page...")
    
    # Page properties
    page_properties = {
        "title": {
            "title": [create_rich_text("🏠 Protocol Manager - Main Dashboard")]
        }
    }
    
    # Create dashboard content
    dashboard_blocks = create_dashboard_content(client, databases)
    
    try:
        # Create the main dashboard page
        dashboard_page = client.pages.create(
            parent=create_page_parent(parent_page_id),
            properties=page_properties,
            children=dashboard_blocks
        )
        
        print(f"✅ Main dashboard created!")
        print(f"   ID: {dashboard_page.id}")
        print(f"   URL: {dashboard_page.url}")
        
        return dashboard_page
        
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return None


def add_quick_access_section(client: NotionClient, dashboard_page_id: str, databases: dict):
    """Add a quick access section with common actions."""
    
    print("⚡ Adding quick access section...")
    
    quick_access_blocks = [
        create_divider_block(),
        create_heading_block("⚡ Quick Access Links", level=2),
        create_paragraph_block("Direct links to common actions and views"),
        
        create_heading_block("📅 Today's Focus", level=3),
        create_bulleted_list_item("🌅 **Morning Planning** - Set daily priorities and energy levels"),
        create_bulleted_list_item("⏰ **Time Blocking** - Schedule focused work sessions"),
        create_bulleted_list_item("✅ **Active Tasks** - Work on high-priority items"),
        create_bulleted_list_item("🌙 **Evening Review** - Reflect on progress and plan tomorrow"),
        
        create_heading_block("📊 Weekly Reviews", level=3),
        create_bulleted_list_item("📈 **Productivity Metrics** - Analyze time blocking effectiveness"),
        create_bulleted_list_item("🎯 **Goal Progress** - Review project and habit advancement"),
        create_bulleted_list_item("💰 **Financial Review** - Check expenses and budget status"),
        create_bulleted_list_item("🔄 **System Optimization** - Improve workflows and processes"),
        
        create_callout_block(
            "🎯 Pro Tip: Bookmark this dashboard page and visit it daily to stay organized and focused!",
            icon="💡",
            color="yellow"
        )
    ]
    
    try:
        result = client.blocks.append_children(dashboard_page_id, quick_access_blocks)
        print(f"✅ Added quick access section with {len(quick_access_blocks)} blocks")
        return True
        
    except Exception as e:
        print(f"❌ Error adding quick access section: {e}")
        return False


def create_system_health_check(client: NotionClient):
    """Perform a system health check and return status information."""
    
    print("🔍 Performing system health check...")
    
    health_status = {
        'connection': False,
        'databases_count': 0,
        'recent_activity': False,
        'errors': []
    }
    
    try:
        # Test API connection
        workspace_info = client.get_workspace_info()
        health_status['connection'] = workspace_info.get('connection_status') == 'connected'
        
        # Count databases
        databases = client.search.search_databases()
        health_status['databases_count'] = len(databases)
        
        # Check for recent activity (simplified check)
        if databases:
            health_status['recent_activity'] = True
        
        print(f"   ✅ Connection: {'Healthy' if health_status['connection'] else 'Failed'}")
        print(f"   📊 Databases: {health_status['databases_count']}")
        print(f"   🔄 Activity: {'Recent' if health_status['recent_activity'] else 'None'}")
        
    except Exception as e:
        health_status['errors'].append(str(e))
        print(f"   ❌ Health check error: {e}")
    
    return health_status


def main():
    """Main function to create the comprehensive dashboard."""
    
    # Connect to Notion
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print(f"\n🏠 Creating Protocol Manager Main Dashboard")
    print("=" * 60)
    
    # Get all database information
    databases = get_all_databases(client)
    
    if not databases:
        print("❌ No databases found. Please create some databases first.")
        return
    
    print(f"📊 Found {len(databases)} databases to include in dashboard")
    
    # Use Protocol Home as parent
    protocol_home_id = "2518f242-f6b7-80c6-ba3a-f6cae6f0809c"
    
    # Perform system health check
    health_status = create_system_health_check(client)
    
    # Create the main dashboard
    dashboard_page = create_main_dashboard(client, protocol_home_id, databases)
    
    if dashboard_page:
        # Add quick access section
        add_quick_access_section(client, dashboard_page.id, databases)
        
        print(f"\n🎉 Protocol Manager Dashboard Created Successfully!")
        print("=" * 60)
        print(f"🔗 **Dashboard URL**: {dashboard_page.url}")
        print(f"\n📊 **System Summary**:")
        print(f"   • Total Databases: {len(databases)}")
        print(f"   • Connection Status: {'✅ Healthy' if health_status['connection'] else '❌ Failed'}")
        print(f"   • Categories: Calendar, Productivity, Tracking")
        
        print(f"\n🗃️ **Included Databases**:")
        for db_name, db_info in databases.items():
            print(f"   {db_info['icon']} {db_name} ({db_info['category']})")
        
        print(f"\n💡 **What You Can Do Now**:")
        print("   📌 Bookmark the dashboard page as your daily starting point")
        print("   🔄 Use it to navigate between all your productivity systems")
        print("   📊 Monitor your progress and system health")
        print("   ⚡ Access quick actions and common workflows")
        print("   🤖 Run automation scripts from the examples provided")
        
        print(f"\n🚀 **Next Steps**:")
        print("   1. Customize the dashboard content for your workflow")
        print("   2. Create daily/weekly review processes")
        print("   3. Set up automation scripts for routine tasks")
        print("   4. Build custom views and filters in each database")
        print("   5. Integrate with other tools and services")
        
    else:
        print("❌ Failed to create dashboard. Check the error messages above.")


if __name__ == "__main__":
    main()
