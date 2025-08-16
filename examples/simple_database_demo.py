"""
Simple demonstration of creating and using a tracking database.
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
    create_select_option,
    create_icon,
)


def create_simple_task_tracker(client: NotionClient, parent_page_id: str):
    """Create a simple task tracking database."""
    
    print("Creating Simple Task Tracker...")
    
    # Database title and description
    title = [create_rich_text("✅ Task Tracker")]
    description = [create_rich_text("Simple database to track your daily tasks")]
    
    # Define the database properties (columns)
    properties = {
        # Title column (required)
        "Task": {
            "title": {}
        },
        
        # Status dropdown
        "Status": {
            "select": {
                "options": [
                    create_select_option("📝 To Do", "red"),
                    create_select_option("🔄 In Progress", "yellow"),
                    create_select_option("✅ Done", "green")
                ]
            }
        },
        
        # Due date
        "Due Date": {
            "date": {}
        },
        
        # Priority
        "Priority": {
            "select": {
                "options": [
                    create_select_option("🔥 High", "red"),
                    create_select_option("⚡ Medium", "yellow"),
                    create_select_option("💧 Low", "blue")
                ]
            }
        },
        
        # Notes
        "Notes": {
            "rich_text": {}
        }
    }
    
    # Create the database
    database = client.databases.create(
        parent=create_page_parent(parent_page_id),
        title=title,
        description=description,
        properties=properties,
        icon=create_icon("emoji", "✅")
    )
    
    print(f"✅ Database created!")
    print(f"   ID: {database.id}")
    print(f"   URL: {database.url}")
    
    return database


def add_sample_tasks(client: NotionClient, database_id: str):
    """Add some sample tasks to the database."""
    
    print(f"\n📝 Adding sample tasks...")
    
    sample_tasks = [
        {
            "Task": {"title": [create_rich_text("Complete Notion client project")]},
            "Status": {"select": create_select_option("✅ Done", "green")},
            "Priority": {"select": create_select_option("🔥 High", "red")},
            "Due Date": {"date": {"start": date.today().isoformat()}},
            "Notes": {"rich_text": [create_rich_text("Successfully built a complete Python client!")]}
        },
        {
            "Task": {"title": [create_rich_text("Write documentation")]},
            "Status": {"select": create_select_option("🔄 In Progress", "yellow")},
            "Priority": {"select": create_select_option("⚡ Medium", "yellow")},
            "Notes": {"rich_text": [create_rich_text("Need to add more examples and tutorials")]}
        },
        {
            "Task": {"title": [create_rich_text("Plan next project")]},
            "Status": {"select": create_select_option("📝 To Do", "red")},
            "Priority": {"select": create_select_option("💧 Low", "blue")},
            "Notes": {"rich_text": [create_rich_text("Brainstorm ideas for the next automation project")]}
        }
    ]
    
    created_tasks = []
    for i, task_data in enumerate(sample_tasks, 1):
        try:
            task = client.pages.create(
                parent={"type": "database_id", "database_id": database_id},
                properties=task_data
            )
            task_title = task_data["Task"]["title"][0]["text"]["content"]
            print(f"   ✅ Added: {task_title}")
            created_tasks.append(task)
        except Exception as e:
            print(f"   ❌ Error adding task {i}: {e}")
    
    return created_tasks


def query_database_examples(client: NotionClient, database_id: str):
    """Show examples of querying the database."""
    
    print(f"\n📊 Querying the database...")
    
    # Query 1: Get all tasks
    print("\n1. All tasks:")
    all_tasks = client.databases.query_all(database_id)
    for task in all_tasks:
        title = ""
        if task.properties.get("Task") and task.properties["Task"].get("title"):
            title = "".join([t.get("plain_text", "") for t in task.properties["Task"]["title"]])
        
        status = "No Status"
        if task.properties.get("Status") and task.properties["Status"].get("select"):
            status = task.properties["Status"]["select"].get("name", "No Status")
        
        print(f"   • {title} - {status}")
    
    # Query 2: Get only completed tasks
    print("\n2. Completed tasks:")
    try:
        completed_tasks = client.databases.query_all(
            database_id,
            filter_criteria={
                "property": "Status",
                "select": {"equals": "✅ Done"}
            }
        )
        
        if completed_tasks:
            for task in completed_tasks:
                title = ""
                if task.properties.get("Task") and task.properties["Task"].get("title"):
                    title = "".join([t.get("plain_text", "") for t in task.properties["Task"]["title"]])
                print(f"   ✅ {title}")
        else:
            print("   No completed tasks found")
            
    except Exception as e:
        print(f"   ❌ Error querying completed tasks: {e}")
    
    # Query 3: Get high priority tasks
    print("\n3. High priority tasks:")
    try:
        high_priority_tasks = client.databases.query_all(
            database_id,
            filter_criteria={
                "property": "Priority",
                "select": {"equals": "🔥 High"}
            }
        )
        
        if high_priority_tasks:
            for task in high_priority_tasks:
                title = ""
                if task.properties.get("Task") and task.properties["Task"].get("title"):
                    title = "".join([t.get("plain_text", "") for t in task.properties["Task"]["title"]])
                print(f"   🔥 {title}")
        else:
            print("   No high priority tasks found")
            
    except Exception as e:
        print(f"   ❌ Error querying high priority tasks: {e}")


def main():
    """Main demonstration function."""
    
    # Connect to Notion
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Use Protocol Home as parent
    protocol_home_id = "2518f242-f6b7-80c6-ba3a-f6cae6f0809c"
    
    print(f"\n🗃️ Creating a simple task tracking database...")
    
    # Create the database
    database = create_simple_task_tracker(client, protocol_home_id)
    
    # Add sample data
    tasks = add_sample_tasks(client, database.id)
    
    # Show query examples
    query_database_examples(client, database.id)
    
    print(f"\n🎉 Complete! Your task tracker is ready to use.")
    print(f"\n🔗 Database URL: {database.url}")
    print(f"\n💡 You can now:")
    print("   • Add more tasks through Notion UI or API")
    print("   • Filter and sort tasks")
    print("   • Update task status and properties")
    print("   • Create views and templates")
    print("   • Build automation workflows")


if __name__ == "__main__":
    main()
