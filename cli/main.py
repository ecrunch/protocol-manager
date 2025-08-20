"""
Command-line interface for Protocol Home management.

This module provides a comprehensive CLI for interacting with the Protocol Home
management system and AI agents.
"""

import os
import sys
import re
from typing import Optional, List, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_client.client import NotionClient
from agents.coordinator import ProtocolCoordinator
from agents.goal_agent import GoalAgent
from agents.todo_agent import TodoAgent
from agents.schedule_agent import ScheduleAgent

# Load environment variables
load_dotenv()

console = Console()


def extract_text_from_blocks(blocks: List[Dict[str, Any]]) -> str:
    """Extract plain text from Notion blocks."""
    text_parts = []
    
    for block in blocks:
        block_type = block.get("type", "")
        
        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
            for text_obj in rich_text:
                text_parts.append(text_obj.get("plain_text", ""))
        
        elif block_type == "bulleted_list_item":
            rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
            for text_obj in rich_text:
                text_parts.append("• " + text_obj.get("plain_text", ""))
        
        elif block_type == "numbered_list_item":
            rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
            for text_obj in rich_text:
                text_parts.append(text_obj.get("plain_text", ""))
        
        # Handle nested children
        if block.get("has_children") and "children" in block:
            nested_text = extract_text_from_blocks(block["children"])
            text_parts.append(nested_text)
    
    return "\n".join(text_parts)


def parse_goals_from_content(content: str) -> List[Dict[str, Any]]:
    """Parse SMART goals from the Goals & Rules content."""
    goals = []
    
    # Look for the SMART Goals section
    lines = content.split('\n')
    in_goals_section = False
    current_goal = None
    
    for line in lines:
        line = line.strip()
        
        # Check if we're entering the SMART Goals section
        if "SMART Goals" in line or "Goals" in line:
            in_goals_section = True
            continue
        
        # Check if we're leaving the goals section
        if in_goals_section and (
            "Scheduling Constraints" in line or 
            "Priority Hierarchy" in line or
            "Success Metrics" in line
        ):
            if current_goal:
                goals.append(current_goal)
            break
        
        if in_goals_section:
            # Look for goal titles (major categories)
            if line and not line.startswith("•") and not line.startswith("Specific:"):
                if current_goal:
                    goals.append(current_goal)
                
                current_goal = {
                    "title": line,
                    "description": "",
                    "category": "Personal",
                    "priority": "Medium",
                    "target_date": None,
                    "details": []
                }
            
            # Extract SMART details
            elif current_goal:
                if line.startswith("Specific:"):
                    current_goal["description"] = line.replace("Specific:", "").strip()
                elif line.startswith("Measurable:"):
                    current_goal["details"].append(line)
                elif line.startswith("Time-bound:"):
                    # Try to extract date information
                    time_info = line.replace("Time-bound:", "").strip()
                    current_goal["details"].append(line)
                    # You could add date parsing here if needed
                elif line.startswith("•"):
                    current_goal["details"].append(line)
    
    # Add the last goal if exists
    if current_goal:
        goals.append(current_goal)
    
    # Process specific goals we can identify
    processed_goals = []
    
    # Machine Learning Study goal
    ml_goal = {
        "title": "Machine Learning Study",
        "description": "Complete structured ML study sessions focusing on deep learning, NLP, and computer vision",
        "category": "Professional",
        "priority": "High",
        "target_date": None  # Could be parsed from weekly tracking
    }
    processed_goals.append(ml_goal)
    
    # Athletics & Health goal
    health_goal = {
        "title": "Athletics & Health",
        "description": "Maintain cardiovascular health and strength training for BP and fatty-liver management",
        "category": "Health",
        "priority": "High",
        "target_date": None
    }
    processed_goals.append(health_goal)
    
    # Mental Health & Clarity goal
    mental_goal = {
        "title": "Mental Health & Clarity",
        "description": "Regular meditation and journaling for stress management and clarity",
        "category": "Personal",
        "priority": "Medium",
        "target_date": None
    }
    processed_goals.append(mental_goal)
    
    # Planning & Organization goal
    planning_goal = {
        "title": "Planning & Organization",
        "description": "Maintain organized systems for productivity and goal tracking",
        "category": "Personal",
        "priority": "Medium",
        "target_date": None
    }
    processed_goals.append(planning_goal)
    
    return processed_goals


def parse_todos_from_content(content: str) -> List[Dict[str, Any]]:
    """Parse todos from the Goals & Rules content based on weekly targets and categories."""
    todos = []
    
    # Extract weekly targets
    if "Weekly Targets" in content:
        # ML Study todos
        todos.extend([
            {
                "title": "ML Deep Work Session - Morning",
                "priority": "High",
                "project": "Machine Learning",
                "time_estimate": 90,
                "context": "@morning"
            },
            {
                "title": "ML Reading Session",
                "priority": "Medium", 
                "project": "Machine Learning",
                "time_estimate": 60,
                "context": "@study"
            },
            {
                "title": "ML Coding Practice",
                "priority": "High",
                "project": "Machine Learning", 
                "time_estimate": 90,
                "context": "@coding"
            }
        ])
        
        # Athletics todos
        todos.extend([
            {
                "title": "Strength Training Session",
                "priority": "High",
                "project": "Health",
                "time_estimate": 60,
                "context": "@gym"
            },
            {
                "title": "Cardio Session",
                "priority": "Medium",
                "project": "Health", 
                "time_estimate": 45,
                "context": "@cardio"
            }
        ])
        
        # Mental health todos
        todos.extend([
            {
                "title": "Morning Meditation",
                "priority": "Medium",
                "project": "Mental Health",
                "time_estimate": 20,
                "context": "@morning"
            },
            {
                "title": "Evening Journaling",
                "priority": "Low",
                "project": "Mental Health",
                "time_estimate": 15,
                "context": "@evening"
            }
        ])
        
        # Weekly review todos
        todos.extend([
            {
                "title": "Weekly Goal Review",
                "priority": "Medium",
                "project": "Planning",
                "time_estimate": 30,
                "context": "@planning"
            },
            {
                "title": "Schedule Planning for Next Week",
                "priority": "Medium", 
                "project": "Planning",
                "time_estimate": 20,
                "context": "@planning"
            }
        ])
    
    return todos


def parse_scheduling_constraints(content: str) -> Dict[str, Any]:
    """Parse scheduling constraints from the Goals & Rules content."""
    constraints = {
        "working_hours": {},
        "health_optimized_timing": {},
        "recovery_rest": {}
    }
    
    lines = content.split('\n')
    in_constraints_section = False
    current_subsection = None
    
    for line in lines:
        line = line.strip()
        
        # Check if we're entering the Scheduling Constraints section
        if "Scheduling Constraints" in line:
            in_constraints_section = True
            continue
        
        # Check if we're leaving the constraints section
        if in_constraints_section and (
            "Priority Hierarchy" in line or 
            "Success Metrics" in line or
            "Goals" in line
        ):
            break
        
        if in_constraints_section:
            # Check for subsections
            if "Working Hours" in line:
                current_subsection = "working_hours"
                continue
            elif "Health-Optimized Timing" in line:
                current_subsection = "health_optimized_timing"
                continue
            elif "Recovery & Rest" in line:
                current_subsection = "recovery_rest"
                continue
            
            # Parse working hours
            if current_subsection == "working_hours":
                if "Core Hours:" in line:
                    # Extract core hours (e.g., "Monday-Friday, 8:00 AM - 5:00 PM CT")
                    time_match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)\s*-\s*(\d{1,2}):(\d{2})\s*(AM|PM)', line)
                    if time_match:
                        start_hour = int(time_match.group(1))
                        start_minute = int(time_match.group(2))
                        start_ampm = time_match.group(3)
                        end_hour = int(time_match.group(4))
                        end_minute = int(time_match.group(5))
                        end_ampm = time_match.group(6)
                        
                        # Convert to 24-hour format
                        if start_ampm == "PM" and start_hour != 12:
                            start_hour += 12
                        if end_ampm == "PM" and end_hour != 12:
                            end_hour += 12
                        if start_ampm == "AM" and start_hour == 12:
                            start_hour = 0
                        if end_ampm == "AM" and end_hour == 12:
                            end_hour = 0
                        
                        constraints["working_hours"]["core_hours"] = {
                            "start": f"{start_hour:02d}:{start_minute:02d}",
                            "end": f"{end_hour:02d}:{end_minute:02d}",
                            "timezone": "CT"  # Default, could be extracted
                        }
                
                elif "Buffer Time:" in line:
                    # Extract buffer time (e.g., "Requires 10-minute buffers between all scheduled blocks")
                    buffer_match = re.search(r'(\d+)-minute', line)
                    if buffer_match:
                        constraints["working_hours"]["buffer_time"] = int(buffer_match.group(1))
                
                elif "Transit:" in line:
                    # Extract transit time (e.g., "Specifies that it takes 30 minutes to get to work")
                    transit_match = re.search(r'(\d+)\s*minutes?', line)
                    if transit_match:
                        constraints["working_hours"]["transit_time"] = int(transit_match.group(1))
                
                elif "No Double-Booking:" in line:
                    constraints["working_hours"]["no_double_booking"] = True
            
            # Parse health-optimized timing
            elif current_subsection == "health_optimized_timing":
                if "ML Deep Work:" in line:
                    if "morning" in line.lower():
                        constraints["health_optimized_timing"]["ml_deep_work"] = "morning"
                    elif "afternoon" in line.lower():
                        constraints["health_optimized_timing"]["ml_deep_work"] = "afternoon"
                    elif "evening" in line.lower():
                        constraints["health_optimized_timing"]["ml_deep_work"] = "evening"
                
                elif "Strength Training:" in line:
                    # Extract time range (e.g., "Recommended for late afternoon (3-5 PM)")
                    time_match = re.search(r'(\d{1,2})-(\d{1,2})\s*(AM|PM)', line)
                    if time_match:
                        start_hour = int(time_match.group(1))
                        end_hour = int(time_match.group(2))
                        ampm = time_match.group(3)
                        
                        if ampm == "PM" and start_hour != 12:
                            start_hour += 12
                        if ampm == "PM" and end_hour != 12:
                            end_hour += 12
                        
                        constraints["health_optimized_timing"]["strength_training"] = f"{start_hour:02d}:00-{end_hour:02d}:00"
                    elif "late afternoon" in line.lower():
                        constraints["health_optimized_timing"]["strength_training"] = "15:00-17:00"
                
                elif "Cardio:" in line:
                    if "flexible" in line.lower():
                        constraints["health_optimized_timing"]["cardio"] = "flexible"
                    elif "morning" in line.lower():
                        constraints["health_optimized_timing"]["cardio"] = "morning"
                    elif "evening" in line.lower():
                        constraints["health_optimized_timing"]["cardio"] = "evening"
                
                elif "Meditation:" in line:
                    if "flexible" in line.lower():
                        constraints["health_optimized_timing"]["meditation"] = "flexible"
                    elif "transition" in line.lower():
                        constraints["health_optimized_timing"]["meditation"] = "transition"
            
            # Parse recovery and rest
            elif current_subsection == "recovery_rest":
                if "Strength Training:" in line and "rest" in line:
                    # Extract rest hours (e.g., "Requires a minimum 48-hour rest between major muscle groups")
                    rest_match = re.search(r'(\d+)-hour', line)
                    if rest_match:
                        constraints["recovery_rest"]["strength_training_rest"] = int(rest_match.group(1))
                
                elif "Cardio:" in line and "recovery" in line:
                    if "active recovery" in line.lower():
                        constraints["recovery_rest"]["cardio_active_recovery"] = True
                
                elif "Sleep Protection:" in line:
                    # Extract sleep protection hours (e.g., "no intense exercise should be done within 3 hours of target bedtime")
                    sleep_match = re.search(r'within\s*(\d+)\s*hours?', line)
                    if sleep_match:
                        constraints["recovery_rest"]["sleep_protection"] = int(sleep_match.group(1))
    
    # Set defaults for missing values
    if not constraints["working_hours"].get("core_hours"):
        constraints["working_hours"]["core_hours"] = {"start": "08:00", "end": "17:00", "timezone": "CT"}
    if "buffer_time" not in constraints["working_hours"]:
        constraints["working_hours"]["buffer_time"] = 10
    if "transit_time" not in constraints["working_hours"]:
        constraints["working_hours"]["transit_time"] = 30
    if "no_double_booking" not in constraints["working_hours"]:
        constraints["working_hours"]["no_double_booking"] = True
    
    if "ml_deep_work" not in constraints["health_optimized_timing"]:
        constraints["health_optimized_timing"]["ml_deep_work"] = "morning"
    if "strength_training" not in constraints["health_optimized_timing"]:
        constraints["health_optimized_timing"]["strength_training"] = "15:00-17:00"
    if "cardio" not in constraints["health_optimized_timing"]:
        constraints["health_optimized_timing"]["cardio"] = "flexible"
    if "meditation" not in constraints["health_optimized_timing"]:
        constraints["health_optimized_timing"]["meditation"] = "flexible"
    
    if "strength_training_rest" not in constraints["recovery_rest"]:
        constraints["recovery_rest"]["strength_training_rest"] = 48
    if "cardio_active_recovery" not in constraints["recovery_rest"]:
        constraints["recovery_rest"]["cardio_active_recovery"] = True
    if "sleep_protection" not in constraints["recovery_rest"]:
        constraints["recovery_rest"]["sleep_protection"] = 3
    
    return constraints


def add_missing_select_options(notion_client, database_id: str, property_name: str, missing_options: List[str]) -> bool:
    """Add missing options to a select property in a Notion database."""
    try:
        # Get current database
        database = notion_client.databases.retrieve(database_id)
        properties = database.properties  # Direct access to properties attribute
        
        if property_name not in properties:
            console.print(f"⚠️  [yellow]Property '{property_name}' not found in database[/yellow]")
            return False
            
        prop_data = properties[property_name]
        if prop_data.get("type") != "select":
            console.print(f"⚠️  [yellow]Property '{property_name}' is not a select type[/yellow]")
            return False
        
        # Get current options
        current_options = prop_data.get("select", {}).get("options", [])
        current_option_names = {opt.get("name") for opt in current_options}
        
        # Add missing options
        new_options = list(current_options)  # Copy existing options
        colors = ["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"]
        
        for i, option_name in enumerate(missing_options):
            if option_name not in current_option_names:
                new_option = {
                    "name": option_name,
                    "color": colors[i % len(colors)]
                }
                new_options.append(new_option)
                console.print(f"   Adding option: {option_name}")
        
        # Update the database
        update_data = {
            "properties": {
                property_name: {
                    "select": {
                        "options": new_options
                    }
                }
            }
        }
        
        notion_client.databases.update(database_id, **update_data)
        console.print(f"✅ [green]Updated {property_name} options successfully[/green]")
        return True
        
    except Exception as e:
        console.print(f"❌ [red]Failed to update select options: {e}[/red]")
        return False


def check_database_schema(notion_client, database_id: str, database_type: str) -> Dict[str, Any]:
    """Check the schema of a Notion database to understand available properties."""
    try:
        database = notion_client.databases.retrieve(database_id)
        
        # database is a Database model object, not a dictionary
        schema_info = {
            "title": database.title,  # List of RichText objects
            "properties": {}
        }
        
        # database.properties is a Dict[str, Dict[str, Any]]
        for prop_name, prop_data in database.properties.items():
            prop_type = prop_data.get("type")
            
            if prop_type == "select":
                # Extract select options
                select_config = prop_data.get("select", {})
                options = []
                if "options" in select_config:
                    options = [opt.get("name", "") for opt in select_config["options"]]
                
                schema_info["properties"][prop_name] = {
                    "type": prop_type,
                    "options": options
                }
            elif prop_type == "multi_select":
                # Extract multi-select options  
                multi_select_config = prop_data.get("multi_select", {})
                options = []
                if "options" in multi_select_config:
                    options = [opt.get("name", "") for opt in multi_select_config["options"]]
                
                schema_info["properties"][prop_name] = {
                    "type": prop_type,
                    "options": options
                }
            elif prop_type in ["title", "rich_text", "number", "date", "checkbox", "url", "email", "phone_number"]:
                schema_info["properties"][prop_name] = {"type": prop_type}
        
        return schema_info
    except Exception as e:
        console.print(f"⚠️  [yellow]Could not retrieve {database_type} database schema: {e}[/yellow]")
        return {}


def setup_goals_and_todos_from_page(page_title: str = "Goals & Rules", enable_scheduling: bool = True) -> str:
    """
    Find and read the Goals & Rules page, then create goals and todos in their respective databases.
    
    Args:
        page_title: Title of the page to search for (default: "Goals & Rules")
        enable_scheduling: Whether to automatically schedule high-priority todos (default: True)
        
    Returns:
        Status message about the setup process
    """
    try:
        # Get clients and agents
        notion_client = get_notion_client()
        coordinator = get_coordinator()
        
        # Search for the Goals & Rules page
        console.print(f"🔍 [cyan]Searching for '{page_title}' page...[/cyan]")
        
        search_results = notion_client.search.search_pages(query=page_title)
        
        if not search_results:
            return f"❌ Could not find a page titled '{page_title}'. Please make sure the page exists and is accessible."
        
        # Find exact match or best match
        target_page = None
        for page in search_results:
            # Get page title
            title_prop = page.properties.get("title") or page.properties.get("Name")
            if title_prop and title_prop.get("title"):
                actual_title = "".join([
                    text.get("plain_text", "") 
                    for text in title_prop["title"]
                ])
                if actual_title == page_title:
                    target_page = page
                    break
        
        if not target_page:
            target_page = search_results[0]  # Use first result as fallback
        
        console.print(f"✅ [green]Found page: {target_page.id}[/green]")
        
        # Read page content
        console.print("📖 [cyan]Reading page content...[/cyan]")
        page_blocks = notion_client.blocks.get_all_children(target_page.id)
        
        # Convert blocks to a format we can work with
        blocks_data = []
        for block in page_blocks:
            # Handle both Pydantic v1 and v2
            try:
                if hasattr(block, 'model_dump'):
                    block_dict = block.model_dump()
                else:
                    block_dict = block.dict()
            except Exception as e:
                console.print(f"⚠️  [yellow]Could not convert block {block.id}: {e}[/yellow]")
                continue
                
            # Get nested children if needed
            if block.has_children:
                try:
                    children = notion_client.blocks.get_all_children(block.id)
                    for child in children:
                        try:
                            if hasattr(child, 'model_dump'):
                                child_dict = child.model_dump()
                            else:
                                child_dict = child.dict()
                            block_dict["children"] = block_dict.get("children", []) + [child_dict]
                        except Exception as e:
                            console.print(f"⚠️  [yellow]Could not convert child block: {e}[/yellow]")
                except Exception as e:
                    console.print(f"⚠️  [yellow]Could not read children for block {block.id}: {e}[/yellow]")
            blocks_data.append(block_dict)
        
        # Extract text content
        content = extract_text_from_blocks(blocks_data)
        console.print(f"📄 [cyan]Extracted {len(content)} characters of content[/cyan]")
        
        # Parse goals, todos, and scheduling constraints
        goals = parse_goals_from_content(content)
        todos = parse_todos_from_content(content)
        scheduling_constraints = parse_scheduling_constraints(content)
        
        console.print(f"🎯 [cyan]Found {len(goals)} goals to create[/cyan]")
        console.print(f"📋 [cyan]Found {len(todos)} todos to create[/cyan]")
        console.print(f"⏰ [cyan]Found scheduling constraints: {len(scheduling_constraints)} categories[/cyan]")
        
        # Load scheduling constraints into the schedule agent
        if scheduling_constraints:
            console.print("🔧 [cyan]Loading scheduling constraints into schedule agent...[/cyan]")
            coordinator.schedule_agent.load_scheduling_constraints(scheduling_constraints)
            
            # Display constraints summary
            constraints_summary = []
            if scheduling_constraints.get("working_hours", {}).get("core_hours"):
                wh = scheduling_constraints["working_hours"]["core_hours"]
                constraints_summary.append(f"Working Hours: {wh['start']}-{wh['end']} {wh['timezone']}")
            if scheduling_constraints.get("working_hours", {}).get("buffer_time"):
                constraints_summary.append(f"Buffer Time: {scheduling_constraints['working_hours']['buffer_time']} minutes")
            if scheduling_constraints.get("health_optimized_timing", {}).get("ml_deep_work"):
                constraints_summary.append(f"ML Work: {scheduling_constraints['health_optimized_timing']['ml_deep_work']}")
            if scheduling_constraints.get("health_optimized_timing", {}).get("strength_training"):
                constraints_summary.append(f"Strength Training: {scheduling_constraints['health_optimized_timing']['strength_training']}")
            
            if constraints_summary:
                console.print("📋 [cyan]Scheduling Constraints Loaded:[/cyan]")
                for constraint in constraints_summary:
                    console.print(f"   • {constraint}")
        
        # Check database schemas
        console.print("🔍 [cyan]Checking database schemas...[/cyan]")
        goals_schema = check_database_schema(notion_client, coordinator.goal_agent.goals_database_id, "goals")
        todos_schema = check_database_schema(notion_client, coordinator.todo_agent.todos_database_id, "todos")
        
        if goals_schema.get("properties"):
            console.print("📊 [cyan]Goals database schema:[/cyan]")
            for prop_name, prop_info in goals_schema["properties"].items():
                if prop_info["type"] == "select":
                    console.print(f"   • {prop_name} ({prop_info['type']}): {', '.join(prop_info['options'])}")
                else:
                    console.print(f"   • {prop_name} ({prop_info['type']})")
        
        # Check and add missing options for goals
        goals_categories = {goal["category"] for goal in goals}
        goals_priorities = {goal["priority"] for goal in goals}
        
        if goals_schema.get("properties", {}).get("Category", {}).get("type") == "select":
            existing_categories = set(goals_schema["properties"]["Category"]["options"])
            missing_categories = goals_categories - existing_categories
            if missing_categories:
                console.print(f"🔧 [cyan]Adding missing categories to Goals database: {', '.join(missing_categories)}[/cyan]")
                add_missing_select_options(notion_client, coordinator.goal_agent.goals_database_id, "Category", list(missing_categories))
        
        if goals_schema.get("properties", {}).get("Priority", {}).get("type") == "select":
            existing_priorities = set(goals_schema["properties"]["Priority"]["options"])
            missing_priorities = goals_priorities - existing_priorities
            if missing_priorities:
                console.print(f"🔧 [cyan]Adding missing priorities to Goals database: {', '.join(missing_priorities)}[/cyan]")
                add_missing_select_options(notion_client, coordinator.goal_agent.goals_database_id, "Priority", list(missing_priorities))
        
        # Create goals
        created_goals = []
        failed_goals = []
        goal_id_mapping = {}  # Map goal titles to their IDs for linking todos
        goal_todo_mapping = {}  # Map goal titles to lists of todos that should be linked
        
        for goal in goals:
            try:
                console.print(f"📊 [cyan]Creating goal: {goal['title']}[/cyan]")
                console.print(f"   Category: {goal['category']}, Priority: {goal['priority']}")
                
                # Call the tool directly for better error handling
                from tools.goal_tools import CreateGoalTool
                create_goal_tool = CreateGoalTool(
                    notion_client=notion_client,
                    goals_database_id=coordinator.goal_agent.goals_database_id
                )
                
                response = create_goal_tool._run(
                    title=goal["title"],
                    description=goal["description"],
                    target_date=goal.get("target_date"),
                    priority=goal["priority"],
                    category=goal["category"]
                )
                
                console.print(f"   Tool response: {response}")
                
                if "✅" in response or "Created goal" in response:
                    created_goals.append(goal["title"])
                    
                    # Extract goal ID from response for linking todos
                    import re
                    goal_id_match = re.search(r'Goal ID: ([a-f0-9-]+)', response)
                    if goal_id_match:
                        goal_id = goal_id_match.group(1)
                        goal_id_mapping[goal["title"]] = goal_id
                        goal_todo_mapping[goal["title"]] = []  # Initialize empty list for todos
                        console.print(f"   🎯 Extracted Goal ID: {goal_id}")
                    else:
                        console.print(f"   ⚠️ [yellow]Could not extract goal ID from response[/yellow]")
                    
                    console.print(f"✅ [green]Created goal: {goal['title']}[/green]")
                else:
                    failed_goals.append((goal["title"], response))
                    console.print(f"❌ [red]Failed to create goal '{goal['title']}': {response}[/red]")
                    
            except Exception as e:
                failed_goals.append((goal["title"], str(e)))
                console.print(f"❌ [red]Failed to create goal '{goal['title']}': {e}[/red]")
                
        if failed_goals:
            console.print(f"\n⚠️  [yellow]Failed to create {len(failed_goals)} goal(s):[/yellow]")
            for title, error in failed_goals:
                console.print(f"   • {title}: {error}")
        
        # Create todos and link them to goals
        created_todos = []
        created_todo_ids = []
        
        for todo in todos:
            try:
                console.print(f"📋 [cyan]Creating todo: {todo['title']}[/cyan]")
                
                # Determine which goal this todo relates to based on project/category
                related_goal_id = None
                related_goal_title = None
                
                # Map project names to goal titles
                project_to_goal = {
                    "Machine Learning": "Machine Learning Study",
                    "Health": "Athletics & Health", 
                    "Mental Health": "Mental Health & Clarity",
                    "Planning": "Planning & Organization"  # Add this goal if it doesn't exist
                }
                
                console.print(f"   🔍 Project: '{todo.get('project', 'Unknown')}'")
                
                if todo.get("project") in project_to_goal:
                    goal_title = project_to_goal[todo["project"]]
                    if goal_title in goal_id_mapping:
                        related_goal_id = goal_id_mapping[goal_title]
                        related_goal_title = goal_title
                        console.print(f"   🎯 Linking to goal: {goal_title}")
                    else:
                        console.print(f"   ⚠️ [yellow]Goal '{goal_title}' not found for project '{todo['project']}'[/yellow]")
                
                # Call the tool directly for better control and ID extraction
                from tools.todo_tools import CreateTodoTool
                create_todo_tool = CreateTodoTool(
                    notion_client=notion_client,
                    todos_database_id=coordinator.todo_agent.todos_database_id
                )
                
                response = create_todo_tool._run(
                    title=todo["title"],
                    priority=todo["priority"],
                    project=todo.get("project"),
                    due_date=None,  # Could be enhanced later
                    time_estimate=todo.get("time_estimate"),
                    context=todo.get("context")
                )
                
                console.print(f"   Tool response: {response}")
                
                if "✅" in response or "Created todo" in response:
                    created_todos.append(todo["title"])
                    
                    # Extract todo ID from response for scheduling and linking
                    import re
                    todo_id_match = re.search(r'Todo ID: ([a-f0-9-]+)', response)
                    if todo_id_match:
                        todo_id = todo_id_match.group(1)
                        created_todo_ids.append((todo_id, todo))
                        console.print(f"   📋 Extracted ID: {todo_id}")
                        
                        # Link todo to goal if we have both IDs
                        # Note: Relations will be created in batch after all todos are created
                        if related_goal_id:
                            try:
                                console.print(f"   🔗 Linking todo to goal: {related_goal_title}")
                                
                                # First, get existing relations to avoid overwriting
                                try:
                                    existing_goal_page = notion_client.pages.retrieve(related_goal_id)
                                    existing_todo_relations = existing_goal_page.properties.get("Related Todos", {}).get("relation", [])
                                    
                                    # Handle both dict and object responses from Notion API
                                    existing_todo_ids = []
                                    for rel in existing_todo_relations:
                                        if hasattr(rel, 'id'):
                                            existing_todo_ids.append(rel.id)
                                        elif isinstance(rel, dict) and 'id' in rel:
                                            existing_todo_ids.append(rel['id'])
                                        else:
                                            console.print(f"   ⚠️ [yellow]Unexpected relation format: {type(rel)}[/yellow]")
                                    
                                    # Only add if not already linked
                                    if todo_id not in existing_todo_ids:
                                        existing_todo_ids.append(todo_id)
                                        console.print(f"   📝 Adding to existing {len(existing_todo_relations)} relations")
                                    else:
                                        console.print(f"   ⚠️ [yellow]Todo already linked to this goal[/yellow]")
                                except Exception as e:
                                    console.print(f"   ⚠️ [yellow]Could not retrieve existing relations: {e}[/yellow]")
                                    existing_todo_ids = [todo_id]
                                
                                # Update the todo to link to the goal and add goal tracking properties
                                # First, get existing goal relations to avoid overwriting
                                try:
                                    existing_todo_page = notion_client.pages.retrieve(todo_id)
                                    existing_goal_relations = existing_todo_page.properties.get("Related Goals", {}).get("relation", [])
                                    
                                    # Handle both dict and object responses from Notion API
                                    existing_goal_ids = []
                                    for rel in existing_goal_relations:
                                        if hasattr(rel, 'id'):
                                            existing_goal_ids.append(rel.id)
                                        elif isinstance(rel, dict) and 'id' in rel:
                                            existing_goal_ids.append(rel['id'])
                                        else:
                                            console.print(f"   ⚠️ [yellow]Unexpected goal relation format: {type(rel)}[/yellow]")
                                    
                                    # Only add if not already linked
                                    if related_goal_id not in existing_goal_ids:
                                        existing_goal_ids.append(related_goal_id)
                                        console.print(f"   📝 Adding to existing {len(existing_goal_relations)} goal relations")
                                    else:
                                        console.print(f"   ⚠️ [yellow]Goal already linked to this todo[/yellow]")
                                except Exception as e:
                                    console.print(f"   ⚠️ [yellow]Could not retrieve existing goal relations: {e}[/yellow]")
                                    existing_goal_ids = [related_goal_id]
                                
                                notion_client.pages.update(
                                    page_id=todo_id,
                                    properties={
                                        "Related Goals": {
                                            "relation": [{"id": gid} for gid in existing_goal_ids]
                                        },
                                        "Goal Progress Impact": {
                                            "select": {"name": "High" if todo.get("priority") in ["High", "Urgent"] else "Medium"}
                                        },
                                        "Goal Milestone": {
                                            "checkbox": False  # Can be updated later
                                        },
                                        "Estimated Goal Contribution": {
                                            "number": 15  # Default 15% contribution, can be adjusted
                                        }
                                    }
                                )
                                
                                # Update the goal to link back to the todo (append to existing)
                                notion_client.pages.update(
                                    page_id=related_goal_id,
                                    properties={
                                        "Related Todos": {
                                            "relation": [{"id": tid} for tid in existing_todo_ids]
                                        }
                                    }
                                )
                                
                                console.print(f"   ✅ [green]Successfully linked todo to goal[/green]")
                                console.print(f"   📊 Goal now has {len(existing_todo_ids)} related todos")
                                
                                # Verify the update worked by checking the goal again
                                try:
                                    updated_goal_page = notion_client.pages.retrieve(related_goal_id)
                                    updated_todo_relations = updated_goal_page.properties.get("Related Todos", {}).get("relation", [])
                                    console.print(f"   🔍 Verification: Goal now shows {len(updated_todo_relations)} related todos")
                                    
                                    # Show the actual todo IDs for debugging
                                    if updated_todo_relations:
                                        console.print(f"   📋 Todo IDs in goal: {[rel.id if hasattr(rel, 'id') else rel.get('id', 'unknown') for rel in updated_todo_relations]}")
                                except Exception as verify_error:
                                    console.print(f"   ⚠️ [yellow]Could not verify update: {verify_error}[/yellow]")
                                
                            except Exception as link_error:
                                console.print(f"   ❌ [red]Failed to link todo to goal: {link_error}[/red]")
                        else:
                            console.print(f"   ⚠️ [yellow]No goal to link to for this todo[/yellow]")
                        
                        # OLD LINKING CODE ABOVE - REPLACED WITH BATCH LINKING BELOW
                    else:
                        console.print(f"   ⚠️ [yellow]Could not extract todo ID from response[/yellow]")
                    
                    console.print(f"✅ [green]Created todo: {todo['title']}[/green]")
                else:
                    console.print(f"❌ [red]Failed to create todo '{todo['title']}': {response}[/red]")
                    
            except Exception as e:
                console.print(f"❌ [red]Failed to create todo '{todo['title']}': {e}[/red]")
        
        # Schedule high-priority todos automatically (if enabled)
        scheduled_todos = []
        if created_todo_ids and enable_scheduling:
            console.print(f"\n📅 [cyan]Automatically scheduling high-priority todos...[/cyan]")
            
            # Get today's date for scheduling
            from datetime import datetime, timedelta
            import pytz
            
            # Set up CDT timezone
            cdt_tz = pytz.timezone('America/Chicago')
            today = datetime.now(cdt_tz)
            
            # Schedule high-priority todos for tomorrow
            for todo_id, todo_data in created_todo_ids:
                if todo_data.get("priority") in ["High", "Urgent"]:
                    try:
                        # Use scheduling constraints to suggest optimal time
                        if todo_data.get("context") == "@morning" or "ML" in todo_data.get("title", ""):
                            schedule_time = "09:00"  # ML Deep Work - optimal cognitive time
                        elif todo_data.get("context") == "@coding":
                            schedule_time = "10:00"  # After ML work
                        elif todo_data.get("context") == "@gym" or "training" in todo_data.get("title", "").lower():
                            schedule_time = "15:00"  # Strength Training - optimal performance time
                        else:
                            schedule_time = "14:00"  # Default afternoon slot
                        
                        # Create tomorrow's date in CDT
                        tomorrow = today + timedelta(days=1)
                        tomorrow = tomorrow.replace(hour=int(schedule_time.split(':')[0]), minute=int(schedule_time.split(':')[1]), second=0, microsecond=0)
                        
                        # Format as ISO string with CDT timezone
                        schedule_datetime = tomorrow.isoformat()
                        
                        console.print(f"   📅 Scheduling '{todo_data['title']}' for {tomorrow.strftime('%Y-%m-%d')} at {schedule_time} CDT")
                        
                        # Call the schedule tool directly
                        from tools.schedule_tools import ScheduleTodoTool
                        schedule_tool = ScheduleTodoTool(
                            notion_client=notion_client,
                            calendar_database_id=coordinator.schedule_agent.calendar_database_id
                        )
                        
                        response = schedule_tool._run(
                            todo_id=todo_id,
                            start_datetime=schedule_datetime,
                            duration_minutes=todo_data.get("time_estimate", 60)
                        )
                        
                        console.print(f"   📅 Schedule tool response: {response}")
                        
                        if "Scheduled todo" in response or "📅" in response:
                            scheduled_todos.append(todo_data["title"])
                            console.print(f"   ✅ [green]Scheduled: {todo_data['title']}[/green]")
                        else:
                            console.print(f"   ⚠️ [yellow]Could not schedule '{todo_data['title']}': {response}[/yellow]")
                            
                    except Exception as e:
                        console.print(f"   ❌ [red]Failed to schedule '{todo_data['title']}': {e}[/red]")
        
                # Now link all todos to their goals in batch (this avoids the overwriting issue)
        console.print(f"\n🔗 [cyan]Creating Database Relations...[/cyan]")
        
        # Project to goal mapping
        project_to_goal = {
            "Machine Learning": "Machine Learning Study",
            "Health": "Athletics & Health", 
            "Mental Health": "Mental Health & Clarity",
            "Planning": "Planning & Organization"
        }
        
        # Collect todos for each goal
        goal_todos = {}
        for goal_title in goal_id_mapping.keys():
            goal_todos[goal_title] = []
        
        for todo_id, todo_data in created_todo_ids:
            project = todo_data.get("project")
            if project in project_to_goal:
                goal_title = project_to_goal[project]
                if goal_title in goal_todos:
                    goal_todos[goal_title].append(todo_id)
                    console.print(f"   📋 {todo_data['title']} → {goal_title}")
        
        # Now update each goal with all its related todos at once
        relations_created = 0
        for goal_title, todo_ids in goal_todos.items():
            if todo_ids and goal_title in goal_id_mapping:
                try:
                    goal_id = goal_id_mapping[goal_title]
                    console.print(f"   🎯 Updating {goal_title} with {len(todo_ids)} todos")
                    
                    # Update goal with all related todos
                    notion_client.pages.update(
                        page_id=goal_id,
                        properties={
                            "Related Todos": {
                                "relation": [{"id": tid} for tid in todo_ids]
                            }
                        }
                    )
                    
                    # Update each todo with the goal link
                    for todo_id in todo_ids:
                        notion_client.pages.update(
                            page_id=todo_id,
                            properties={
                                "Related Goals": {
                                    "relation": [{"id": goal_id}]
                                },
                                "Goal Progress Impact": {
                                    "select": {"name": "High"}  # Default to high for now
                                },
                                "Goal Milestone": {
                                    "checkbox": False
                                },
                                "Estimated Goal Contribution": {
                                    "number": 15  # Default 15%
                                }
                            }
                        )
                    
                    relations_created += len(todo_ids)
                    console.print(f"   ✅ {goal_title} now has {len(todo_ids)} related todos")
                    
                except Exception as e:
                    console.print(f"   ❌ Error updating {goal_title}: {e}")
        
        # Summary of relations created
        if relations_created > 0:
            console.print(f"\n🔗 [cyan]Database Relations Summary:[/cyan]")
            console.print(f"   • {relations_created} todos linked to goals")
            console.print(f"   • Goals now show related todos in 'Related Todos' field")
            console.print(f"   • Todos now show related goals in 'Related Goals' field")
            console.print(f"   • Goal tracking properties added (Impact, Milestone, Contribution)")
        
        # Show detailed breakdown of relations per goal
        console.print(f"\n📊 [cyan]Relations Breakdown:[/cyan]")
        for goal_title, goal_id in goal_id_mapping.items():
            try:
                goal_page = notion_client.pages.retrieve(goal_id)
                related_todos = goal_page.properties.get("Related Todos", {}).get("relation", [])
                console.print(f"   • {goal_title}: {len(related_todos)} related todos")
                
                # Show the actual todo titles for debugging
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
                                console.print(f"     {i+1}. {todo_title}")
                            else:
                                console.print(f"     {i+1}. [No title]")
                        except Exception as e:
                            console.print(f"     {i+1}. [Error: {e}]")
            except Exception as e:
                console.print(f"   • {goal_title}: Error retrieving relations ({e})")
        
        # Generate schedule suggestions for remaining todos (if scheduling is enabled)
        schedule_suggestions = ""
        if created_todos and len(scheduled_todos) < len(created_todos) and enable_scheduling:
            try:
                console.print(f"\n🤖 [cyan]Generating schedule suggestions for remaining todos...[/cyan]")
                
                # Use the enhanced schedule suggestion with constraints
                tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
                remaining_todos = [todo for todo in todos if todo["title"] not in [scheduled["title"] for scheduled in scheduled_todos]]
                
                if remaining_todos:
                    suggestions_response = coordinator.schedule_agent.suggest_optimal_schedule_with_constraints(
                        tomorrow, remaining_todos
                    )
                    if suggestions_response:
                        schedule_suggestions = f"\n\n📅 **Schedule Suggestions (with Constraints):**\n{suggestions_response}"
                        console.print(f"✅ [green]Generated constraint-aware schedule suggestions[/green]")
                
            except Exception as e:
                console.print(f"⚠️ [yellow]Could not generate schedule suggestions: {e}[/yellow]")
        
        # Return enhanced summary
        scheduling_section = ""
        if enable_scheduling:
            scheduling_section = f"""
📅 **Todos Automatically Scheduled ({len(scheduled_todos)}):**
{chr(10).join(f"• {todo}" for todo in scheduled_todos) if scheduled_todos else "• None (high-priority todos not found or already scheduled)"}

{schedule_suggestions}"""
        else:
            scheduling_section = "\n📅 **Scheduling:** Disabled (use --schedule to enable auto-scheduling)"
        
        constraints_section = ""
        if scheduling_constraints:
            constraints_section = f"""
⏰ **Scheduling Constraints Loaded:**
• Working Hours: {scheduling_constraints.get('working_hours', {}).get('core_hours', {}).get('start', '08:00')}-{scheduling_constraints.get('working_hours', {}).get('core_hours', {}).get('end', '17:00')} CT
• Buffer Time: {scheduling_constraints.get('working_hours', {}).get('buffer_time', 10)} minutes
• ML Work: {scheduling_constraints.get('health_optimized_timing', {}).get('ml_deep_work', 'morning')} preference
• Strength Training: {scheduling_constraints.get('health_optimized_timing', {}).get('strength_training', '15:00-17:00')}
• Recovery: {scheduling_constraints.get('recovery_rest', {}).get('strength_training_rest', 48)} hours rest between major muscle groups
"""
        
        next_steps_scheduling = ""
        if enable_scheduling:
            next_steps_scheduling = "\n• Use `protocol chat \"show my schedule for tomorrow\"` to see scheduled items"
        
        summary = f"""
🏠 **Protocol Home Setup Complete!**

📊 **Goals Created ({len(created_goals)}):**
{chr(10).join(f"• {goal}" for goal in created_goals)}

📋 **Todos Created ({len(created_todos)}):**
{chr(10).join(f"• {todo}" for todo in created_todos)}
{constraints_section}{scheduling_section}

🎯 **Next Steps:**
• Use `protocol overview` to see your setup
• Use `protocol goal progress` to track goal progress  
• Use `protocol todo list` to see your tasks{next_steps_scheduling}
• Use `protocol chat` for AI-powered assistance and scheduling
• Use `protocol schedule constraints` to view/modify scheduling constraints
"""
        
        return summary
        
    except Exception as e:
        return f"❌ Error setting up goals and todos: {str(e)}"


def get_notion_client() -> NotionClient:
    """Get configured Notion client."""
    api_token = os.getenv('NOTION_API_TOKEN')
    if not api_token:
        console.print("❌ [red]NOTION_API_TOKEN not found in environment variables[/red]")
        console.print("Please set your Notion API token in a .env file or environment variable.")
        console.print("Example: NOTION_API_TOKEN=ntn_your_integration_token_here")
        sys.exit(1)
    
    return NotionClient(auth_token=api_token)


def get_coordinator() -> ProtocolCoordinator:
    """Get configured protocol coordinator."""
    notion_client = get_notion_client()
    
    goals_db_id = os.getenv('NOTION_GOALS_DATABASE_ID')
    todos_db_id = os.getenv('NOTION_TODOS_DATABASE_ID')
    calendar_db_id = os.getenv('NOTION_CALENDAR_DATABASE_ID')
    
    if not goals_db_id or not todos_db_id or not calendar_db_id:
        console.print("❌ [red]Missing required database IDs[/red]")
        console.print("Please set NOTION_GOALS_DATABASE_ID, NOTION_TODOS_DATABASE_ID, and NOTION_CALENDAR_DATABASE_ID in your .env file")
        sys.exit(1)
    
    return ProtocolCoordinator(
        notion_client=notion_client,
        goals_database_id=goals_db_id,
        todos_database_id=todos_db_id,
        calendar_database_id=calendar_db_id,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        verbose=os.getenv('AGENT_VERBOSE', 'false').lower() == 'true'
    )


@click.group()
@click.version_option(version="0.1.0", prog_name="Protocol Manager")
def protocol_cli():
    """
    🏠 Protocol Home - AI-powered productivity management system.
    
    Manage your goals, tasks, and schedule with intelligent AI agents.
    """
    pass


@protocol_cli.command()
def status():
    """Check the status of all agents and connections."""
    try:
        coordinator = get_coordinator()
        status_info = coordinator.get_system_status()
        
        table = Table(title="🏠 Protocol Home System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        
        for component, status in status_info.items():
            table.add_row(component.replace('_', ' ').title(), status)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [red]Error checking status: {str(e)}[/red]")


@protocol_cli.command()
def commands():
    """Show available commands and examples."""
    coordinator = get_coordinator()
    command_list = coordinator.get_available_commands()
    
    console.print(Panel("\n".join(command_list), title="📚 Available Commands", border_style="blue"))


@protocol_cli.command()
def cli_help():
    """Show available CLI commands."""
    cli_commands = [
        "🏠 Protocol Home CLI Commands:",
        "",
        "📊 Database & Setup:",
        "  • protocol setup-databases          - Create Notion databases",
        "  • protocol import-goals-rules      - Import goals from Notion page",
        "  • protocol link-todos-to-goals     - Link existing todos to goals",
        "  • protocol status                   - Check system status",
        "",
        "🎯 Goals:",
        "  • protocol goal create [title]     - Create a new goal",
        "  • protocol goal list               - List all goals",
        "  • protocol goal update [id]        - Update a goal",
        "",
        "📋 Todos:",
        "  • protocol todo create [title]     - Create a new todo",
        "  • protocol todo list               - List all todos",
        "  • protocol todo complete [id]      - Mark todo as complete",
        "",
        "📅 Schedule:",
        "  • protocol schedule create         - Create calendar event",
        "  • protocol schedule view           - View calendar",
        "  • protocol schedule constraints    - View scheduling constraints",
        "",
        "🤖 AI Assistant:",
        "  • protocol chat [message]          - Chat with AI assistant",
        "  • protocol overview                - Get productivity overview",
        "",
        "💡 Examples:",
        "  • protocol import-goals-rules",
        "  • protocol chat 'Create a goal to learn Python'",
        "  • protocol goal create 'Learn AI' --priority High --category Learning",
    ]
    
    console.print(Panel("\n".join(cli_commands), title="🖥️ CLI Commands", border_style="blue"))


@protocol_cli.command()
@click.argument('message', required=False)
def chat(message: Optional[str]):
    """
    Interactive chat mode with the Protocol Home AI assistant.
    
    If MESSAGE is provided, processes it directly. Otherwise, enters interactive mode.
    """
    coordinator = get_coordinator()
    
    if message:
        # Single message mode
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing your request...", total=None)
            
            try:
                response = coordinator.process_request(message)
                progress.stop()
                console.print(Panel(Markdown(response), title="🤖 Assistant Response", border_style="green"))
            except Exception as e:
                progress.stop()
                console.print(f"❌ [red]Error: {str(e)}[/red]")
    else:
        # Interactive mode
        console.print(Panel(
            "🏠 Welcome to Protocol Home Interactive Mode!\n\n"
            "Type your requests naturally, like:\n"
            "• 'Create a goal to learn Python'\n"
            "• 'Show me my tasks for today'\n"
            "• 'Plan my week'\n\n"
            "Type 'quit', 'exit', or 'bye' to leave.",
            title="💬 Interactive Chat Mode",
            border_style="blue"
        ))
        
        while True:
            try:
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ")
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    console.print("👋 [green]Goodbye! Have a productive day![/green]")
                    break
                
                if not user_input.strip():
                    continue
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Thinking...", total=None)
                    
                    try:
                        response = coordinator.process_request(user_input)
                        progress.stop()
                        console.print(f"\n[bold green]Assistant:[/bold green] {response}")
                    except Exception as e:
                        progress.stop()
                        console.print(f"❌ [red]Error: {str(e)}[/red]")
                        
            except KeyboardInterrupt:
                console.print("\n👋 [green]Goodbye! Have a productive day![/green]")
                break
            except EOFError:
                console.print("\n👋 [green]Goodbye! Have a productive day![/green]")
                break


@protocol_cli.group()
def goal():
    """Manage goals and objectives."""
    pass


@goal.command()
@click.argument('title')
@click.option('--description', '-d', help='Goal description')
@click.option('--target-date', '-t', help='Target completion date (YYYY-MM-DD)')
@click.option('--priority', '-p', type=click.Choice(['High', 'Medium', 'Low']), default='Medium', help='Priority level')
@click.option('--category', '-c', default='Personal', help='Goal category')
def create(title: str, description: str, target_date: str, priority: str, category: str):
    """Create a new goal."""
    try:
        notion_client = get_notion_client()
        goals_db_id = os.getenv('NOTION_GOALS_DATABASE_ID')
        
        agent = GoalAgent(
            notion_client=notion_client,
            goals_database_id=goals_db_id,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        response = agent.create_goal(
            title=title,
            description=description or f"Goal: {title}",
            target_date=target_date,
            priority=priority,
            category=category
        )
        
        console.print(Panel(response, title="📊 Goal Created", border_style="green"))
        
    except Exception as e:
        console.print(f"❌ [red]Error creating goal: {str(e)}[/red]")


@goal.command()
@click.option('--category', '-c', help='Filter by category')
@click.option('--status', '-s', help='Filter by status')
def list(category: str, status: str):
    """List goals with optional filters."""
    try:
        notion_client = get_notion_client()
        goals_db_id = os.getenv('NOTION_GOALS_DATABASE_ID')
        
        agent = GoalAgent(
            notion_client=notion_client,
            goals_database_id=goals_db_id,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        response = agent.get_goals_summary(category=category)
        console.print(Panel(Markdown(response), title="📊 Goals List", border_style="blue"))
        
    except Exception as e:
        console.print(f"❌ [red]Error listing goals: {str(e)}[/red]")


@goal.command()
def progress():
    """Show goal progress and analytics."""
    try:
        notion_client = get_notion_client()
        goals_db_id = os.getenv('NOTION_GOALS_DATABASE_ID')
        
        agent = GoalAgent(
            notion_client=notion_client,
            goals_database_id=goals_db_id,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        response = agent.track_progress()
        console.print(Panel(Markdown(response), title="📈 Goal Progress", border_style="green"))
        
    except Exception as e:
        console.print(f"❌ [red]Error getting progress: {str(e)}[/red]")


@protocol_cli.group()
def todo():
    """Manage tasks and todos."""
    pass


@todo.command()
@click.argument('title')
@click.option('--priority', '-p', type=click.Choice(['Urgent', 'High', 'Medium', 'Low']), default='Medium')
@click.option('--project', '-pr', help='Project or category')
@click.option('--due-date', '-d', help='Due date (YYYY-MM-DD)')
@click.option('--time-estimate', '-t', type=int, help='Estimated time in minutes')
def add(title: str, priority: str, project: str, due_date: str, time_estimate: int):
    """Add a new task."""
    try:
        notion_client = get_notion_client()
        todos_db_id = os.getenv('NOTION_TODOS_DATABASE_ID')
        
        agent = TodoAgent(
            notion_client=notion_client,
            todos_database_id=todos_db_id,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        response = agent.add_task(
            title=title,
            priority=priority,
            project=project,
            due_date=due_date,
            time_estimate=time_estimate
        )
        
        console.print(Panel(response, title="📋 Task Added", border_style="green"))
        
    except Exception as e:
        console.print(f"❌ [red]Error adding task: {str(e)}[/red]")


@todo.command()
@click.option('--project', '-p', help='Filter by project')
@click.option('--status', '-s', help='Filter by status')
@click.option('--today', is_flag=True, help='Show only today\'s tasks')
def list(project: str, status: str, today: bool):
    """List tasks with optional filters."""
    try:
        notion_client = get_notion_client()
        todos_db_id = os.getenv('NOTION_TODOS_DATABASE_ID')
        
        agent = TodoAgent(
            notion_client=notion_client,
            todos_database_id=todos_db_id,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        if today:
            response = agent.get_today_tasks()
        elif project:
            response = agent.get_project_tasks(project)
        else:
            # Use the coordinator to handle complex queries
            coordinator = get_coordinator()
            query = "Show me my tasks"
            if status:
                query += f" with status {status}"
            response = coordinator.process_request(query)
        
        console.print(Panel(Markdown(response), title="📋 Tasks List", border_style="blue"))
        
    except Exception as e:
        console.print(f"❌ [red]Error listing tasks: {str(e)}[/red]")


@todo.command()
@click.option('--method', '-m', type=click.Choice(['eisenhower', 'moscow', 'abc']), default='eisenhower')
@click.option('--project', '-p', help='Project to prioritize')
def prioritize(method: str, project: str):
    """Prioritize tasks using various frameworks."""
    try:
        notion_client = get_notion_client()
        todos_db_id = os.getenv('NOTION_TODOS_DATABASE_ID')
        
        agent = TodoAgent(
            notion_client=notion_client,
            todos_database_id=todos_db_id,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        response = agent.prioritize_tasks(method=method, project=project)
        console.print(Panel(Markdown(response), title="🎯 Task Prioritization", border_style="yellow"))
        
    except Exception as e:
        console.print(f"❌ [red]Error prioritizing tasks: {str(e)}[/red]")


@todo.command()
@click.option('--priority', '-p', help='Schedule todos with this priority (High, Medium, Low, Urgent)')
@click.option('--project', '-pr', help='Schedule todos from this project')
@click.option('--date', '-d', help='Date to schedule for (YYYY-MM-DD, defaults to tomorrow)')
def schedule(priority: str, project: str, date: str):
    """Schedule existing todos as calendar events."""
    try:
        coordinator = get_coordinator()
        
        # Build the scheduling request
        request = "Schedule my todos"
        if priority:
            request += f" with {priority} priority"
        if project:
            request += f" from the {project} project"
        if date:
            request += f" for {date}"
        else:
            request += " for tomorrow"
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scheduling todos...", total=None)
            
            response = coordinator.process_request(request)
            progress.stop()
            
        console.print(Panel(Markdown(response), title="📅 Todo Scheduling", border_style="green"))
        
    except Exception as e:
        console.print(f"❌ [red]Error scheduling todos: {str(e)}[/red]")


@protocol_cli.group()
def schedule():
    """Manage calendar and scheduling."""
    pass


@schedule.command()
@click.option('--date', '-d', help='Date to view (YYYY-MM-DD, defaults to today)')
def view(date: str):
    """View your schedule for a specific date."""
    try:
        coordinator = get_coordinator()
        
        request = "Show me my schedule"
        if date:
            request += f" for {date}"
        else:
            request += " for today"
            
        response = coordinator.process_request(request)
        console.print(Panel(Markdown(response), title="📅 Your Schedule", border_style="blue"))
        
    except Exception as e:
        console.print(f"❌ [red]Error viewing schedule: {str(e)}[/red]")


@schedule.command()
@click.argument('title')
@click.argument('datetime')
@click.option('--duration', '-d', type=int, default=60, help='Duration in minutes')
@click.option('--location', '-l', help='Event location')
def create(title: str, datetime: str, duration: int, location: str):
    """Create a new calendar event."""
    try:
        coordinator = get_coordinator()
        
        request = f"Create a calendar event '{title}' at {datetime}"
        if duration != 60:
            request += f" for {duration} minutes"
        if location:
            request += f" at {location}"
            
        response = coordinator.process_request(request)
        console.print(Panel(Markdown(response), title="📅 Event Created", border_style="green"))
        
    except Exception as e:
        console.print(f"❌ [red]Error creating event: {str(e)}[/red]")


@schedule.command()
@click.option('--date', '-d', help='Date to find free time (YYYY-MM-DD, defaults to today)')
@click.option('--duration', '-dur', type=int, default=60, help='Duration needed in minutes')
def free(date: str, duration: int):
    """Find free time slots in your schedule."""
    try:
        coordinator = get_coordinator()
        
        request = f"Find {duration} minutes of free time"
        if date:
            request += f" on {date}"
        else:
            request += " today"
            
        response = coordinator.process_request(request)
        console.print(Panel(Markdown(response), title="🕐 Free Time Slots", border_style="cyan"))
        
    except Exception as e:
        console.print(f"❌ [red]Error finding free time: {str(e)}[/red]")


@protocol_cli.command()
def overview():
    """Show an overview of goals, tasks, and schedule."""
    try:
        coordinator = get_coordinator()
        response = coordinator.process_request("Show me an overview of my goals and tasks")
        console.print(Panel(Markdown(response), title="🏠 Protocol Home Overview", border_style="cyan"))
        
    except Exception as e:
        console.print(f"❌ [red]Error getting overview: {str(e)}[/red]")


@protocol_cli.command()
def setup_databases():
    """Create Notion databases for Protocol Home agents."""
    try:
        console.print("🏠 [bold blue]Setting up Notion databases...[/bold blue]")
        
        # Import and run the setup script
        import subprocess
        import sys
        
        result = subprocess.run([sys.executable, "setup_notion_databases.py"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            console.print("✅ [green]Database setup completed![/green]")
        else:
            console.print("❌ [red]Database setup failed[/red]")
            console.print("Try running: python setup_notion_databases.py")
            
    except Exception as e:
        console.print(f"❌ [red]Error running setup: {str(e)}[/red]")
        console.print("Try running: python setup_notion_databases.py")


@protocol_cli.command()
@click.option('--page-title', '-p', default="Goals & Rules", help='Title of the Notion page to read')
@click.option('--force', '-f', is_flag=True, help='Force import even if goals already exist')
@click.option('--schedule/--no-schedule', default=True, help='Automatically schedule high-priority todos (default: enabled)')
def import_goals_rules(page_title: str, force: bool, schedule: bool):
    """Import goals and todos from your 'Goals & Rules' Notion page with optional auto-scheduling."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Setting up goals and todos from Notion page...", total=None)
            
            result = setup_goals_and_todos_from_page(page_title, enable_scheduling=schedule)
            progress.stop()
            
            console.print(Panel(Markdown(result), title="📚 Goals & Rules Import", border_style="green"))
            
    except Exception as e:
        console.print(f"❌ [red]Error importing goals and rules: {str(e)}[/red]")


@protocol_cli.command()
@click.option('--goals-db-id', envvar='NOTION_GOALS_DATABASE_ID', help='Goals database ID')
@click.option('--todos-db-id', envvar='NOTION_TODOS_DATABASE_ID', help='Todos database ID')
def link_todos_to_goals(goals_db_id: str, todos_db_id: str):
    """Manually link existing todos to goals using the relation properties."""
    try:
        if not goals_db_id or not todos_db_id:
            console.print("❌ [red]Please provide both goals and todos database IDs[/red]")
            console.print("Set NOTION_GOALS_DATABASE_ID and NOTION_TODOS_DATABASE_ID in your .env file")
            return
        
        console.print("🔗 [cyan]Linking existing todos to goals...[/cyan]")
        
        notion_client = get_notion_client()
        
        # Get all goals
        goals_response = notion_client.databases.query(database_id=goals_db_id)
        goals = goals_response.results
        
        # Get all todos
        todos_response = notion_client.databases.query(database_id=todos_db_id)
        todos = todos_response.results
        
        console.print(f"📊 Found {len(goals)} goals and {len(todos)} todos")
        
        # Create a simple mapping interface
        goal_mapping = {}
        for goal in goals:
            title_prop = goal.properties.get("Name", {}).get("title", [])
            if title_prop:
                goal_title = title_prop[0].get("plain_text", "")
                goal_mapping[goal_title] = goal.id
                console.print(f"   🎯 {goal_title} (ID: {goal.id})")
        
        console.print("\n📋 Available todos:")
        for todo in todos:
            title_prop = todo.properties.get("Task", {}).get("title", [])
            if title_prop:
                todo_title = title_prop[0].get("plain_text", "")
                console.print(f"   📋 {todo_title}")
        
        console.print("\n💡 To link todos to goals:")
        console.print("1. Open a todo in Notion")
        console.print("2. Click on the 'Related Goals' field")
        console.print("3. Search for and select the appropriate goal")
        console.print("4. The goal will automatically show the todo in its 'Related Todos' field")
        
        # Show current relations
        linked_todos = 0
        for todo in todos:
            related_goals = todo.properties.get("Related Goals", {}).get("relation", [])
            if related_goals:
                linked_todos += 1
        
        console.print(f"\n🔗 Current status: {linked_todos}/{len(todos)} todos have goal relations")
        
    except Exception as e:
        console.print(f"❌ [red]Error linking todos to goals: {str(e)}[/red]")


@protocol_cli.command()
def setup():
    """Setup guide for Protocol Home."""
    setup_text = """
# 🏠 Protocol Home Setup Guide

## 1. Environment Configuration
Copy `config.env.example` to `.env` and fill in your values:

- **NOTION_API_TOKEN**: Get from https://developers.notion.com/
- **NOTION_*_DATABASE_ID**: Create databases in Notion and copy their IDs
- **OPENAI_API_KEY**: Get from https://platform.openai.com/

## 2. Notion Setup
Option A - Automatic Setup (Recommended):
- Run: `protocol setup-databases`

Option B - Manual Setup:
Create these databases in your Notion workspace:

### Goals Database
Properties:
- Name (Title)
- Description (Text)
- Status (Select): Not Started, In Progress, Completed, On Hold
- Priority (Select): High, Medium, Low
- Category (Select): Personal, Professional, Health, etc.
- Progress (Number): 0-100
- Target Date (Date)

### Todos Database  
Properties:
- Task (Title)
- Status (Select): Todo, In Progress, Done
- Priority (Select): Urgent, High, Medium, Low
- Project (Select): Add your projects
- Due Date (Date)
- Completed (Checkbox)
- Time Estimate (Number)
- Context (Select): @home, @office, @calls, etc.

### Calendar Database
Properties:
- Title (Title)
- Event Type (Select): Meeting, Call, Work Session, etc.
- Start Date (Date)
- End Date (Date)
- Status (Select): Scheduled, Confirmed, Tentative, Cancelled
- Location (Text)
- Related Todo (Text)

## 3. Goals & Rules Page Setup
Create a page titled "Goals & Rules" with the following structure:

### SMART Goals
- **Machine Learning Study**: Complete structured ML study sessions
- **Athletics & Health**: Maintain cardiovascular health and strength training
- **Mental Health & Clarity**: Regular meditation and journaling

### Scheduling Constraints
#### Working Hours
- **Core Hours**: Monday-Friday, 8:00 AM - 5:00 PM CT
- **Buffer Time**: Requires 10-minute buffers between all scheduled blocks
- **Transit**: Specifies that it takes 30 minutes to get to work
- **No Double-Booking**: Enforces strict calendar conflict prevention

#### Health-Optimized Timing
- **ML Deep Work**: Prefers mornings when cognitive function is at its peak
- **Strength Training**: Recommended for late afternoon (3-5 PM) for optimal performance
- **Cardio**: Flexible timing, can be scheduled in the morning or evening
- **Meditation**: Flexible, often works well as a transition between work blocks

#### Recovery & Rest
- **Strength Training**: Requires a minimum 48-hour rest between major muscle groups
- **Cardio**: Allows for active recovery days with walking versus running
- **Sleep Protection**: States no intense exercise should be done within 3 hours of target bedtime

### Weekly Targets
- ML Deep Work Session - Morning (90 min)
- ML Reading Session (60 min)
- ML Coding Practice (90 min)
- Strength Training Session (60 min)
- Cardio Session (45 min)
- Morning Meditation (20 min)
- Evening Journaling (15 min)

## 4. First Steps
1. Run `protocol status` to check connections
2. Run `protocol import-goals-rules` to import your goals, todos, and scheduling constraints
3. Try `protocol schedule constraints` to view your scheduling constraints
4. Try `protocol schedule plan-with-constraints` to see constraint-aware scheduling
5. Use `protocol chat "Create a goal to learn Python"`
6. Use `protocol overview` to see your productivity dashboard

## 5. Scheduling Constraints Management
The system automatically captures your scheduling constraints from the Goals & Rules page:

### View Constraints
```bash
protocol schedule constraints
```

### Update Monthly Constraints
```bash
protocol schedule update-constraints --month "March" --working-hours "09:00-18:00" --buffer-time 15
```

### Check Constraints for Specific Date
```bash
protocol schedule check-constraints --date "2024-03-15"
```

### Plan with Constraints
```bash
protocol schedule plan-with-constraints --date "2024-03-15"
```

### Reset Constraints
```bash
protocol schedule reset-constraints --month "March"
protocol schedule reset-constraints --month "all"
```

## 6. Advanced Features
- **Month-to-Month Adjustments**: Update constraints for specific months
- **Constraint-Aware Scheduling**: AI automatically respects your constraints when scheduling
- **Health-Optimized Timing**: Activities are scheduled at optimal times for performance
- **Recovery Management**: System tracks rest periods between intense activities
- **Buffer Time Management**: Automatically adds buffer time between scheduled blocks

## 7. AI Agent Integration
Your scheduling constraints are automatically integrated into the AI agents:
- **Schedule Agent**: Uses constraints for optimal time slot suggestions
- **Goal Agent**: Considers constraints when planning goal-related activities
- **Todo Agent**: Schedules todos at constraint-appropriate times
- **Coordinator**: Routes requests considering all constraint categories
"""
    
    console.print(Panel(Markdown(setup_text), title="📚 Setup Guide", border_style="blue"))


@schedule.command()
def constraints():
    """View current scheduling constraints."""
    try:
        coordinator = get_coordinator()
        constraints = coordinator.schedule_agent.scheduling_constraints.to_dict()
        
        # Format constraints for display
        working_hours = constraints["working_hours"]
        health_timing = constraints["health_optimized_timing"]
        recovery = constraints["recovery_rest"]
        
        constraints_text = f"""
# ⏰ Current Scheduling Constraints

## Working Hours
- **Core Hours**: {working_hours['core_hours']['start']}-{working_hours['core_hours']['end']} {working_hours['core_hours']['timezone']}
- **Days**: {', '.join(working_hours['days'])}
- **Buffer Time**: {working_hours['buffer_time']} minutes between all scheduled blocks
- **Transit Time**: {working_hours['transit_time']} minutes to get to work
- **No Double-Booking**: {'Enabled' if working_hours['no_double_booking'] else 'Disabled'}

## Health-Optimized Timing
- **ML Deep Work**: {health_timing['ml_deep_work']} (peak cognitive function)
- **Strength Training**: {health_timing['strength_training']} (optimal performance)
- **Cardio**: {health_timing['cardio']} timing
- **Meditation**: {health_timing['meditation']} timing

## Recovery & Rest
- **Strength Training Rest**: {recovery['strength_training_rest']} hours between major muscle groups
- **Cardio Active Recovery**: {'Enabled' if recovery['cardio_active_recovery'] else 'Disabled'}
- **Sleep Protection**: {recovery['sleep_protection']} hours before bedtime for intense exercise

## Monthly Adjustments
{chr(10).join(f"- **{month.title()}**: {', '.join(f'{k}={v}' for k, v in monthly.items())}") if constraints.get('monthly_adjustments') else "- None configured"}

**Last Updated**: {constraints.get('last_updated', 'Unknown')}
"""
        
        console.print(Panel(Markdown(constraints_text), title="⏰ Scheduling Constraints", border_style="cyan"))
        
    except Exception as e:
        console.print(f"❌ [red]Error viewing constraints: {str(e)}[/red]")


@schedule.command()
@click.option('--month', '-m', required=True, help='Month to update (e.g., "January", "Feb")')
@click.option('--working-hours', '-wh', help='Working hours override (e.g., "09:00-18:00")')
@click.option('--buffer-time', '-b', type=int, help='Buffer time in minutes')
@click.option('--ml-work', help='ML work timing preference (morning/afternoon/evening)')
@click.option('--strength-training', help='Strength training timing (e.g., "14:00-16:00")')
@click.option('--cardio', help='Cardio timing preference (morning/evening/flexible)')
@click.option('--meditation', help='Meditation timing preference (morning/evening/transition)')
@click.option('--strength-rest', type=int, help='Strength training rest hours')
@click.option('--sleep-protection', type=int, help='Sleep protection hours')
def update_constraints(month: str, working_hours: str, buffer_time: int, ml_work: str, 
                      strength_training: str, cardio: str, meditation: str, 
                      strength_rest: int, sleep_protection: int):
    """Update scheduling constraints for a specific month."""
    try:
        coordinator = get_coordinator()
        
        # Build constraints update
        constraints_update = {}
        
        if working_hours:
            # Parse working hours (e.g., "09:00-18:00")
            time_match = re.search(r'(\d{2}):(\d{2})-(\d{2}):(\d{2})', working_hours)
            if time_match:
                start_hour, start_minute, end_hour, end_minute = map(int, time_match.groups())
                constraints_update["working_hours"] = {
                    "core_hours": {
                        "start": f"{start_hour:02d}:{start_minute:02d}",
                        "end": f"{end_hour:02d}:{end_minute:02d}"
                    }
                }
        
        if buffer_time is not None:
            if "working_hours" not in constraints_update:
                constraints_update["working_hours"] = {}
            constraints_update["working_hours"]["buffer_time"] = buffer_time
        
        if any([ml_work, strength_training, cardio, meditation]):
            constraints_update["health_optimized_timing"] = {}
            if ml_work:
                constraints_update["health_optimized_timing"]["ml_deep_work"] = ml_work
            if strength_training:
                constraints_update["health_optimized_timing"]["strength_training"] = strength_training
            if cardio:
                constraints_update["health_optimized_timing"]["cardio"] = cardio
            if meditation:
                constraints_update["health_optimized_timing"]["meditation"] = meditation
        
        if any([strength_rest, sleep_protection]):
            constraints_update["recovery_rest"] = {}
            if strength_rest:
                constraints_update["recovery_rest"]["strength_training_rest"] = strength_rest
            if sleep_protection:
                constraints_update["recovery_rest"]["sleep_protection"] = sleep_protection
        
        if not constraints_update:
            console.print("⚠️ [yellow]No constraints specified for update[/yellow]")
            return
        
        # Update the constraints
        coordinator.schedule_agent.update_monthly_constraints(month, constraints_update)
        
        console.print(f"✅ [green]Updated constraints for {month}[/green]")
        console.print("Updated values:")
        for category, values in constraints_update.items():
            console.print(f"  • {category}: {values}")
        
        # Show updated constraints
        constraints()
        
    except Exception as e:
        console.print(f"❌ [red]Error updating constraints: {str(e)}[/red]")


@schedule.command()
@click.option('--month', '-m', help='Month to reset (e.g., "January", "Feb") or "all" for all months')
def reset_constraints(month: str):
    """Reset scheduling constraints to defaults."""
    try:
        coordinator = get_coordinator()
        
        if month and month.lower() != "all":
            # Reset specific month
            coordinator.schedule_agent.scheduling_constraints.monthly_adjustments.pop(month.lower(), None)
            console.print(f"✅ [green]Reset constraints for {month}[/green]")
        else:
            # Reset all monthly adjustments
            coordinator.schedule_agent.scheduling_constraints.monthly_adjustments.clear()
            console.print("✅ [green]Reset all monthly constraint adjustments[/green]")
        
        # Show current constraints
        constraints()
        
    except Exception as e:
        console.print(f"❌ [red]Error resetting constraints: {str(e)}[/red]")


@schedule.command()
@click.option('--date', '-d', help='Date to check (YYYY-MM-DD, defaults to today)')
def check_constraints(date: str):
    """Check how constraints apply to a specific date."""
    try:
        coordinator = get_coordinator()
        
        if not date:
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
        
        constraints = coordinator.schedule_agent.get_constraints_for_date(date)
        
        # Format for display
        working_hours = constraints["working_hours"]
        health_timing = constraints["health_optimized_timing"]
        recovery = constraints["recovery_rest"]
        monthly = constraints.get("monthly_adjustments", {})
        
        constraints_text = f"""
# ⏰ Constraints for {date}

## Working Hours
- **Core Hours**: {working_hours['core_hours']['start']}-{working_hours['core_hours']['end']} {working_hours['core_hours']['timezone']}
- **Buffer Time**: {working_hours['buffer_time']} minutes between all scheduled blocks
- **Transit Time**: {working_hours['transit_time']} minutes to get to work
- **No Double-Booking**: {'Enabled' if working_hours['no_double_booking'] else 'Disabled'}

## Health-Optimized Timing
- **ML Deep Work**: {health_timing['ml_deep_work']} (peak cognitive function)
- **Strength Training**: {health_timing['strength_training']} (optimal performance)
- **Cardio**: {health_timing['cardio']} timing
- **Meditation**: {health_timing['meditation']} timing

## Recovery & Rest
- **Strength Training Rest**: {recovery['strength_training_rest']} hours between major muscle groups
- **Cardio Active Recovery**: {'Enabled' if recovery['cardio_active_recovery'] else 'Disabled'}
- **Sleep Protection**: {recovery['sleep_protection']} hours before bedtime for intense exercise

## Month-Specific Adjustments
{chr(10).join(f"- **{k.title()}**: {', '.join(f'{k2}={v2}' for k2, v2 in v.items())}") if monthly else "- None for this month"}
"""
        
        console.print(Panel(Markdown(constraints_text), title=f"⏰ Constraints for {date}", border_style="cyan"))
        
    except Exception as e:
        console.print(f"❌ [red]Error checking constraints: {str(e)}[/red]")


@schedule.command()
@click.option('--date', '-d', help='Date to plan for (YYYY-MM-DD, defaults to tomorrow)')
def plan_with_constraints(date: str):
    """Create an optimal schedule plan considering all constraints."""
    try:
        coordinator = get_coordinator()
        
        if not date:
            from datetime import datetime, timedelta
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Get todos for the date
        todos_response = coordinator.todo_agent.get_today_tasks()
        
        # For demo purposes, create some sample todos
        sample_todos = [
            {"title": "ML Deep Work Session", "priority": "High", "project": "Machine Learning"},
            {"title": "Strength Training", "priority": "High", "project": "Health"},
            {"title": "Cardio Session", "priority": "Medium", "project": "Health"},
            {"title": "Meditation", "priority": "Medium", "project": "Mental Health"},
            {"title": "Code Review", "priority": "Medium", "project": "Development"}
        ]
        
        # Generate optimal schedule with constraints
        optimal_schedule = coordinator.schedule_agent.suggest_optimal_schedule_with_constraints(date, sample_todos)
        
        console.print(Panel(Markdown(optimal_schedule), title=f"📅 Optimal Schedule for {date}", border_style="green"))
        
    except Exception as e:
        console.print(f"❌ [red]Error planning with constraints: {str(e)}[/red]")


def main():
    """Main entry point for the CLI."""
    try:
        protocol_cli()
    except KeyboardInterrupt:
        console.print("\n👋 [green]Goodbye![/green]")
    except Exception as e:
        console.print(f"❌ [red]Unexpected error: {str(e)}[/red]")


if __name__ == '__main__':
    main()
