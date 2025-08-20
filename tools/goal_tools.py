"""
LangChain tools for goal management in Notion.

This module contains specialized tools for creating, updating, and managing
goals in the Protocol Home system.
"""

from typing import Type, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import tool
from .base_tool import BaseNotionTool


class CreateGoalInput(BaseModel):
    """Input schema for creating a goal."""
    title: str = Field(description="Goal title")
    description: str = Field(description="Detailed goal description")
    target_date: Optional[str] = Field(description="Target completion date (YYYY-MM-DD)")
    priority: str = Field(description="Priority level (High/Medium/Low)", default="Medium")
    category: str = Field(description="Goal category (Personal/Professional/Health/etc.)", default="Personal")


class CreateGoalTool(BaseNotionTool):
    """Tool for creating goals in Notion."""
    
    name: str = "create_goal"
    description: str = "Create a new goal in the goals database with title, description, target date, priority, and category"
    args_schema: Type[BaseModel] = CreateGoalInput
    goals_database_id: str = Field(description="The ID of the goals database")
    
    def __init__(self, notion_client, goals_database_id: str, **kwargs):
        super().__init__(notion_client=notion_client, goals_database_id=goals_database_id, **kwargs)
    
    def _run(self, title: str, description: str, target_date: Optional[str] = None, 
             priority: str = "Medium", category: str = "Personal") -> str:
        """Create a goal in Notion and return the page ID."""
        try:
            # Prepare properties for the goal
            properties = {
                "Name": {"title": self._format_notion_title(title)},
                "Description": {"rich_text": self._format_notion_rich_text(description)},
                "Priority": {"select": self._format_notion_select(priority)},
                "Category": {"select": self._format_notion_select(category)},
                "Status": {"select": self._format_notion_select("Not Started")},
                "Progress": {"number": 0},
            }
            
            # Add target date if provided
            if target_date:
                date_obj = self._format_notion_date(target_date)
                if date_obj:
                    properties["Target Date"] = {"date": date_obj}
            
            # Create the goal page
            goal_page = self.notion_client.pages.create(
                parent={"database_id": self.goals_database_id},
                properties=properties
            )
            
            page_id = goal_page.id
            return f"✅ Created goal '{title}' successfully! Goal ID: {page_id}"
            
        except Exception as e:
            return self._handle_notion_error(e, "goal creation")


class UpdateGoalInput(BaseModel):
    """Input schema for updating a goal."""
    goal_id: str = Field(description="The ID of the goal to update")
    title: Optional[str] = Field(description="New goal title", default=None)
    description: Optional[str] = Field(description="New goal description", default=None)
    target_date: Optional[str] = Field(description="New target date (YYYY-MM-DD)", default=None)
    priority: Optional[str] = Field(description="New priority (High/Medium/Low)", default=None)
    category: Optional[str] = Field(description="New category", default=None)
    status: Optional[str] = Field(description="New status (Not Started/In Progress/Completed/On Hold)", default=None)
    progress: Optional[int] = Field(description="Progress percentage (0-100)", default=None)


class UpdateGoalTool(BaseNotionTool):
    """Tool for updating existing goals in Notion."""
    
    name: str = "update_goal"
    description: str = "Update an existing goal's properties like title, description, status, progress, etc."
    args_schema: Type[BaseModel] = UpdateGoalInput
    
    def _run(self, goal_id: str, title: Optional[str] = None, description: Optional[str] = None,
             target_date: Optional[str] = None, priority: Optional[str] = None, 
             category: Optional[str] = None, status: Optional[str] = None,
             progress: Optional[int] = None) -> str:
        """Update a goal in Notion."""
        try:
            # Build properties dict with only the fields to update
            properties = {}
            
            if title:
                properties["Name"] = {"title": self._format_notion_title(title)}
            if description:
                properties["Description"] = {"rich_text": self._format_notion_rich_text(description)}
            if priority:
                properties["Priority"] = {"select": self._format_notion_select(priority)}
            if category:
                properties["Category"] = {"select": self._format_notion_select(category)}
            if status:
                properties["Status"] = {"select": self._format_notion_select(status)}
            if progress is not None:
                properties["Progress"] = {"number": max(0, min(100, progress))}
            if target_date:
                date_obj = self._format_notion_date(target_date)
                if date_obj:
                    properties["Target Date"] = {"date": date_obj}
            
            if not properties:
                return "❌ No properties specified for update. Please provide at least one field to update."
            
            # Update the goal page
            self.notion_client.pages.update(
                page_id=goal_id,
                properties=properties
            )
            
            updated_fields = list(properties.keys())
            return f"✅ Updated goal successfully! Updated fields: {', '.join(updated_fields)}"
            
        except Exception as e:
            return self._handle_notion_error(e, "goal update")


class GetGoalsInput(BaseModel):
    """Input schema for retrieving goals."""
    status: Optional[str] = Field(description="Filter by status (Not Started/In Progress/Completed/On Hold)", default=None)
    category: Optional[str] = Field(description="Filter by category", default=None)
    priority: Optional[str] = Field(description="Filter by priority (High/Medium/Low)", default=None)
    limit: int = Field(description="Maximum number of goals to return", default=10)


class GetGoalsTool(BaseNotionTool):
    """Tool for retrieving goals from Notion with optional filters."""
    
    name: str = "get_goals"
    description: str = "Retrieve goals from the database with optional filters for status, category, priority"
    args_schema: Type[BaseModel] = GetGoalsInput
    goals_database_id: str = Field(description="The ID of the goals database")
    
    def __init__(self, notion_client, goals_database_id: str, **kwargs):
        super().__init__(notion_client=notion_client, goals_database_id=goals_database_id, **kwargs)
    
    def _run(self, status: Optional[str] = None, category: Optional[str] = None,
             priority: Optional[str] = None, limit: int = 10) -> str:
        """Retrieve goals with optional filters."""
        try:
            # Build filter conditions
            filter_conditions = []
            
            if status:
                filter_conditions.append({
                    "property": "Status",
                    "select": {"equals": status}
                })
            
            if category:
                filter_conditions.append({
                    "property": "Category", 
                    "select": {"equals": category}
                })
                
            if priority:
                filter_conditions.append({
                    "property": "Priority",
                    "select": {"equals": priority}
                })
            
            # Build query
            query = {
                "database_id": self.goals_database_id,
                "page_size": min(limit, 100),
                "sorts": [
                    {
                        "property": "Priority",
                        "direction": "ascending"  # High priority first
                    }
                ]
            }
            
            # Add filters if any
            if filter_conditions:
                if len(filter_conditions) == 1:
                    query["filter"] = filter_conditions[0]
                else:
                    query["filter"] = {
                        "and": filter_conditions
                    }
            
            # Query the database
            response = self.notion_client.databases.query(**query)
            goals = response.get("results", [])
            
            if not goals:
                return "📭 No goals found matching your criteria."
            
            # Format the results
            result_lines = [f"📋 Found {len(goals)} goal(s):\n"]
            
            for i, goal in enumerate(goals, 1):
                title = self._extract_page_title(goal)
                status_val = self._extract_property_value(goal, "Status") or "Unknown"
                priority_val = self._extract_property_value(goal, "Priority") or "Unknown"
                category_val = self._extract_property_value(goal, "Category") or "Unknown"
                progress_val = self._extract_property_value(goal, "Progress") or 0
                target_date = self._extract_property_value(goal, "Target Date") or "No date set"
                
                result_lines.append(
                    f"{i}. **{title}**\n"
                    f"   Status: {status_val} | Priority: {priority_val} | Category: {category_val}\n"
                    f"   Progress: {progress_val}% | Target: {target_date}\n"
                    f"   ID: {goal['id']}\n"
                )
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return self._handle_notion_error(e, "goal retrieval")


class ArchiveGoalInput(BaseModel):
    """Input schema for archiving a goal."""
    goal_id: str = Field(description="The ID of the goal to archive")


class ArchiveGoalTool(BaseNotionTool):
    """Tool for archiving completed goals."""
    
    name: str = "archive_goal"
    description: str = "Archive a goal by setting its status to Completed and moving it to archive"
    args_schema: Type[BaseModel] = ArchiveGoalInput
    
    def _run(self, goal_id: str) -> str:
        """Archive a goal."""
        try:
            # Update the goal to completed status
            self.notion_client.pages.update(
                page_id=goal_id,
                properties={
                    "Status": {"select": self._format_notion_select("Completed")},
                    "Progress": {"number": 100},
                    "Archived": {"checkbox": True}
                }
            )
            
            return f"🗃️ Goal archived successfully! Goal ID: {goal_id}"
            
        except Exception as e:
            return self._handle_notion_error(e, "goal archiving")


class GetGoalProgressInput(BaseModel):
    """Input schema for getting goal progress."""
    goal_id: Optional[str] = Field(description="Specific goal ID to get progress for", default=None)
    category: Optional[str] = Field(description="Category to analyze progress for", default=None)


class GetGoalProgressTool(BaseNotionTool):
    """Tool for calculating and retrieving goal progress metrics."""
    
    name: str = "get_goal_progress"
    description: str = "Get progress metrics for specific goals or goal categories"
    args_schema: Type[BaseModel] = GetGoalProgressInput
    goals_database_id: str = Field(description="The ID of the goals database")
    
    def __init__(self, notion_client, goals_database_id: str, **kwargs):
        super().__init__(notion_client=notion_client, goals_database_id=goals_database_id, **kwargs)
    
    def _run(self, goal_id: Optional[str] = None, category: Optional[str] = None) -> str:
        """Calculate goal progress metrics."""
        try:
            if goal_id:
                # Get specific goal progress
                goal = self.notion_client.pages.retrieve(page_id=goal_id)
                title = self._extract_page_title(goal)
                progress = self._extract_property_value(goal, "Progress") or 0
                status = self._extract_property_value(goal, "Status") or "Unknown"
                
                return f"📊 Goal Progress for '{title}':\nProgress: {progress}%\nStatus: {status}"
            
            else:
                # Get overall progress statistics
                query = {"database_id": self.goals_database_id}
                
                if category:
                    query["filter"] = {
                        "property": "Category",
                        "select": {"equals": category}
                    }
                
                response = self.notion_client.databases.query(**query)
                goals = response.get("results", [])
                
                if not goals:
                    return "📭 No goals found for progress analysis."
                
                # Calculate statistics
                total_goals = len(goals)
                completed = sum(1 for g in goals if self._extract_property_value(g, "Status") == "Completed")
                in_progress = sum(1 for g in goals if self._extract_property_value(g, "Status") == "In Progress")
                not_started = sum(1 for g in goals if self._extract_property_value(g, "Status") == "Not Started")
                
                total_progress = sum(self._extract_property_value(g, "Progress") or 0 for g in goals)
                avg_progress = total_progress / total_goals if total_goals > 0 else 0
                
                category_text = f" ({category})" if category else ""
                
                return (
                    f"📊 Goal Progress Summary{category_text}:\n\n"
                    f"Total Goals: {total_goals}\n"
                    f"Completed: {completed} ({completed/total_goals*100:.1f}%)\n"
                    f"In Progress: {in_progress} ({in_progress/total_goals*100:.1f}%)\n"
                    f"Not Started: {not_started} ({not_started/total_goals*100:.1f}%)\n"
                    f"Average Progress: {avg_progress:.1f}%"
                )
                
        except Exception as e:
            return self._handle_notion_error(e, "goal progress analysis")
