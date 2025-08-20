"""
Protocol Manager - LangChain AI Agent Integration

A comprehensive productivity management system that combines a Notion Python client
with LangChain-powered AI agents for intelligent goal, schedule, and todo management.
"""

__version__ = "0.1.0"
__author__ = "Protocol Home Team"
__email__ = "contact@protocolhome.com"

from .agents import (
    BaseProtocolAgent,
    GoalAgent,
    TodoAgent,
    ProtocolCoordinator,
)

from .tools import (
    BaseNotionTool,
    CreateGoalTool,
    UpdateGoalTool,
    GetGoalsTool,
    CreateTodoTool,
    UpdateTodoTool,
    GetTodosTool,
)

from .notion_client import NotionClient

__all__ = [
    # Core agents
    "BaseProtocolAgent",
    "GoalAgent", 
    "TodoAgent",
    "ProtocolCoordinator",
    
    # Tools
    "BaseNotionTool",
    "CreateGoalTool",
    "UpdateGoalTool", 
    "GetGoalsTool",
    "CreateTodoTool",
    "UpdateTodoTool",
    "GetTodosTool",
    
    # Notion client
    "NotionClient",
]
