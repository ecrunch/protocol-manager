"""
Schedule-specific prompts and templates for the Schedule Agent.
"""

SCHEDULE_PROMPT_TEMPLATES = {
    "create_event": """
Help create a well-structured calendar event:

User Request: {user_input}

Ensure the event has:
- Clear title and description
- Specific date and time
- Appropriate duration
- Location or context
- Any necessary preparation time

Ask for missing details if needed.
""",

    "time_optimization": """
Analyze this schedule and suggest optimizations:

Schedule: {schedule_data}
Goals: {user_goals}
Tasks: {pending_tasks}

Provide:
1. Time allocation efficiency analysis
2. Gaps that could be used productively
3. Conflicts or over-scheduling issues
4. Better sequencing of activities
5. Work-life balance assessment
""",

    "routine_planning": """
Help establish a sustainable routine:

User Requirements: {requirements}
Current Schedule: {current_schedule}
Goals: {goals}

Provide:
1. Suggested daily/weekly routine structure
2. Time blocks for different activity types
3. Flexibility buffers for unexpected events
4. Energy management considerations
5. Habit stacking opportunities
""",

    "conflict_resolution": """
Resolve this scheduling conflict:

Conflicting Events: {conflicts}
User Priorities: {priorities}
Available Alternatives: {alternatives}

Provide:
1. Assessment of conflict severity
2. Recommended resolution approach
3. Alternative time slots
4. Impact analysis of each option
5. Prevention strategies for future conflicts
"""
}
