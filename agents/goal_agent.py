"""
Goal management agent for Protocol Home.

This agent specializes in goal setting, tracking, and achievement management
using SMART goal principles and productivity frameworks.
"""

from typing import List, Optional
from langchain.tools import BaseTool
from .base_agent import BaseProtocolAgent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.goal_tools import (
    CreateGoalTool,
    UpdateGoalTool,
    GetGoalsTool,
    ArchiveGoalTool,
    GetGoalProgressTool,
)
from prompts.system_prompts import GOAL_AGENT_PROMPT


class GoalAgent(BaseProtocolAgent):
    """Agent specialized in goal setting and management."""
    
    def __init__(
        self,
        notion_client,
        goals_database_id: str,
        openai_api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Goal Agent.
        
        Args:
            notion_client: Initialized Notion client instance
            goals_database_id: The ID of the Goals database in Notion
            openai_api_key: OpenAI API key
            **kwargs: Additional arguments for BaseProtocolAgent
        """
        self.goals_database_id = goals_database_id
        super().__init__(notion_client, openai_api_key, **kwargs)
        
    def _setup_tools(self) -> List[BaseTool]:
        """Setup goal management tools."""
        return [
            CreateGoalTool(
                notion_client=self.notion,
                goals_database_id=self.goals_database_id
            ),
            UpdateGoalTool(notion_client=self.notion),
            GetGoalsTool(
                notion_client=self.notion,
                goals_database_id=self.goals_database_id
            ),
            ArchiveGoalTool(notion_client=self.notion),
            GetGoalProgressTool(
                notion_client=self.notion,
                goals_database_id=self.goals_database_id
            ),
        ]
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the goal agent."""
        return GOAL_AGENT_PROMPT
        
    def create_goal(
        self,
        title: str,
        description: str,
        target_date: Optional[str] = None,
        priority: str = "Medium",
        category: str = "Personal"
    ) -> str:
        """
        Create a new goal using natural language processing.
        
        Args:
            title: Goal title
            description: Goal description
            target_date: Target completion date (YYYY-MM-DD)
            priority: Priority level (High/Medium/Low)
            category: Goal category
            
        Returns:
            Result message from goal creation
        """
        request = f"Create a goal titled '{title}' with description '{description}'"
        if target_date:
            request += f" with target date {target_date}"
        if priority != "Medium":
            request += f" with {priority} priority"
        if category != "Personal":
            request += f" in {category} category"
            
        return self.process(request)
        
    def get_goals_summary(self, category: Optional[str] = None) -> str:
        """
        Get a summary of goals with optional category filter.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            Goals summary and analysis
        """
        if category:
            request = f"Show me a summary of my {category} goals"
        else:
            request = "Show me a summary of all my goals"
            
        return self.process(request)
        
    def track_progress(self, goal_id: Optional[str] = None) -> str:
        """
        Track progress for a specific goal or all goals.
        
        Args:
            goal_id: Optional specific goal ID to track
            
        Returns:
            Progress tracking analysis
        """
        if goal_id:
            request = f"Track progress for goal {goal_id}"
        else:
            request = "Show me progress across all my goals"
            
        return self.process(request)
        
    def suggest_goal_breakdown(self, goal_description: str) -> str:
        """
        Suggest how to break down a large goal into smaller milestones.
        
        Args:
            goal_description: Description of the goal to break down
            
        Returns:
            Suggested goal breakdown and milestones
        """
        request = f"Help me break down this goal into smaller milestones: {goal_description}"
        return self.process(request)
        
    def review_goals(self, timeframe: str = "monthly") -> str:
        """
        Conduct a goal review and provide insights.
        
        Args:
            timeframe: Review timeframe (weekly/monthly/quarterly)
            
        Returns:
            Goal review analysis and recommendations
        """
        request = f"Conduct a {timeframe} review of my goals and provide insights"
        return self.process(request)
