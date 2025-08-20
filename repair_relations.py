"""
Repair script to fix any existing relations that might have been overwritten.

This script checks the current state of relations and can repair them if needed.
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

def repair_relations():
    """Repair any broken or overwritten relations."""
    
    try:
        notion_client = get_notion_client()
        
        # Get database IDs from environment
        goals_db_id = os.getenv('NOTION_GOALS_DATABASE_ID')
        todos_db_id = os.getenv('NOTION_TODOS_DATABASE_ID')
        
        if not goals_db_id or not todos_db_id:
            console.print("❌ [red]Database IDs not found in environment variables[/red]")
            console.print("Please set NOTION_GOALS_DATABASE_ID and NOTION_TODOS_DATABASE_ID")
            sys.exit(1)
        
        console.print("🔧 [cyan]Repairing database relations...[/cyan]")
        
        # Get all goals and todos
        goals_response = notion_client.databases.query(database_id=goals_db_id)
        goals = goals_response.results
        
        todos_response = notion_client.databases.query(database_id=todos_db_id)
        todos = todos_response.results
        
        console.print(f"📊 Found {len(goals)} goals and {len(todos)} todos")
        
        # Project to goal mapping (same as in the import script)
        project_to_goal = {
            "Machine Learning": "Machine Learning Study",
            "Health": "Athletics & Health", 
            "Mental Health": "Mental Health & Clarity",
            "Planning": "Planning & Organization"
        }
        
        # Create goal title to ID mapping
        goal_mapping = {}
        for goal in goals:
            title_prop = goal.properties.get("Name", {}).get("title", [])
            if title_prop:
                goal_title = title_prop[0].get("plain_text", "")
                goal_mapping[goal_title] = goal.id
        
        console.print(f"🎯 Goal mapping created: {list(goal_mapping.keys())}")
        
        # Check and repair relations
        repairs_made = 0
        
        for todo in todos:
            todo_title_prop = todo.properties.get("Task", {}).get("title", [])
            if not todo_title_prop:
                continue
                
            todo_title = todo_title_prop[0].get("plain_text", "")
            todo_project = todo.properties.get("Project", {}).get("select", {}).get("name", "")
            
            # Find which goal this todo should be linked to
            target_goal_title = None
            for project, goal_title in project_to_goal.items():
                if project in todo_project or project.lower() in todo_title.lower():
                    target_goal_title = goal_title
                    break
            
            if not target_goal_title or target_goal_title not in goal_mapping:
                continue
            
            target_goal_id = goal_mapping[target_goal_title]
            
            # Check current relations
            current_goal_relations = todo.properties.get("Related Goals", {}).get("relation", [])
            current_goal_ids = [rel.id for rel in current_goal_relations]
            
            # Check if this goal is already linked
            if target_goal_id not in current_goal_ids:
                console.print(f"🔗 [cyan]Repairing: {todo_title} → {target_goal_title}[/cyan]")
                
                try:
                    # Add the goal to the todo's relations
                    new_goal_ids = current_goal_ids + [target_goal_id]
                    notion_client.pages.update(
                        page_id=todo.id,
                        properties={
                            "Related Goals": {
                                "relation": [{"id": gid} for gid in new_goal_ids]
                            }
                        }
                    )
                    
                    # Add the todo to the goal's relations
                    goal_page = notion_client.pages.retrieve(target_goal_id)
                    current_todo_relations = goal_page.properties.get("Related Todos", {}).get("relation", [])
                    current_todo_ids = [rel.id for rel in current_todo_relations]
                    
                    if todo.id not in current_todo_ids:
                        new_todo_ids = current_todo_ids + [todo.id]
                        notion_client.pages.update(
                            page_id=target_goal_id,
                            properties={
                                "Related Todos": {
                                    "relation": [{"id": tid} for tid in new_todo_ids]
                                }
                            }
                        )
                    
                    repairs_made += 1
                    console.print(f"   ✅ [green]Repaired relation[/green]")
                    
                except Exception as e:
                    console.print(f"   ❌ [red]Failed to repair: {e}[/red]")
        
        console.print(f"\n🔧 [cyan]Repair Summary:[/cyan]")
        console.print(f"   • {repairs_made} relations repaired")
        
        if repairs_made == 0:
            console.print("   ✅ [green]All relations are already correct![/green]")
        else:
            console.print("   🎯 [green]Relations have been repaired![/green]")
            console.print("   💡 Run 'python test_relations_working.py' to verify")
        
    except Exception as e:
        console.print(f"❌ [red]Error repairing relations: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

def show_current_relations():
    """Show the current state of relations."""
    
    try:
        notion_client = get_notion_client()
        
        # Get database IDs from environment
        goals_db_id = os.getenv('NOTION_GOALS_DATABASE_ID')
        todos_db_id = os.getenv('NOTION_TODOS_DATABASE_ID')
        
        if not goals_db_id or not todos_db_id:
            console.print("❌ [red]Database IDs not found in environment variables[/red]")
            return
        
        console.print("🔍 [cyan]Current Relations Status:[/cyan]")
        
        # Get all goals and todos
        goals_response = notion_client.databases.query(database_id=goals_db_id)
        goals = goals_response.results
        
        todos_response = notion_client.databases.query(database_id=todos_db_id)
        todos = todos_response.results
        
        # Show goals and their related todos
        console.print("\n🎯 [cyan]Goals and Related Todos:[/cyan]")
        for goal in goals:
            title_prop = goal.properties.get("Name", {}).get("title", [])
            goal_title = title_prop[0].get("plain_text", "") if title_prop else "Untitled"
            
            related_todos = goal.properties.get("Related Todos", {}).get("relation", [])
            console.print(f"   • {goal_title}: {len(related_todos)} related todos")
            
            if related_todos:
                for todo_ref in related_todos:
                    try:
                        todo_page = notion_client.pages.retrieve(todo_ref.id)
                        todo_title_prop = todo_page.properties.get("Task", {}).get("title", [])
                        if todo_title_prop:
                            todo_title = todo_title_prop[0].get("plain_text", "")
                            console.print(f"     - {todo_title}")
                    except Exception:
                        console.print(f"     - [Error retrieving todo]")
        
        # Show todos and their related goals
        console.print("\n📋 [cyan]Todos and Related Goals:[/cyan]")
        for todo in todos:
            title_prop = todo.properties.get("Task", {}).get("title", [])
            todo_title = title_prop[0].get("plain_text", "") if title_prop else "Untitled"
            
            related_goals = todo.properties.get("Related Goals", {}).get("relation", [])
            console.print(f"   • {todo_title}: {len(related_goals)} related goals")
            
            if related_goals:
                for goal_ref in related_goals:
                    try:
                        goal_page = notion_client.pages.retrieve(goal_ref.id)
                        goal_title_prop = goal_page.properties.get("Name", {}).get("title", [])
                        if goal_title_prop:
                            goal_title = goal_title_prop[0].get("plain_text", "")
                            console.print(f"     - {goal_title}")
                    except Exception:
                        console.print(f"     - [Error retrieving goal]")
        
    except Exception as e:
        console.print(f"❌ [red]Error showing relations: {str(e)}[/red]")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "repair":
        repair_relations()
    else:
        show_current_relations()
        console.print("\n💡 To repair relations, run: python repair_relations.py repair")
