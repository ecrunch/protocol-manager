"""
Goal-specific prompts and templates for the Goal Agent.
"""

GOAL_PROMPT_TEMPLATES = {
    "create_goal": """
Based on the user's input, help them create a SMART goal:

User Request: {user_input}

Ensure the goal is:
- Specific: Clear and well-defined
- Measurable: Has quantifiable success criteria  
- Achievable: Realistic given the user's context
- Relevant: Aligned with their values/priorities
- Time-bound: Has a clear deadline

Ask clarifying questions if needed to make the goal SMART.
""",

    "break_down_goal": """
Help break down this large goal into smaller, actionable milestones:

Goal: {goal_description}

Provide:
1. 3-5 major milestones leading to the goal
2. Specific actions for each milestone  
3. Suggested timeline for each milestone
4. Success criteria for each milestone

Make sure each milestone is achievable within 1-4 weeks.
""",

    "progress_review": """
Analyze the progress on this goal and provide insights:

Goal: {goal_title}
Current Progress: {progress_percentage}%
Target Date: {target_date}
Status: {status}

Provide:
1. Progress assessment (on track/behind/ahead)
2. Specific next actions to maintain/improve progress
3. Any suggested adjustments to timeline or approach
4. Motivational insights or celebration of achievements
""",

    "goal_prioritization": """
Help prioritize these goals based on importance and urgency:

Goals: {goals_list}

Provide:
1. Recommended priority order with rationale
2. Identify any conflicts or dependencies
3. Suggest which goals to focus on first
4. Any goals that might need to be deferred
5. Timeline recommendations for each goal
"""
}
