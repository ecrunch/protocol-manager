"""
Test script to verify database relations are working correctly.

This script tests the relation properties between Goals and Todos databases
to ensure they're properly linked.
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

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
        console.print("Please install with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error creating Notion client: {str(e)}[/red]")
        sys.exit(1)

def test_database_relations():
    """Test the relation properties between Goals and Todos databases."""
    
    try:
        notion_client = get_notion_client()
        
        # Get database IDs from environment
        goals_db_id = os.getenv('NOTION_GOALS_DATABASE_ID')
        todos_db_id = os.getenv('NOTION_TODOS_DATABASE_ID')
        
        if not goals_db_id or not todos_db_id:
            console.print("❌ [red]Database IDs not found in environment variables[/red]")
            console.print("Please set NOTION_GOALS_DATABASE_ID and NOTION_TODOS_DATABASE_ID")
            sys.exit(1)
        
        console.print("🔍 [cyan]Testing database relations...[/cyan]")
        
        # Get all goals
        goals_response = notion_client.databases.query(database_id=goals_db_id)
        goals = goals_response.results
        
        # Get all todos
        todos_response = notion_client.databases.query(database_id=todos_db_id)
        todos = todos_response.results
        
        console.print(f"📊 Found {len(goals)} goals and {len(todos)} todos")
        
        # Test Goals database relations
        console.print("\n🎯 [cyan]Goals Database Relations:[/cyan]")
        goals_table = Table(title="Goals and Their Related Todos")
        goals_table.add_column("Goal Name", style="cyan")
        goals_table.add_column("Related Todos Count", style="green")
        goals_table.add_column("Related Todos", style="blue")
        
        for goal in goals:
            title_prop = goal.properties.get("Name", {}).get("title", [])
            goal_title = title_prop[0].get("plain_text", "") if title_prop else "Untitled"
            
            related_todos = goal.properties.get("Related Todos", {}).get("relation", [])
            related_todos_count = len(related_todos)
            
            # Get the actual todo titles
            related_todo_titles = []
            for todo_ref in related_todos:
                try:
                    todo_page = notion_client.pages.retrieve(todo_ref.id)
                    todo_title_prop = todo_page.properties.get("Task", {}).get("title", [])
                    if todo_title_prop:
                        todo_title = todo_title_prop[0].get("plain_text", "")
                        related_todo_titles.append(todo_title)
                except Exception as e:
                    related_todo_titles.append(f"Error: {str(e)}")
            
            goals_table.add_row(
                goal_title,
                str(related_todos_count),
                ", ".join(related_todo_titles) if related_todo_titles else "None"
            )
        
        console.print(goals_table)
        
        # Test Todos database relations
        console.print("\n📋 [cyan]Todos Database Relations:[/cyan]")
        todos_table = Table(title="Todos and Their Related Goals")
        todos_table.add_column("Todo Name", style="cyan")
        todos_table.add_column("Related Goals Count", style="green")
        todos_table.add_column("Related Goals", style="blue")
        todos_table.add_column("Goal Progress Impact", style="yellow")
        todos_table.add_column("Goal Milestone", style="purple")
        
        for todo in todos:
            title_prop = todo.properties.get("Task", {}).get("title", [])
            todo_title = title_prop[0].get("plain_text", "") if title_prop else "Untitled"
            
            related_goals = todo.properties.get("Related Goals", {}).get("relation", [])
            related_goals_count = len(related_goals)
            
            # Get the actual goal titles
            related_goal_titles = []
            for goal_ref in related_goals:
                try:
                    goal_page = notion_client.pages.retrieve(goal_ref.id)
                    goal_title_prop = goal_page.properties.get("Name", {}).get("title", [])
                    if goal_title_prop:
                        goal_title = goal_title_prop[0].get("plain_text", "")
                        related_goal_titles.append(goal_title)
                except Exception as e:
                    related_goal_titles.append(f"Error: {str(e)}")
            
            # Get goal tracking properties
            goal_impact = todo.properties.get("Goal Progress Impact", {}).get("select", {}).get("name", "Not Set")
            goal_milestone = todo.properties.get("Goal Milestone", {}).get("checkbox", False)
            
            todos_table.add_row(
                todo_title,
                str(related_goals_count),
                ", ".join(related_goal_titles) if related_goal_titles else "None",
                goal_impact,
                "✓" if goal_milestone else "✗"
            )
        
        console.print(todos_table)
        
        # Summary
        total_relations = sum(len(goal.properties.get("Related Todos", {}).get("relation", [])) for goal in goals)
        total_todo_relations = sum(len(todo.properties.get("Related Goals", {}).get("relation", [])) for todo in todos)
        
        console.print(f"\n🔗 [cyan]Relations Summary:[/cyan]")
        console.print(f"   • Goals with related todos: {sum(1 for g in goals if g.properties.get('Related Todos', {}).get('relation', []))}/{len(goals)}")
        console.print(f"   • Todos with related goals: {sum(1 for t in todos if t.properties.get('Related Goals', {}).get('relation', []))}/{len(todos)}")
        console.print(f"   • Total goal-todo relations: {total_relations}")
        console.print(f"   • Total todo-goal relations: {total_todo_relations}")
        
        if total_relations == 0:
            console.print("\n⚠️ [yellow]No relations found![/yellow]")
            console.print("Try running: protocol import-goals-rules")
            console.print("Or manually link todos to goals in Notion")
        else:
            console.print("\n✅ [green]Relations are working correctly![/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Error testing relations: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_relations()
