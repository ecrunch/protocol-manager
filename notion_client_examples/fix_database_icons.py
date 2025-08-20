"""
Fix duplicate icons in databases by updating database properties.
"""

import sys
import os

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_client import NotionClient
from notion_client.utils import create_rich_text


def list_current_databases(client: NotionClient):
    """List current databases and their icons."""
    
    print("🔍 Checking current databases...")
    
    # Search for databases in the workspace
    try:
        databases = client.search.search_databases()
        
        if not databases:
            print("No databases found")
            return []
        
        print(f"\nFound {len(databases)} databases:")
        print("-" * 60)
        
        db_info = []
        for i, db in enumerate(databases, 1):
            # Get database title
            title = ""
            if db.title:
                title = "".join([t.plain_text for t in db.title])
            
            # Check icon
            icon_info = "No icon"
            if db.icon:
                if db.icon.type == "emoji":
                    icon_info = f"Emoji: {db.icon.emoji}"
                elif db.icon.type == "external":
                    icon_info = f"External: {db.icon.external.get('url', 'N/A')}"
                elif db.icon.type == "file":
                    icon_info = f"File: {db.icon.file.get('url', 'N/A')}"
            
            print(f"{i:2d}. {title}")
            print(f"    ID: {db.id}")
            print(f"    Icon: {icon_info}")
            print(f"    URL: {db.url}")
            print()
            
            db_info.append({
                'title': title,
                'id': db.id,
                'icon': db.icon,
                'url': db.url
            })
        
        return db_info
        
    except Exception as e:
        print(f"❌ Error listing databases: {e}")
        return []


def fix_database_icons(client: NotionClient, database_info: list):
    """Remove emoji icons from database titles and clean up formatting."""
    
    print(f"\n🔧 Fixing database icons...")
    
    # Define clean titles without emojis
    clean_titles = {
        "📋 Project Tracker": "Project Tracker",
        "🎯 Habit Tracker": "Habit Tracker", 
        "💰 Expense Tracker": "Expense Tracker",
        "👥 Contacts": "Contacts",
        "✅ Task Tracker": "Task Tracker",
        "📅 Calendar Events": "Calendar Events",
        "⏰ Time Blocks": "Time Blocks",
        "✅ Todos & Tasks": "Todos & Tasks",
        "📋 Daily Planning": "Daily Planning"
    }
    
    # Define appropriate emojis for database icons
    database_icons = {
        "Project Tracker": "📋",
        "Habit Tracker": "🎯",
        "Expense Tracker": "💰",
        "Contacts": "👥",
        "Task Tracker": "✅",
        "Calendar Events": "📅",
        "Time Blocks": "⏰",
        "Todos & Tasks": "📝",
        "Daily Planning": "📋"
    }
    
    updated_count = 0
    
    for db_info in database_info:
        current_title = db_info['title']
        
        # Determine clean title
        clean_title = clean_titles.get(current_title, current_title)
        
        # Remove any emoji from the beginning of the title
        if clean_title.startswith(('📋', '🎯', '💰', '👥', '✅', '📅', '⏰', '📝')):
            # Find where the emoji ends and text begins
            for i, char in enumerate(clean_title):
                if char.isalpha() or char.isdigit():
                    clean_title = clean_title[i:].strip()
                    break
        
        # Get appropriate icon
        icon_emoji = database_icons.get(clean_title, "📋")
        
        # Update the database if needed
        needs_update = False
        update_data = {}
        
        # Check if title needs cleaning
        if current_title != clean_title:
            update_data["title"] = [create_rich_text(clean_title)]
            needs_update = True
            print(f"   📝 Updating title: '{current_title}' → '{clean_title}'")
        
        # Check if icon needs updating
        current_icon = db_info.get('icon')
        if not current_icon or current_icon.emoji != icon_emoji:
            update_data["icon"] = {
                "type": "emoji",
                "emoji": icon_emoji
            }
            needs_update = True
            print(f"   🎨 Setting icon: {icon_emoji}")
        
        if needs_update:
            try:
                client.databases.update(db_info['id'], **update_data)
                print(f"   ✅ Updated: {clean_title}")
                updated_count += 1
            except Exception as e:
                print(f"   ❌ Error updating {clean_title}: {e}")
        else:
            print(f"   ✨ Already clean: {clean_title}")
    
    return updated_count


def main():
    """Main function to fix database icons."""
    
    # Connect to Notion
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print("\n🎨 Database Icon Cleanup Tool")
    print("=" * 50)
    
    # List current databases
    database_info = list_current_databases(client)
    
    if not database_info:
        print("No databases found to update.")
        return
    
    # Ask for confirmation
    print(f"\n❓ Found {len(database_info)} databases. Fix icon duplication?")
    response = input("Continue? (y/n): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("Cancelled.")
        return
    
    # Fix the icons
    updated_count = fix_database_icons(client, database_info)
    
    print(f"\n🎉 Database cleanup complete!")
    print(f"   Updated: {updated_count} databases")
    print(f"\n💡 What was fixed:")
    print("   • Removed emoji duplicates from database titles")
    print("   • Set clean emoji icons on databases")
    print("   • Kept titles descriptive but clean")
    
    print(f"\n✨ Your databases should now show single, clean icons!")


if __name__ == "__main__":
    main()
