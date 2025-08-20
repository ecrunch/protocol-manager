"""
Agent prompts and templates for Protocol Home management.

This module contains system prompts, templates, and prompt management utilities
for the various LangChain agents.
"""

from .system_prompts import (
    BASE_SYSTEM_PROMPT,
    GOAL_AGENT_PROMPT,
    SCHEDULE_AGENT_PROMPT,
    TODO_AGENT_PROMPT,
    COORDINATOR_PROMPT,
)
from .goal_prompts import GOAL_PROMPT_TEMPLATES
from .schedule_prompts import SCHEDULE_PROMPT_TEMPLATES
from .todo_prompts import TODO_PROMPT_TEMPLATES

__all__ = [
    "BASE_SYSTEM_PROMPT",
    "GOAL_AGENT_PROMPT",
    "SCHEDULE_AGENT_PROMPT", 
    "TODO_AGENT_PROMPT",
    "COORDINATOR_PROMPT",
    "GOAL_PROMPT_TEMPLATES",
    "SCHEDULE_PROMPT_TEMPLATES",
    "TODO_PROMPT_TEMPLATES",
]
