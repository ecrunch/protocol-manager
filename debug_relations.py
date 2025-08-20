"""
Debug script to check the current state of relations and see what's happening.
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
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
        console.print("Please install with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error creating Notion client: {str(e)}[/red]")
        sys.exit(1)

def debug_relations():
    """Debug the current state of relations."""
    
    try:
        notion_client = get_notion_client()
        
        # Get database IDs from environment
        goals_db_id = os.getenv('NOTION_GOALS_DATABASE_ID')
        todos_db_id = os.getenv('NOTION_TODOS_DATABASE_ID')
        
        if not goals_db_id or not todos_db_id:
            console.print("❌ [red]Database IDs not found in environment variables[/red]")
            return
        
        console.print("🔍 [cyan]Debugging Relations...[/cyan]")
        
        # Get all goals and todos
        goals_response = notion_client.databases.query(database_id=goals_db_id)
        goals = goals_response.results
        
        todos_response = notion_client.databases.query(database_id=todos_db_id)
        todos = todos_response.results
        
        console.print(f"📊 Found {len(goals)} goals and {len(todos)} todos")
        
        # Show goals and their current relations
        console.print("\n🎯 [cyan]Goals and Current Relations:[/cyan]")
        for goal in goals:
            title_prop = goal.properties.get("Name", {}).get("title", [])
            goal_title = title_prop[0].get("plain_text", "") if title_prop else "Untitled"
            
            related_todos = goal.properties.get("Related Todos", {}).get("relation", [])
            console.print(f"\n   • {goal_title} (ID: {goal.id})")
            console.print(f"     Related Todos: {len(related_todos)}")
            
            if related_todos:
                for i, todo_ref in enumerate(related_todos):
                    try:
                        if hasattr(todo_ref, 'id'):
                            todo_id = todo_ref.id
                        elif isinstance(todo_ref, dict) and 'id' in todo_ref:
                            todo_id = todo_ref['id']
                        else:
                            todo_id = str(todo_ref)
                        
                        todo_page = notion_client.pages.retrieve(todo_id)
                        todo_title_prop = todo_page.properties.get("Task", {}).get("title", [])
                        if todo_title_prop:
                            todo_title = todo_title_prop[0].get("plain_text", "")
                            console.print(f"       {i+1}. {todo_title} (ID: {todo_id})")
                        else:
                            console.print(f"       {i+1}. [No title] (ID: {todo_id})")
                    except Exception as e:
                        console.print(f"       {i+1}. [Error: {e}]")
            else:
                console.print(f"     [No related todos]")
        
        # Show todos and their current relations
        console.print("\n📋 [cyan]Todos and Current Relations:[/cyan]")
        for todo in todos:
            title_prop = todo.properties.get("Task", {}).get("title", [])
            todo_title = title_prop[0].get("plain_text", "") if title_prop else "Untitled"
            
            project = todo.properties.get("Project", {}).get("select", {}).get("name", "Unknown")
            related_goals = todo.properties.get("Related Goals", {}).get("relation", [])
            
            console.print(f"\n   • {todo_title} (ID: {todo.id})")
            console.print(f"     Project: {project}")
            console.print(f"     Related Goals: {len(related_goals)}")
            
            if related_goals:
                for i, goal_ref in enumerate(related_goals):
                    try:
                        if hasattr(goal_ref, 'id'):
                            goal_id = goal_ref.id
                        elif isinstance(goal_ref, dict) and 'id' in goal_ref:
                            goal_id = goal_ref['id']
                        else:
                            goal_id = str(goal_ref)
                        
                        goal_page = notion_client.pages.retrieve(goal_id)
                        goal_title_prop = goal_page.properties.get("Name", {}).get("title", [])
                        if goal_title_prop:
                            goal_title = goal_title_prop[0].get("plain_text", "")
                            console.print(f"       {i+1}. {goal_title} (ID: {goal_id})")
                        else:
                            console.print(f"       {i+1}. [No title] (ID: {goal_id})")
                    except Exception as e:
                        console.print(f"       {i+1}. [Error: {e}]")
            else:
                console.print(f"     [No related goals]")
        
        # Check for expected relations based on project mapping
        console.print("\n🔍 [cyan]Expected vs Actual Relations:[/cyan]")
        project_to_goal = {
            "Machine Learning": "Machine Learning Study",
            "Health": "Athletics & Health", 
            "Mental Health": "Mental Health & Clarity",
            "Planning": "Planning & Organization"
        }
        
        for project, expected_goal in project_to_goal.items():
            todos_with_project = [t for t in todos if t.properties.get("Project", {}).get("select", {}).get("name") == project]
            console.print(f"\n   Project: {project}")
            console.print(f"     Expected Goal: {expected_goal}")
            console.print(f"     Todos with this project: {len(todos_with_project)}")
            
            for todo in todos_with_project:
                todo_title = todo.properties.get("Task", {}).get("title", [])[0].get("plain_text", "") if todo.properties.get("Task", {}).get("title", []) else "Unknown"
                related_goals = todo.properties.get("Related Goals", {}).get("relation", [])
                console.print(f"       • {todo_title}: {len(related_goals)} related goals")
                
                if related_goals:
                    for goal_ref in related_goals:
                        try:
                            if hasattr(goal_ref, 'id'):
                                goal_id = goal_ref.id
                            elif isinstance(goal_ref, dict) and 'id' in goal_ref:
                                goal_id = goal_ref['id']
                            else:
                                goal_id = str(goal_ref)
                            
                            goal_page = notion_client.pages.retrieve(goal_id)
                            goal_title_prop = goal_page.properties.get("Name", {}).get("title", [])
                            if goal_title_prop:
                                goal_title = goal_title_prop[0].get("plain_text", "")
                                console.print(f"         - {goal_title}")
                            else:
                                console.print(f"         - [No title]")
                        except Exception as e:
                            console.print(f"         - [Error: {e}]")
                else:
                    console.print(f"         - [No related goals]")
        
    except Exception as e:
        console.print(f"❌ [red]Error debugging relations: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_relations()
