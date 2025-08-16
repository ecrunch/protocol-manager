"""
Examples of creating databases to track different things using the Notion Python client.

This script demonstrates how to create various tracking databases with different
property types and configurations.
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
    create_select_option,
    create_icon,
)


def create_project_tracker(client: NotionClient, parent_page_id: str):
    """Create a database to track projects."""
    
    print("Creating Project Tracker database...")
    
    # Database title
    title = [create_rich_text("📋 Project Tracker")]
    
    # Database description
    description = [create_rich_text("Track all your projects with tasks, deadlines, and progress")]
    
    # Define properties (columns)
    properties = {
        # Title property (required for all databases)
        "Project Name": {
            "title": {}
        },
        
        # Status with predefined options
        "Status": {
            "select": {
                "options": [
                    create_select_option("🟡 Planning", "yellow"),
                    create_select_option("🔵 In Progress", "blue"),
                    create_select_option("🟢 Completed", "green"),
                    create_select_option("🔴 On Hold", "red"),
                    create_select_option("⚫ Cancelled", "gray")
                ]
            }
        },
        
        # Priority levels
        "Priority": {
            "select": {
                "options": [
                    create_select_option("🔥 High", "red"),
                    create_select_option("⚡ Medium", "yellow"),
                    create_select_option("💧 Low", "green")
                ]
            }
        },
        
        # Due date
        "Due Date": {
            "date": {}
        },
        
        # Assigned person
        "Assigned To": {
            "people": {}
        },
        
        # Progress percentage
        "Progress": {
            "number": {
                "format": "percent"
            }
        },
        
        # Description/notes
        "Description": {
            "rich_text": {}
        },
        
        # Tags for categorization
        "Tags": {
            "multi_select": {
                "options": [
                    create_select_option("🏢 Work", "blue"),
                    create_select_option("🏠 Personal", "green"),
                    create_select_option("💻 Development", "purple"),
                    create_select_option("📚 Learning", "orange"),
                    create_select_option("🎯 Goal", "red")
                ]
            }
        },
        
        # URL for project links
        "Project URL": {
            "url": {}
        },
        
        # Budget/cost tracking
        "Budget": {
            "number": {
                "format": "dollar"
            }
        }
    }
    
    try:
        database = client.databases.create(
            parent=create_page_parent(parent_page_id),
            title=title,
            description=description,
            properties=properties,
            icon=create_icon("emoji", "📋")
        )
        
        print(f"✅ Project Tracker created!")
        print(f"   ID: {database.id}")
        print(f"   URL: {database.url}")
        
        return database
        
    except Exception as e:
        print(f"❌ Error creating Project Tracker: {e}")
        return None


def create_habit_tracker(client: NotionClient, parent_page_id: str):
    """Create a database to track daily habits."""
    
    print("\nCreating Habit Tracker database...")
    
    title = [create_rich_text("🎯 Habit Tracker")]
    description = [create_rich_text("Track your daily habits and build consistency")]
    
    properties = {
        "Habit": {
            "title": {}
        },
        
        "Date": {
            "date": {}
        },
        
        "Completed": {
            "checkbox": {}
        },
        
        "Category": {
            "select": {
                "options": [
                    create_select_option("💪 Health", "green"),
                    create_select_option("📚 Learning", "blue"),
                    create_select_option("💼 Work", "purple"),
                    create_select_option("🧘 Mindfulness", "orange"),
                    create_select_option("🎨 Creative", "pink")
                ]
            }
        },
        
        "Streak Count": {
            "number": {}
        },
        
        "Difficulty": {
            "select": {
                "options": [
                    create_select_option("😊 Easy", "green"),
                    create_select_option("😐 Medium", "yellow"),
                    create_select_option("😤 Hard", "red")
                ]
            }
        },
        
        "Notes": {
            "rich_text": {}
        },
        
        "Time Spent": {
            "number": {
                "format": "number"
            }
        }
    }
    
    try:
        database = client.databases.create(
            parent=create_page_parent(parent_page_id),
            title=title,
            description=description,
            properties=properties,
            icon=create_icon("emoji", "🎯")
        )
        
        print(f"✅ Habit Tracker created!")
        print(f"   ID: {database.id}")
        print(f"   URL: {database.url}")
        
        return database
        
    except Exception as e:
        print(f"❌ Error creating Habit Tracker: {e}")
        return None


def create_expense_tracker(client: NotionClient, parent_page_id: str):
    """Create a database to track expenses."""
    
    print("\nCreating Expense Tracker database...")
    
    title = [create_rich_text("💰 Expense Tracker")]
    description = [create_rich_text("Track your spending and manage your budget")]
    
    properties = {
        "Description": {
            "title": {}
        },
        
        "Amount": {
            "number": {
                "format": "dollar"
            }
        },
        
        "Date": {
            "date": {}
        },
        
        "Category": {
            "select": {
                "options": [
                    create_select_option("🍔 Food", "orange"),
                    create_select_option("🚗 Transportation", "blue"),
                    create_select_option("🏠 Housing", "green"),
                    create_select_option("🛍️ Shopping", "pink"),
                    create_select_option("🎬 Entertainment", "purple"),
                    create_select_option("⚕️ Healthcare", "red"),
                    create_select_option("📚 Education", "brown"),
                    create_select_option("💼 Business", "gray")
                ]
            }
        },
        
        "Payment Method": {
            "select": {
                "options": [
                    create_select_option("💳 Credit Card", "blue"),
                    create_select_option("💰 Cash", "green"),
                    create_select_option("🏦 Debit Card", "purple"),
                    create_select_option("📱 Digital Wallet", "orange")
                ]
            }
        },
        
        "Merchant": {
            "rich_text": {}
        },
        
        "Necessary": {
            "checkbox": {}
        },
        
        "Receipt": {
            "files": {}
        }
    }
    
    try:
        database = client.databases.create(
            parent=create_page_parent(parent_page_id),
            title=title,
            description=description,
            properties=properties,
            icon=create_icon("emoji", "💰")
        )
        
        print(f"✅ Expense Tracker created!")
        print(f"   ID: {database.id}")
        print(f"   URL: {database.url}")
        
        return database
        
    except Exception as e:
        print(f"❌ Error creating Expense Tracker: {e}")
        return None


def create_contact_database(client: NotionClient, parent_page_id: str):
    """Create a database to manage contacts."""
    
    print("\nCreating Contact Database...")
    
    title = [create_rich_text("👥 Contacts")]
    description = [create_rich_text("Manage your professional and personal contacts")]
    
    properties = {
        "Name": {
            "title": {}
        },
        
        "Email": {
            "email": {}
        },
        
        "Phone": {
            "phone_number": {}
        },
        
        "Company": {
            "rich_text": {}
        },
        
        "Position": {
            "rich_text": {}
        },
        
        "Relationship": {
            "select": {
                "options": [
                    create_select_option("👨‍💼 Colleague", "blue"),
                    create_select_option("👨‍💻 Client", "green"),
                    create_select_option("👨‍🎓 Mentor", "purple"),
                    create_select_option("👥 Friend", "yellow"),
                    create_select_option("👨‍👩‍👧‍👦 Family", "pink"),
                    create_select_option("🤝 Business Partner", "orange")
                ]
            }
        },
        
        "Last Contact": {
            "date": {}
        },
        
        "LinkedIn": {
            "url": {}
        },
        
        "Notes": {
            "rich_text": {}
        },
        
        "Birthday": {
            "date": {}
        }
    }
    
    try:
        database = client.databases.create(
            parent=create_page_parent(parent_page_id),
            title=title,
            description=description,
            properties=properties,
            icon=create_icon("emoji", "👥")
        )
        
        print(f"✅ Contact Database created!")
        print(f"   ID: {database.id}")
        print(f"   URL: {database.url}")
        
        return database
        
    except Exception as e:
        print(f"❌ Error creating Contact Database: {e}")
        return None


def add_sample_data(client: NotionClient, databases: dict):
    """Add some sample data to the created databases."""
    
    print("\n📝 Adding sample data...")
    
    # Add sample project
    if "project_tracker" in databases and databases["project_tracker"]:
        try:
            sample_project = client.pages.create(
                parent={"type": "database_id", "database_id": databases["project_tracker"].id},
                properties={
                    "Project Name": {"title": [create_rich_text("Build Notion Client")]},
                    "Status": {"select": create_select_option("🟢 Completed", "green")},
                    "Priority": {"select": create_select_option("🔥 High", "red")},
                    "Progress": {"number": 100},
                    "Description": {"rich_text": [create_rich_text("Complete Python client for Notion API")]},
                    "Tags": {"multi_select": [
                        create_select_option("💻 Development", "purple"),
                        create_select_option("🏢 Work", "blue")
                    ]}
                }
            )
            print(f"✅ Added sample project")
        except Exception as e:
            print(f"❌ Error adding sample project: {e}")
    
    # Add sample habit
    if "habit_tracker" in databases and databases["habit_tracker"]:
        try:
            from datetime import date
            sample_habit = client.pages.create(
                parent={"type": "database_id", "database_id": databases["habit_tracker"].id},
                properties={
                    "Habit": {"title": [create_rich_text("Daily Coding")]},
                    "Date": {"date": {"start": date.today().isoformat()}},
                    "Completed": {"checkbox": True},
                    "Category": {"select": create_select_option("📚 Learning", "blue")},
                    "Streak Count": {"number": 15},
                    "Difficulty": {"select": create_select_option("😐 Medium", "yellow")},
                    "Time Spent": {"number": 120}
                }
            )
            print(f"✅ Added sample habit")
        except Exception as e:
            print(f"❌ Error adding sample habit: {e}")


def main():
    """Main function to create tracking databases."""
    
    # Connect to Notion
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Use Protocol Home as parent (from previous examples)
    protocol_home_id = "2518f242-f6b7-80c6-ba3a-f6cae6f0809c"
    
    print(f"\n🗃️ Creating tracking databases under Protocol Home...")
    print("=" * 60)
    
    # Create different types of tracking databases
    databases = {}
    
    # Project Tracker
    databases["project_tracker"] = create_project_tracker(client, protocol_home_id)
    
    # Habit Tracker
    databases["habit_tracker"] = create_habit_tracker(client, protocol_home_id)
    
    # Expense Tracker
    databases["expense_tracker"] = create_expense_tracker(client, protocol_home_id)
    
    # Contact Database
    databases["contact_database"] = create_contact_database(client, protocol_home_id)
    
    # Add sample data
    add_sample_data(client, databases)
    
    print("\n" + "=" * 60)
    print("🎉 Database creation complete!")
    print("\n💡 What you can do now:")
    print("1. Visit the URLs above to see your new databases in Notion")
    print("2. Add more entries through the Notion UI or programmatically")
    print("3. Query and filter data using the client.databases.query() method")
    print("4. Create relationships between databases")
    print("5. Build custom workflows and automation")
    
    # Show some query examples
    print(f"\n📊 Example: Query your databases programmatically:")
    print(f"""
# Query completed projects
completed_projects = client.databases.query_all(
    database_id="{databases.get('project_tracker', {}).get('id', 'DATABASE_ID')}",
    filter_criteria={{
        "property": "Status",
        "select": {{"equals": "🟢 Completed"}}
    }}
)

# Query recent habits
from datetime import date, timedelta
recent_habits = client.databases.query_all(
    database_id="{databases.get('habit_tracker', {}).get('id', 'DATABASE_ID')}",
    filter_criteria={{
        "property": "Date",
        "date": {{"after": (date.today() - timedelta(days=7)).isoformat()}}
    }}
)
""")


if __name__ == "__main__":
    main()
