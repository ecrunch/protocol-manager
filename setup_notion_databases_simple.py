"""
Simple setup script for creating Notion databases using direct API calls.

This script creates the required Goals and Todos databases using the Notion API
directly and prints the database IDs for your .env file.
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database(headers, parent, title, properties):
    """Create a database in Notion."""
    url = "https://api.notion.com/v1/databases"
    payload = {
        "parent": parent,
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print(f"❌ Failed to create {title} database:")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def main():
    """Main setup function."""
    print("🏠 Protocol Home Database Setup")
    print("=" * 40)
    
    # Get API token
    notion_token = os.getenv('NOTION_API_TOKEN')
    if not notion_token:
        print("❌ NOTION_API_TOKEN not found in environment variables")
        print("Please add it to your .env file:")
        print("NOTION_API_TOKEN=ntn_your_integration_token_here")
        return
    
    if not notion_token.startswith('ntn_'):
        print("❌ Invalid Notion API token format")
        print("Token should start with 'ntn_'")
        return
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json", 
        "Notion-Version": "2022-06-28"
    }
    
    # Get parent page ID (optional)
    parent_page_id = os.getenv('NOTION_PARENT_PAGE_ID')
    
    if parent_page_id:
        parent = {"type": "page_id", "page_id": parent_page_id}
        print(f"📄 Creating databases under page: {parent_page_id}")
    else:
        print("🏠 Creating databases in workspace root")
        print("💡 To create under a specific page, set NOTION_PARENT_PAGE_ID in .env")
        # For workspace, we need to use a different approach
        # This is a limitation of the API - let's ask for a parent page
        print("\n⚠️  Note: Notion API requires a parent page for database creation")
        print("Please either:")
        print("1. Set NOTION_PARENT_PAGE_ID in your .env file, or")
        print("2. Use the main setup script: python setup_notion_databases.py")
        return
    
    # Define Goals database properties
    goals_properties = {
        "Name": {"title": {}},
        "Description": {"rich_text": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "Not Started", "color": "gray"},
                    {"name": "In Progress", "color": "yellow"},
                    {"name": "Completed", "color": "green"},
                    {"name": "On Hold", "color": "red"}
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "green"}
                ]
            }
        },
        "Category": {
            "select": {
                "options": [
                    {"name": "Personal", "color": "blue"},
                    {"name": "Professional", "color": "purple"},
                    {"name": "Health", "color": "green"},
                    {"name": "Learning", "color": "orange"},
                    {"name": "Financial", "color": "brown"}
                ]
            }
        },
        "Progress": {"number": {"format": "percent"}},
        "Target Date": {"date": {}},
        "Archived": {"checkbox": {}}
    }
    
    # Define Todos database properties
    todos_properties = {
        "Task": {"title": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "Todo", "color": "gray"},
                    {"name": "In Progress", "color": "yellow"},
                    {"name": "Done", "color": "green"}
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "Urgent", "color": "red"},
                    {"name": "High", "color": "orange"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "green"}
                ]
            }
        },
        "Project": {
            "select": {
                "options": [
                    {"name": "Personal", "color": "blue"},
                    {"name": "Work", "color": "purple"},
                    {"name": "Learning", "color": "orange"},
                    {"name": "Health", "color": "green"}
                ]
            }
        },
        "Due Date": {"date": {}},
        "Completed": {"checkbox": {}},
        "Time Estimate": {"number": {}},
        "Context": {
            "select": {
                "options": [
                    {"name": "@home", "color": "blue"},
                    {"name": "@office", "color": "purple"},
                    {"name": "@calls", "color": "orange"},
                    {"name": "@errands", "color": "green"},
                    {"name": "@computer", "color": "gray"}
                ]
            }
        }
    }
    
    # Create databases
    print("\n🎯 Creating Goals database...")
    goals_db_id = create_database(headers, parent, "🎯 Goals", goals_properties)
    
    if not goals_db_id:
        return
    
    print(f"✅ Goals database created: {goals_db_id}")
    
    print("\n📋 Creating Todos database...")
    todos_db_id = create_database(headers, parent, "📋 Todos", todos_properties)
    
    if not todos_db_id:
        return
    
    print(f"✅ Todos database created: {todos_db_id}")
    
    # Display results
    print("\n🎉 Success! Databases created successfully!")
    print("\n📊 Database Information:")
    print("-" * 50)
    print(f"Goals Database ID:  {goals_db_id}")
    print(f"Todos Database ID:  {todos_db_id}")
    print(f"Goals URL: https://notion.so/{goals_db_id.replace('-', '')}")
    print(f"Todos URL: https://notion.so/{todos_db_id.replace('-', '')}")
    
    # Generate .env content
    print("\n📝 Add these lines to your .env file:")
    print("-" * 40)
    print(f"NOTION_GOALS_DATABASE_ID={goals_db_id}")
    print(f"NOTION_TODOS_DATABASE_ID={todos_db_id}")
    
    # Save to file
    with open('database_ids.txt', 'w') as f:
        f.write(f"NOTION_GOALS_DATABASE_ID={goals_db_id}\n")
        f.write(f"NOTION_TODOS_DATABASE_ID={todos_db_id}\n")
    
    print(f"\n✅ Database IDs saved to database_ids.txt")
    
    print("\n💡 Next steps:")
    print("1. Add the database IDs to your .env file")
    print("2. Test your setup: python -m cli.main status")
    print("3. Start using your agents: python -m cli.main chat")

if __name__ == "__main__":
    main()
