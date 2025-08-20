"""
Todo/task management agent for Protocol Home.

This agent specializes in task creation, prioritization, completion tracking,
and workflow optimization using productivity frameworks.
"""

from typing import List, Optional
from langchain.tools import BaseTool
from .base_agent import BaseProtocolAgent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.todo_tools import (
    CreateTodoTool,
    UpdateTodoTool,
    GetTodosTool,
    CompleteTodoTool,
    PrioritizeTodosTool,
)
from prompts.system_prompts import TODO_AGENT_PROMPT


class TodoAgent(BaseProtocolAgent):
    """Agent specialized in todo and task management."""
    
    def __init__(
        self,
        notion_client,
        todos_database_id: str,
        openai_api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Todo Agent.
        
        Args:
            notion_client: Initialized Notion client instance
            todos_database_id: The ID of the Todos database in Notion
            openai_api_key: OpenAI API key
            **kwargs: Additional arguments for BaseProtocolAgent
        """
        self.todos_database_id = todos_database_id
        super().__init__(notion_client, openai_api_key, **kwargs)
        
    def _setup_tools(self) -> List[BaseTool]:
        """Setup todo management tools."""
        return [
            CreateTodoTool(
                notion_client=self.notion,
                todos_database_id=self.todos_database_id
            ),
            UpdateTodoTool(notion_client=self.notion),
            GetTodosTool(
                notion_client=self.notion,
                todos_database_id=self.todos_database_id
            ),
            CompleteTodoTool(notion_client=self.notion),
            PrioritizeTodosTool(
                notion_client=self.notion,
                todos_database_id=self.todos_database_id
            ),
        ]
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the todo agent."""
        return TODO_AGENT_PROMPT
        
    def add_task(
        self,
        title: str,
        priority: str = "Medium",
        project: Optional[str] = None,
        due_date: Optional[str] = None,
        time_estimate: Optional[int] = None
    ) -> str:
        """
        Add a new task using natural language processing.
        
        Args:
            title: Task title/description
            priority: Priority level (Urgent/High/Medium/Low)
            project: Project or category
            due_date: Due date (YYYY-MM-DD)
            time_estimate: Estimated time in minutes
            
        Returns:
            Result message from task creation
        """
        request = f"Create a task: {title}"
        if priority != "Medium":
            request += f" with {priority} priority"
        if project:
            request += f" for project {project}"
        if due_date:
            request += f" due on {due_date}"
        if time_estimate:
            request += f" estimated to take {time_estimate} minutes"
            
        return self.process(request)
        
    def get_today_tasks(self) -> str:
        """
        Get today's tasks and priorities.
        
        Returns:
            Today's task list with priorities
        """
        return self.process("Show me my tasks for today")
        
    def get_project_tasks(self, project: str) -> str:
        """
        Get all tasks for a specific project.
        
        Args:
            project: Project name
            
        Returns:
            Project task list
        """
        return self.process(f"Show me all tasks for the {project} project")
        
    def prioritize_tasks(self, method: str = "eisenhower", project: Optional[str] = None) -> str:
        """
        Prioritize tasks using a specific framework.
        
        Args:
            method: Prioritization method (eisenhower/moscow/abc)
            project: Optional project to focus on
            
        Returns:
            Prioritization analysis and recommendations
        """
        request = f"Prioritize my tasks using the {method} method"
        if project:
            request += f" for the {project} project"
            
        return self.process(request)
        
    def complete_task(self, task_description: str) -> str:
        """
        Mark a task as completed using natural language.
        
        Args:
            task_description: Description to identify the task
            
        Returns:
            Completion confirmation
        """
        return self.process(f"Mark this task as completed: {task_description}")
        
    def break_down_task(self, task_description: str) -> str:
        """
        Break down a complex task into smaller subtasks.
        
        Args:
            task_description: Description of the task to break down
            
        Returns:
            Suggested task breakdown
        """
        return self.process(f"Help me break down this task into smaller steps: {task_description}")
        
    def get_productivity_insights(self) -> str:
        """
        Get productivity insights and patterns.
        
        Returns:
            Productivity analysis and recommendations
        """
        return self.process("Give me insights about my task completion patterns and productivity")
        
    def suggest_time_blocking(self) -> str:
        """
        Suggest time blocking based on current tasks.
        
        Returns:
            Time blocking suggestions
        """
        return self.process("Suggest a time blocking schedule based on my current tasks")
        
    def get_overdue_tasks(self) -> str:
        """
        Get list of overdue tasks.
        
        Returns:
            Overdue task list with recommendations
        """
        return self.process("Show me my overdue tasks and suggest how to handle them")
        
    def weekly_review(self) -> str:
        """
        Conduct a weekly task review.
        
        Returns:
            Weekly productivity review and insights
        """
        return self.process("Conduct a weekly review of my tasks and productivity")
