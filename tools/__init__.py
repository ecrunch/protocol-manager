"""
LangChain tools for Notion operations.

This module contains specialized tools that wrap the Notion client functionality
to enable LangChain agents to interact with Notion databases and pages.
"""

from .base_tool import BaseNotionTool
from .goal_tools import (
    CreateGoalTool,
    UpdateGoalTool,
    GetGoalsTool,
    ArchiveGoalTool,
    GetGoalProgressTool,
)
# Schedule tools - TODO: Implement these
# from .schedule_tools import (
#     CreateEventTool,
#     UpdateEventTool,
#     GetScheduleTool,
#     FindFreeTimeTool,
#     ScheduleTaskTool,
# )
from .todo_tools import (
    CreateTodoTool,
    UpdateTodoTool,
    GetTodosTool,
    CompleteTodoTool,
    PrioritizeTodosTool,
)

__all__ = [
    "BaseNotionTool",
    # Goal tools
    "CreateGoalTool",
    "UpdateGoalTool", 
    "GetGoalsTool",
    "ArchiveGoalTool",
    "GetGoalProgressTool",
    # Schedule tools - TODO: Add when implemented
    # "CreateEventTool",
    # "UpdateEventTool",
    # "GetScheduleTool",
    # "FindFreeTimeTool",
    # "ScheduleTaskTool",
    # Todo tools
    "CreateTodoTool",
    "UpdateTodoTool",
    "GetTodosTool",
    "CompleteTodoTool",
    "PrioritizeTodosTool",
]
