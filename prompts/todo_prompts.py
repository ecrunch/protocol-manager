"""
Todo-specific prompts and templates for the Todo Agent.
"""

TODO_PROMPT_TEMPLATES = {
    "create_task": """
Help create a well-structured task based on this input:

User Request: {user_input}

Ensure the task:
- Starts with an action verb
- Has a clear, specific outcome
- Includes estimated time if possible
- Has appropriate priority level
- Is assigned to the right project/context

Ask clarifying questions if the task is too vague.
""",

    "break_down_task": """
Break down this complex task into smaller, actionable subtasks:

Task: {task_description}

Provide:
1. 3-7 specific subtasks in logical order
2. Time estimate for each subtask
3. Any dependencies between subtasks
4. Suggested contexts/locations for each
5. Priority order for completing the subtasks
""",

    "prioritize_tasks": """
Analyze and prioritize these tasks using the {method} method:

Tasks: {tasks_list}

Provide:
1. Tasks organized by priority categories
2. Rationale for each categorization
3. Recommended order of execution
4. Any tasks that could be eliminated or delegated
5. Time management suggestions
""",

    "productivity_review": """
Analyze the task completion patterns and provide insights:

Completed Tasks: {completed_tasks}
Pending Tasks: {pending_tasks}
Overdue Tasks: {overdue_tasks}

Provide:
1. Productivity trends and patterns
2. Areas of strength and improvement
3. Suggestions for better task management
4. Workflow optimization recommendations
5. Time estimation accuracy feedback
""",

    "time_blocking": """
Suggest a time blocking schedule for these tasks:

Tasks: {tasks_list}
Available Time: {time_blocks}
User Preferences: {preferences}

Provide:
1. Optimal time allocation for each task
2. Consideration of energy levels and focus
3. Buffer time recommendations
4. Batch similar tasks together
5. Break and rest period suggestions
"""
}
