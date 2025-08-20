"""
Setup script for creating Notion databases for Protocol Home agents.

This script creates the required Goals, Todos, and Calendar databases with all necessary
properties and prints the database IDs for your .env file.
"""

import os
import sys
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Load environment variables
load_dotenv()

console = Console()

def get_notion_client():
    """Get configured Notion client."""
    try:
        from notion_client.client import NotionClient
        
        api_token = os.getenv('NOTION_API_TOKEN')
        if not api_token:
            console.print("❌ [red]NOTION_API_TOKEN not found in environment variables[/red]")
            console.print("Please set your Notion API token in a .env file")
            console.print("Example: NOTION_API_TOKEN=ntn_your_integration_token_here")
            sys.exit(1)
        
        if not api_token.startswith('ntn_'):
            console.print("❌ [red]Invalid Notion API token format[/red]")
            console.print("Token should start with 'ntn_'")
            sys.exit(1)
        
        return NotionClient(auth_token=api_token)
        
    except ImportError:
        console.print("❌ [red]notion_client not found[/red]")
        console.print("Please install with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error creating Notion client: {str(e)}[/red]")
        sys.exit(1)


def get_parent_page():
    """Get the parent page ID for creating databases."""
    parent_page_id = os.getenv('NOTION_PARENT_PAGE_ID')
    
    if not parent_page_id:
        console.print("\n📋 [yellow]Parent page required for database creation[/yellow]")
        console.print("Notion API requires a parent page to create databases.")
        console.print("\n💡 To get a page ID:")
        console.print("1. Open any page in Notion (or create a new one)")
        console.print("2. Copy the page URL")
        console.print("3. Extract the ID from the URL (the long string after the last /)")
        console.print("   Example: https://notion.so/workspace/Page-Title-abc123def456...")
        console.print("   The ID would be: abc123def456...")
        parent_page_id = console.input("\nEnter parent page ID: ").strip()
        
        if not parent_page_id:
            console.print("❌ [red]Parent page ID is required[/red]")
            return None
    
    return parent_page_id


def create_goals_database(notion_client, parent_page_id=None):
    """Create the Goals database with all required properties."""
    
    # Define the parent
    if parent_page_id:
        from notion_client.utils import create_page_parent
        parent = create_page_parent(parent_page_id)
    else:
        # For workspace creation, we actually need a page parent
        # Notion API requires a parent page for database creation
        console.print("❌ [red]Parent page ID required for database creation[/red]")
        console.print("Notion API doesn't support creating databases directly in workspace root")
        return None
    
    # Define properties for Goals database
    properties = {
        "Name": {
            "title": {}
        },
        "Description": {
            "rich_text": {}
        },
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
        "Progress": {
            "number": {
                "format": "percent"
            }
        },
        "Target Date": {
            "date": {}
        },
        "Archived": {
            "checkbox": {}
        }
    }
    
    try:
        database = notion_client.databases.create(
            parent=parent,
            title=[{"type": "text", "text": {"content": "🎯 Goals"}}],
            properties=properties
        )
        return database.id
        
    except Exception as e:
        console.print(f"❌ Error creating Goals database: {str(e)}")
        return None


def create_todos_database(notion_client, parent_page_id=None):
    """Create the Todos database with all required properties."""
    
    # Define the parent
    if parent_page_id:
        from notion_client.utils import create_page_parent
        parent = create_page_parent(parent_page_id)
    else:
        # For workspace creation, we actually need a page parent
        # Notion API requires a parent page for database creation
        console.print("❌ [red]Parent page ID required for database creation[/red]")
        console.print("Notion API doesn't support creating databases directly in workspace root")
        return None
    
    # Define properties for Todos database
    properties = {
        "Task": {
            "title": {}
        },
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
        "Due Date": {
            "date": {}
        },
        "Completed": {
            "checkbox": {}
        },
        "Time Estimate": {
            "number": {}
        },
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
    
    try:
        database = notion_client.databases.create(
            parent=parent,
            title=[{"type": "text", "text": {"content": "📋 Todos"}}],
            properties=properties
        )
        return database.id
        
    except Exception as e:
        console.print(f"❌ Error creating Todos database: {str(e)}")
        return None


def create_calendar_database(notion_client, parent_page_id=None):
    """Create the Calendar database with all required properties."""
    
    # Define the parent
    if parent_page_id:
        from notion_client.utils import create_page_parent
        parent = create_page_parent(parent_page_id)
    else:
        # For workspace creation, we actually need a page parent
        # Notion API requires a parent page for database creation
        console.print("❌ [red]Parent page ID required for database creation[/red]")
        console.print("Notion API doesn't support creating databases directly in workspace root")
        return None
    
    # Define properties for Calendar database
    properties = {
        "Event Title": {
            "title": {}
        },
        "Start Date & Time": {
            "date": {}
        },
        "End Date & Time": {
            "date": {}
        },
        "Event Type": {
            "select": {
                "options": [
                    {"name": "Meeting", "color": "blue"},
                    {"name": "Call", "color": "green"},
                    {"name": "Workshop", "color": "purple"},
                    {"name": "Event", "color": "pink"},
                    {"name": "Travel", "color": "orange"},
                    {"name": "Appointment", "color": "red"},
                    {"name": "Learning", "color": "yellow"},
                    {"name": "Work", "color": "gray"}
                ]
            }
        },
        "Location": {
            "rich_text": {}
        },
        "Meeting URL": {
            "url": {}
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "Confirmed", "color": "green"},
                    {"name": "Tentative", "color": "yellow"},
                    {"name": "Cancelled", "color": "red"},
                    {"name": "Rescheduled", "color": "orange"}
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "blue"}
                ]
            }
        },
        "Preparation Needed": {
            "checkbox": {}
        },
        "Notes": {
            "rich_text": {}
        },
        "Recurring": {
            "select": {
                "options": [
                    {"name": "Daily", "color": "blue"},
                    {"name": "Weekly", "color": "green"},
                    {"name": "Monthly", "color": "orange"},
                    {"name": "None", "color": "gray"}
                ]
            }
        }
    }
    
    try:
        database = notion_client.databases.create(
            parent=parent,
            title=[{"type": "text", "text": {"content": "📅 Calendar"}}],
            properties=properties
        )
        return database.id
        
    except Exception as e:
        console.print(f"❌ Error creating Calendar database: {str(e)}")
        return None


def add_database_relations(notion_client, goals_db_id, todos_db_id):
    """Add relation properties between Goals and Todos databases."""
    
    try:
        # Add relation property to Goals database
        notion_client.databases.update(
            database_id=goals_db_id,
            properties={
                "Related Todos": {
                    "relation": {
                        "database_id": todos_db_id,
                        "single_property": {}
                    }
                }
            }
        )
        
        # Add relation property to Todos database
        notion_client.databases.update(
            database_id=todos_db_id,
            properties={
                "Related Goals": {
                    "relation": {
                        "database_id": goals_db_id,
                        "single_property": {}
                    }
                },
                "Goal Progress Impact": {
                    "select": {
                        "options": [
                            {"name": "High", "color": "red"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "Low", "color": "green"}
                        ]
                    }
                },
                "Goal Milestone": {
                    "checkbox": {}
                },
                "Estimated Goal Contribution": {
                    "number": {
                        "format": "percent"
                    }
                }
            }
        )
        
        console.print("✅ [green]Database relations added successfully[/green]")
        return True
        
    except Exception as e:
        console.print(f"⚠️ [yellow]Warning: Could not add database relations: {str(e)}[/yellow]")
        return False


def add_sample_data(notion_client, goals_db_id, todos_db_id, calendar_db_id):
    """Add sample data to the newly created databases."""
    
    try:
        # Add sample goal
        notion_client.pages.create(
            parent={"type": "database_id", "database_id": goals_db_id},
            properties={
                "Name": {"title": [{"text": {"content": "Learn AI and Productivity Tools"}}]},
                "Description": {"rich_text": [{"text": {"content": "Master AI tools and productivity systems to enhance personal and professional effectiveness"}}]},
                "Status": {"select": {"name": "In Progress"}},
                "Priority": {"select": {"name": "High"}},
                "Category": {"select": {"name": "Learning"}},
                "Progress": {"number": 25},
                "Target Date": {"date": {"start": "2024-12-31"}}
            }
        )
        
        # Add sample todos
        todos = [
            {
                "Task": "Set up Protocol Home AI agents",
                "Status": "Done",
                "Priority": "High",
                "Project": "Learning",
                "Completed": True
            },
            {
                "Task": "Create first productivity goal",
                "Status": "Todo",
                "Priority": "Medium",
                "Project": "Personal",
                "Context": "@computer"
            },
            {
                "Task": "Review weekly productivity patterns",
                "Status": "Todo",
                "Priority": "Low",
                "Project": "Personal",
                "Context": "@home"
            }
        ]
        
        for todo in todos:
            properties = {}
            for key, value in todo.items():
                if key == "Task":
                    properties[key] = {"title": [{"text": {"content": value}}]}
                elif key == "Completed":
                    properties[key] = {"checkbox": value}
                elif key == "Time Estimate":
                    properties[key] = {"number": value}
                else:
                    properties[key] = {"select": {"name": value}}
            
            notion_client.pages.create(
                parent={"type": "database_id", "database_id": todos_db_id},
                properties=properties
            )
        
        # Add sample calendar events
        from datetime import datetime, timedelta
        today = datetime.now()
        
        calendar_events = [
            {
                "Event Title": "Team Weekly Standup",
                "Start Date & Time": (today + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0),
                "End Date & Time": (today + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0),
                "Event Type": "Meeting",
                "Status": "Confirmed",
                "Priority": "Medium",
                "Location": "Conference Room A",
                "Recurring": "Weekly",
                "Preparation Needed": False
            },
            {
                "Event Title": "Focus Time: Deep Work",
                "Start Date & Time": (today + timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0),
                "End Date & Time": (today + timedelta(days=2)).replace(hour=16, minute=0, second=0, microsecond=0),
                "Event Type": "Work",
                "Status": "Confirmed",
                "Priority": "High",
                "Location": "Home Office",
                "Recurring": "None",
                "Preparation Needed": True,
                "Notes": "Block out distraction-free time for important project work"
            },
            {
                "Event Title": "Learning Session: AI Tools",
                "Start Date & Time": (today + timedelta(days=7)).replace(hour=19, minute=0, second=0, microsecond=0),
                "End Date & Time": (today + timedelta(days=7)).replace(hour=20, minute=30, second=0, microsecond=0),
                "Event Type": "Learning",
                "Status": "Tentative",
                "Priority": "Medium",
                "Recurring": "Weekly",
                "Preparation Needed": True
            }
        ]
        
        for event in calendar_events:
            properties = {}
            for key, value in event.items():
                if key == "Event Title":
                    properties[key] = {"title": [{"text": {"content": value}}]}
                elif key in ["Start Date & Time", "End Date & Time"]:
                    properties[key] = {"date": {"start": value.isoformat()}}
                elif key == "Preparation Needed":
                    properties[key] = {"checkbox": value}
                elif key in ["Location", "Notes"]:
                    if value:
                        properties[key] = {"rich_text": [{"text": {"content": value}}]}
                else:
                    properties[key] = {"select": {"name": value}}
            
            notion_client.pages.create(
                parent={"type": "database_id", "database_id": calendar_db_id},
                properties=properties
            )
            
        console.print("✅ [green]Sample data added successfully[/green]")
        
    except Exception as e:
        console.print(f"⚠️ [yellow]Warning: Could not add sample data: {str(e)}[/yellow]")


def main():
    """Main setup function."""
    
    console.print(Panel.fit(
        "🏠 [bold blue]Protocol Home Database Setup[/bold blue]\n"
        "Creating Notion databases for your AI agents...",
        border_style="blue"
    ))
    
    # Get Notion client
    notion_client = get_notion_client()
    console.print("✅ [green]Notion client connected[/green]")
    
    # Get parent page
    parent_page_id = get_parent_page()
    if parent_page_id:
        console.print(f"📄 Using parent page: {parent_page_id}")
    else:
        console.print("🏠 Creating databases in workspace root")
    
    # Create databases with progress indication
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Create Goals database
        task1 = progress.add_task("Creating Goals database...", total=None)
        goals_db_id = create_goals_database(notion_client, parent_page_id)
        progress.stop_task(task1)
        
        if not goals_db_id:
            console.print("❌ [red]Failed to create Goals database[/red]")
            sys.exit(1)
        
        # Create Todos database
        task2 = progress.add_task("Creating Todos database...", total=None)
        todos_db_id = create_todos_database(notion_client, parent_page_id)
        progress.stop_task(task2)
        
        if not todos_db_id:
            console.print("❌ [red]Failed to create Todos database[/red]")
            sys.exit(1)
        
        # Create Calendar database
        task3 = progress.add_task("Creating Calendar database...", total=None)
        calendar_db_id = create_calendar_database(notion_client, parent_page_id)
        progress.stop_task(task3)
        
        if not calendar_db_id:
            console.print("❌ [red]Failed to create Calendar database[/red]")
            sys.exit(1)
        
        # Add database relations
        task4 = progress.add_task("Adding database relations...", total=None)
        relations_added = add_database_relations(notion_client, goals_db_id, todos_db_id)
        progress.stop_task(task4)
        
        # Add sample data
        task5 = progress.add_task("Adding sample data...", total=None)
        add_sample_data(notion_client, goals_db_id, todos_db_id, calendar_db_id)
        progress.stop_task(task5)
    
    # Display results
    console.print("\n🎉 [bold green]Databases created successfully![/bold green]\n")
    
    # Create results table
    table = Table(title="📊 Database Information")
    table.add_column("Database", style="cyan")
    table.add_column("ID", style="green")
    table.add_column("URL", style="blue")
    table.add_column("Features", style="yellow")
    
    goals_url = f"https://notion.so/{goals_db_id.replace('-', '')}"
    todos_url = f"https://notion.so/{todos_db_id.replace('-', '')}"
    calendar_url = f"https://notion.so/{calendar_db_id.replace('-', '')}"
    
    table.add_row("🎯 Goals", goals_db_id, goals_url, "✅ Related Todos relation")
    table.add_row("📋 Todos", todos_db_id, todos_url, "✅ Related Goals + Goal tracking")
    table.add_row("📅 Calendar", calendar_db_id, calendar_url, "✅ Event management")
    
    console.print(table)
    
    # Generate .env content
    env_content = f"""
# Add these lines to your .env file:
NOTION_GOALS_DATABASE_ID={goals_db_id}
NOTION_TODOS_DATABASE_ID={todos_db_id}
NOTION_CALENDAR_DATABASE_ID={calendar_db_id}

# 🎉 Your databases now include:
# - Goals ↔ Todos relations for workflow management
# - Goal progress tracking properties
# - Enhanced todo organization features
"""
    
    console.print(Panel(
        env_content.strip(),
        title="📝 Environment Variables",
        border_style="green"
    ))
    
    # Save to file option
    save_choice = console.input("\nSave these IDs to a file? [Y/n]: ").strip().lower()
    if save_choice in ['', 'y', 'yes']:
        with open('database_ids.txt', 'w') as f:
            f.write(f"NOTION_GOALS_DATABASE_ID={goals_db_id}\n")
            f.write(f"NOTION_TODOS_DATABASE_ID={todos_db_id}\n")
            f.write(f"NOTION_CALENDAR_DATABASE_ID={calendar_db_id}\n")
        console.print("✅ [green]Database IDs saved to database_ids.txt[/green]")
    
    console.print("\n💡 [bold yellow]Next steps:[/bold yellow]")
    console.print("1. Add the database IDs to your .env file")
    console.print("2. Test your setup: python -m cli.main status")
    console.print("3. Start using your agents: python -m cli.main chat")
    console.print("4. View your databases in Notion using the URLs above")
    console.print("5. The databases now have relation properties linking Goals and Todos!")
    console.print("6. Use 'Related Goals' in Todos and 'Related Todos' in Goals to create links")


if __name__ == "__main__":
    main()
