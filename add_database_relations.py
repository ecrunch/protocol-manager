"""
Add relation properties between Goals and Todos databases.

This script adds relation properties to connect todos with their associated goals,
enabling better workflow management and progress tracking.
"""

import os
import sys
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
            sys.exit(1)
        
        return NotionClient(auth_token=api_token)
        
    except ImportError:
        console.print("❌ [red]notion_client not found[/red]")
        console.print("Please install with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error creating Notion client: {str(e)}[/red]")
        sys.exit(1)


def get_database_ids():
    """Get database IDs from environment or database_ids.txt."""
    goals_id = os.getenv('NOTION_GOALS_DATABASE_ID')
    todos_id = os.getenv('NOTION_TODOS_DATABASE_ID')
    
    if not goals_id or not todos_id:
        # Try to read from database_ids.txt
        try:
            with open('database_ids.txt', 'r') as f:
                for line in f:
                    if 'NOTION_GOALS_DATABASE_ID=' in line:
                        goals_id = line.split('=')[1].strip()
                    elif 'NOTION_TODOS_DATABASE_ID=' in line:
                        todos_id = line.split('=')[1].strip()
        except FileNotFoundError:
            pass
    
    if not goals_id or not todos_id:
        console.print("❌ [red]Database IDs not found[/red]")
        console.print("Please set NOTION_GOALS_DATABASE_ID and NOTION_TODOS_DATABASE_ID in your .env file")
        console.print("Or ensure database_ids.txt exists with the correct IDs")
        sys.exit(1)
    
    return goals_id, todos_id


def add_relation_to_goals(notion_client, goals_db_id, todos_db_id):
    """Add 'Related Todos' relation property to Goals database."""
    
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
        
        console.print("✅ [green]Added 'Related Todos' relation to Goals database[/green]")
        return True
        
    except Exception as e:
        console.print(f"❌ [red]Error adding relation to Goals database: {str(e)}[/red]")
        return False


def add_relation_to_todos(notion_client, todos_db_id, goals_db_id):
    """Add 'Related Goals' relation property to Todos database."""
    
    try:
        # Add relation property to Todos database
        notion_client.databases.update(
            database_id=todos_db_id,
            properties={
                "Related Goals": {
                    "relation": {
                        "database_id": goals_db_id,
                        "single_property": {}
                    }
                }
            }
        )
        
        console.print("✅ [green]Added 'Related Goals' relation to Todos database[/green]")
        return True
        
    except Exception as e:
        console.print(f"❌ [red]Error adding relation to Todos database: {str(e)}[/red]")
        return False


def add_enhanced_properties(notion_client, todos_db_id):
    """Add additional properties to Todos database for better goal integration."""
    
    try:
        # Add properties that will help with goal management
        notion_client.databases.update(
            database_id=todos_db_id,
            properties={
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
        
        console.print("✅ [green]Added enhanced properties to Todos database[/green]")
        return True
        
    except Exception as e:
        console.print(f"⚠️ [yellow]Warning: Could not add enhanced properties: {str(e)}[/yellow]")
        return False


def create_sample_relations(notion_client, goals_db_id, todos_db_id):
    """Create sample relations between existing goals and todos."""
    
    try:
        # Get existing goals and todos
        goals_response = notion_client.databases.query(database_id=goals_db_id, page_size=10)
        todos_response = notion_client.client.databases.query(database_id=todos_db_id, page_size=10)
        
        if not goals_response.get('results') or not todos_response.get('results'):
            console.print("⚠️ [yellow]No existing goals or todos found to create sample relations[/yellow]")
            return
        
        # Create a sample relation (first goal to first todo)
        first_goal = goals_response['results'][0]
        first_todo = todos_response['results'][0]
        
        # Update the todo to relate to the goal
        notion_client.pages.update(
            page_id=first_todo['id'],
            properties={
                "Related Goals": {
                    "relation": [
                        {"id": first_goal['id']}
                    ]
                }
            }
        )
        
        console.print("✅ [green]Created sample relation between first goal and first todo[/green]")
        
    except Exception as e:
        console.print(f"⚠️ [yellow]Warning: Could not create sample relations: {str(e)}[/yellow]")


def main():
    """Main function to add relations between databases."""
    
    console.print(Panel.fit(
        "🔗 [bold blue]Adding Database Relations[/bold blue]\n"
        "Connecting Goals and Todos for better workflow management...",
        border_style="blue"
    ))
    
    # Get Notion client
    notion_client = get_notion_client()
    console.print("✅ [green]Notion client connected[/green]")
    
    # Get database IDs
    goals_db_id, todos_db_id = get_database_ids()
    console.print(f"🎯 Goals Database: {goals_db_id}")
    console.print(f"📋 Todos Database: {todos_db_id}")
    
    # Add relations with progress indication
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Add relation to Goals database
        task1 = progress.add_task("Adding relation to Goals database...", total=None)
        success1 = add_relation_to_goals(notion_client, goals_db_id, todos_db_id)
        progress.stop_task(task1)
        
        # Add relation to Todos database
        task2 = progress.add_task("Adding relation to Todos database...", total=None)
        success2 = add_relation_to_todos(notion_client, todos_db_id, goals_db_id)
        progress.stop_task(task2)
        
        # Add enhanced properties
        task3 = progress.add_task("Adding enhanced properties...", total=None)
        success3 = add_enhanced_properties(notion_client, todos_db_id)
        progress.stop_task(task3)
        
        # Create sample relations
        task4 = progress.add_task("Creating sample relations...", total=None)
        create_sample_relations(notion_client, goals_db_id, todos_db_id)
        progress.stop_task(task4)
    
    if success1 and success2:
        console.print("\n🎉 [bold green]Database relations added successfully![/bold green]\n")
        
        # Display results table
        table = Table(title="🔗 New Database Properties")
        table.add_column("Database", style="cyan")
        table.add_column("New Properties", style="green")
        table.add_column("Purpose", style="blue")
        
        table.add_row(
            "🎯 Goals",
            "Related Todos",
            "Link todos that contribute to this goal"
        )
        table.add_row(
            "📋 Todos",
            "Related Goals, Goal Progress Impact, Goal Milestone, Estimated Goal Contribution",
            "Link to goals and track impact on goal progress"
        )
        
        console.print(table)
        
        console.print("\n💡 [bold yellow]How to use the new relations:[/bold yellow]")
        console.print("1. **In Goals database**: Use 'Related Todos' to see all todos contributing to a goal")
        console.print("2. **In Todos database**: Use 'Related Goals' to link todos to specific goals")
        console.print("3. **Goal Progress Impact**: Rate how much a todo contributes to goal completion")
        console.print("4. **Goal Milestone**: Mark todos that represent significant progress milestones")
        console.print("5. **Estimated Goal Contribution**: Set percentage contribution to goal progress")
        
        console.print("\n🚀 [bold green]Next steps:[/bold green]")
        console.print("1. Open your databases in Notion")
        console.print("2. Start linking existing todos to goals")
        console.print("3. Use the new properties to track goal progress")
        console.print("4. Create views that show todos grouped by goals")
        
    else:
        console.print("\n❌ [red]Some operations failed. Check the errors above.[/red]")


if __name__ == "__main__":
    main()
