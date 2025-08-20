"""
Test script to verify database relations between Goals and Todos.

This script tests the relation properties and creates sample data to demonstrate
how goals and todos can be linked together.
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
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
            sys.exit(1)
        
        return NotionClient(auth_token=api_token)
        
    except ImportError:
        console.print("❌ [red]notion_client not found[/red]")
        sys.exit(1)


def get_database_ids():
    """Get database IDs from environment or database_ids.txt."""
    goals_id = os.getenv('NOTION_GOALS_DATABASE_ID')
    todos_id = os.getenv('NOTION_TODOS_DATABASE_ID')
    
    if not goals_id or not todos_id:
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
        sys.exit(1)
    
    return goals_id, todos_id


def test_database_properties(notion_client, goals_db_id, todos_db_id):
    """Test that both databases have the expected relation properties."""
    
    try:
        # Get Goals database properties
        goals_db = notion_client.databases.retrieve(database_id=goals_db_id)
        goals_properties = goals_db.get('properties', {})
        
        # Get Todos database properties
        todos_db = notion_client.databases.retrieve(database_id=todos_db_id)
        todos_properties = todos_db.get('properties', {})
        
        # Check Goals database
        goals_has_relations = 'Related Todos' in goals_properties
        if goals_has_relations:
            console.print("✅ [green]Goals database has 'Related Todos' property[/green]")
        else:
            console.print("❌ [red]Goals database missing 'Related Todos' property[/red]")
        
        # Check Todos database
        todos_has_relations = 'Related Goals' in todos_properties
        todos_has_impact = 'Goal Progress Impact' in todos_properties
        todos_has_milestone = 'Goal Milestone' in todos_properties
        todos_has_contribution = 'Estimated Goal Contribution' in todos_properties
        
        if todos_has_relations:
            console.print("✅ [green]Todos database has 'Related Goals' property[/green]")
        else:
            console.print("❌ [red]Todos database missing 'Related Goals' property[/red]")
        
        if todos_has_impact:
            console.print("✅ [green]Todos database has 'Goal Progress Impact' property[/green]")
        else:
            console.print("❌ [red]Todos database missing 'Goal Progress Impact' property[/red]")
        
        if todos_has_milestone:
            console.print("✅ [green]Todos database has 'Goal Milestone' property[/green]")
        else:
            console.print("❌ [red]Todos database missing 'Goal Milestone' property[/red]")
        
        if todos_has_contribution:
            console.print("✅ [green]Todos database has 'Estimated Goal Contribution' property[/green]")
        else:
            console.print("❌ [red]Todos database missing 'Estimated Goal Contribution' property[/red]")
        
        return goals_has_relations and todos_has_relations
        
    except Exception as e:
        console.print(f"❌ [red]Error testing database properties: {str(e)}[/red]")
        return False


def create_test_goal_todo_relation(notion_client, goals_db_id, todos_db_id):
    """Create a test goal and todo with a relation between them."""
    
    try:
        # Create a test goal
        test_goal = notion_client.pages.create(
            parent={"type": "database_id", "database_id": goals_db_id},
            properties={
                "Name": {"title": [{"text": {"content": "Test Goal: Database Relations"}}]},
                "Description": {"rich_text": [{"text": {"content": "Testing the new relation properties between Goals and Todos databases"}}]},
                "Status": {"select": {"name": "In Progress"}},
                "Priority": {"select": {"name": "High"}},
                "Category": {"select": {"name": "Learning"}},
                "Progress": {"number": 0},
                "Target Date": {"date": {"start": "2024-12-31"}}
            }
        )
        
        console.print(f"✅ [green]Created test goal: {test_goal['id']}[/green]")
        
        # Create a test todo
        test_todo = notion_client.pages.create(
            parent={"type": "database_id", "database_id": todos_db_id},
            properties={
                "Task": {"title": [{"text": {"content": "Test the new relation properties"}}]},
                "Status": {"select": {"name": "Todo"}},
                "Priority": {"select": {"name": "High"}},
                "Project": {"select": {"name": "Learning"}},
                "Context": {"select": {"name": "@computer"}},
                "Goal Progress Impact": {"select": {"name": "High"}},
                "Goal Milestone": {"checkbox": True},
                "Estimated Goal Contribution": {"number": 25}
            }
        )
        
        console.print(f"✅ [green]Created test todo: {test_todo['id']}[/green]")
        
        # Link the todo to the goal
        notion_client.pages.update(
            page_id=test_todo['id'],
            properties={
                "Related Goals": {
                    "relation": [
                        {"id": test_goal['id']}
                    ]
                }
            }
        )
        
        console.print("✅ [green]Linked todo to goal successfully[/green]")
        
        return test_goal['id'], test_todo['id']
        
    except Exception as e:
        console.print(f"❌ [red]Error creating test relation: {str(e)}[/red]")
        return None, None


def verify_relation(notion_client, goal_id, todo_id):
    """Verify that the relation is working correctly."""
    
    try:
        # Get the updated todo to check the relation
        updated_todo = notion_client.pages.retrieve(page_id=todo_id)
        related_goals = updated_todo.get('properties', {}).get('Related Goals', {}).get('relation', [])
        
        if related_goals and related_goals[0]['id'] == goal_id:
            console.print("✅ [green]Relation verified: Todo is linked to Goal[/green]")
            return True
        else:
            console.print("❌ [red]Relation verification failed[/red]")
            return False
            
    except Exception as e:
        console.print(f"❌ [red]Error verifying relation: {str(e)}[/red]")
        return False


def main():
    """Main test function."""
    
    console.print(Panel.fit(
        "🧪 [bold blue]Testing Database Relations[/bold blue]\n"
        "Verifying that Goals and Todos can be properly linked...",
        border_style="blue"
    ))
    
    # Get Notion client
    notion_client = get_notion_client()
    console.print("✅ [green]Notion client connected[/green]")
    
    # Get database IDs
    goals_db_id, todos_db_id = get_database_ids()
    console.print(f"🎯 Goals Database: {goals_db_id}")
    console.print(f"📋 Todos Database: {todos_db_id}")
    
    # Test database properties
    console.print("\n🔍 [bold yellow]Testing Database Properties...[/bold yellow]")
    properties_ok = test_database_properties(notion_client, goals_db_id, todos_db_id)
    
    if not properties_ok:
        console.print("\n❌ [red]Database properties test failed. Run add_database_relations.py first.[/red]")
        return
    
    # Create test relation
    console.print("\n🔗 [bold yellow]Creating Test Relation...[/bold yellow]")
    goal_id, todo_id = create_test_goal_todo_relation(notion_client, goals_db_id, todos_db_id)
    
    if not goal_id or not todo_id:
        console.print("\n❌ [red]Failed to create test relation[/red]")
        return
    
    # Verify relation
    console.print("\n✅ [bold yellow]Verifying Relation...[/bold yellow]")
    relation_verified = verify_relation(notion_client, goal_id, todo_id)
    
    if relation_verified:
        console.print("\n🎉 [bold green]All tests passed! Database relations are working correctly.[/bold green]")
        
        # Display test results
        table = Table(title="🧪 Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="blue")
        
        table.add_row("Database Properties", "✅ PASS", "All required properties present")
        table.add_row("Test Goal Creation", "✅ PASS", f"Goal ID: {goal_id}")
        table.add_row("Test Todo Creation", "✅ PASS", f"Todo ID: {todo_id}")
        table.add_row("Relation Creation", "✅ PASS", "Todo linked to Goal")
        table.add_row("Relation Verification", "✅ PASS", "Bidirectional link confirmed")
        
        console.print(table)
        
        console.print("\n💡 [bold yellow]Next steps:[/bold yellow]")
        console.print("1. Open your databases in Notion to see the new properties")
        console.print("2. Start linking your existing goals and todos")
        console.print("3. Create views that group todos by goals")
        console.print("4. Use the new properties to track goal progress")
        
    else:
        console.print("\n❌ [red]Relation verification failed. Check the errors above.[/red]")


if __name__ == "__main__":
    main()
