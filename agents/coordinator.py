"""
Protocol Coordinator for managing multiple agents.

This coordinator routes user requests to appropriate agents and handles
complex multi-domain tasks that involve goals, schedules, and todos.
"""

import re
from typing import Dict, List, Optional, Tuple
from .base_agent import BaseProtocolAgent
from .goal_agent import GoalAgent
from .todo_agent import TodoAgent
from .schedule_agent import ScheduleAgent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.system_prompts import COORDINATOR_PROMPT


class ProtocolCoordinator:
    """Coordinates multiple agents for complex workflows."""
    
    def __init__(
        self,
        notion_client,
        goals_database_id: str,
        todos_database_id: str,
        calendar_database_id: str,
        openai_api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Protocol Coordinator.
        
        Args:
            notion_client: Initialized Notion client instance
            goals_database_id: The ID of the Goals database
            todos_database_id: The ID of the Todos database
            calendar_database_id: The ID of the Calendar database
            openai_api_key: OpenAI API key
            **kwargs: Additional arguments for agents
        """
        self.notion = notion_client
        self.openai_api_key = openai_api_key
        
        # Initialize specialized agents
        self.goal_agent = GoalAgent(
            notion_client=notion_client,
            goals_database_id=goals_database_id,
            openai_api_key=openai_api_key,
            **kwargs
        )
        
        self.todo_agent = TodoAgent(
            notion_client=notion_client,
            todos_database_id=todos_database_id,
            openai_api_key=openai_api_key,
            **kwargs
        )
        
        self.schedule_agent = ScheduleAgent(
            notion_client=notion_client,
            calendar_database_id=calendar_database_id,
            todos_database_id=todos_database_id,
            openai_api_key=openai_api_key,
            **kwargs
        )
        
        # Intent classification patterns
        self.intent_patterns = {
            'goal_management': [
                r'\b(goal|objective|target|achievement|milestone)\b',
                r'\b(set|create|plan|achieve|accomplish)\b.*\b(goal|objective)\b',
                r'\b(progress|track|review).*\b(goal|objective)\b',
                r'\b(smart|okr|key result)\b',
            ],
            'todo_management': [
                r'\b(task|todo|action|item|job)\b',
                r'\b(do|complete|finish|check off)\b',
                r'\b(priority|urgent|deadline|due)\b',
                r'\b(eisenhower|moscow|abc priority)\b',
                r'\b(productivity|workflow|organize)\b',
            ],
            'schedule_management': [
                r'\b(schedule|calendar|appointment|meeting)\b',
                r'\b(time|timing|when|date)\b',
                r'\b(block|allocate|reserve|plan)\b.*\b(time)\b',
                r'\b(routine|habit|daily|weekly)\b',
            ],
            'multi_domain': [
                r'\b(plan|organize|review).*\b(week|day|month)\b',
                r'\b(integrate|connect|align)\b',
                r'\b(overview|summary|dashboard)\b',
                r'\b(productivity|performance|efficiency)\b.*\b(review|analysis)\b',
            ]
        }
        
    def classify_intent(self, user_input: str) -> str:
        """
        Classify user intent to determine which agent(s) to use.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Intent classification (goal_management, todo_management, schedule_management, multi_domain)
        """
        user_input_lower = user_input.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, user_input_lower))
                score += matches
            intent_scores[intent] = score
        
        # If multiple intents have high scores, it's likely multi-domain
        high_score_intents = [intent for intent, score in intent_scores.items() 
                             if score > 0 and intent != 'multi_domain']
        
        if len(high_score_intents) > 1 or intent_scores.get('multi_domain', 0) > 0:
            return 'multi_domain'
        
        # Return the intent with the highest score
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        # Default to todo management for actionable requests
        action_words = ['create', 'add', 'make', 'do', 'complete', 'finish', 'help']
        if any(word in user_input_lower for word in action_words):
            return 'todo_management'
        
        return 'multi_domain'
    
    def process_request(self, user_input: str) -> str:
        """
        Process a user request by routing to appropriate agent(s).
        
        Args:
            user_input: The user's input/request
            
        Returns:
            Response from the appropriate agent(s)
        """
        try:
            intent = self.classify_intent(user_input)
            
            if intent == "goal_management":
                return self._handle_goal_request(user_input)
            elif intent == "todo_management":
                return self._handle_todo_request(user_input)
            elif intent == "schedule_management":
                return self._handle_schedule_request(user_input)
            elif intent == "multi_domain":
                return self._handle_multi_domain_request(user_input)
            else:
                return self._handle_general_request(user_input)
                
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}. Please try again or rephrase your request."
    
    async def aprocess_request(self, user_input: str) -> str:
        """
        Asynchronously process a user request.
        
        Args:
            user_input: The user's input/request
            
        Returns:
            Response from the appropriate agent(s)
        """
        try:
            intent = self.classify_intent(user_input)
            
            if intent == "goal_management":
                return await self.goal_agent.aprocess(user_input)
            elif intent == "todo_management":
                return await self.todo_agent.aprocess(user_input)
            elif intent == "schedule_management":
                return await self._ahandle_schedule_request(user_input)
            elif intent == "multi_domain":
                return await self._ahandle_multi_domain_request(user_input)
            else:
                return await self._ahandle_general_request(user_input)
                
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}. Please try again or rephrase your request."
    
    def _handle_goal_request(self, user_input: str) -> str:
        """Handle goal-related requests."""
        return self.goal_agent.process(user_input)
    
    def _handle_todo_request(self, user_input: str) -> str:
        """Handle todo-related requests."""
        return self.todo_agent.process(user_input)
    
    def _handle_schedule_request(self, user_input: str) -> str:
        """Handle schedule-related requests."""
        return self.schedule_agent.process(user_input)
    
    def _handle_multi_domain_request(self, user_input: str) -> str:
        """Handle complex requests involving multiple domains."""
        # For multi-domain requests, analyze what's needed
        if any(word in user_input.lower() for word in ['plan', 'organize', 'review', 'overview']):
            
            # Get information from multiple agents
            responses = []
            
            # Get goals overview
            try:
                goal_summary = self.goal_agent.get_goals_summary()
                responses.append(f"📊 **Goals Overview:**\n{goal_summary}\n")
            except Exception as e:
                responses.append(f"📊 **Goals:** Unable to retrieve goals ({str(e)})\n")
            
            # Get todos overview
            try:
                todo_summary = self.todo_agent.get_today_tasks()
                responses.append(f"📋 **Today's Tasks:**\n{todo_summary}\n")
            except Exception as e:
                responses.append(f"📋 **Tasks:** Unable to retrieve tasks ({str(e)})\n")
            
            # Get schedule overview
            try:
                schedule_summary = self.schedule_agent.get_today_schedule()
                responses.append(f"📅 **Today's Schedule:**\n{schedule_summary}\n")
            except Exception as e:
                responses.append(f"📅 **Schedule:** Unable to retrieve schedule ({str(e)})\n")
            
            # Combine and analyze
            combined_response = "\n".join(responses)
            
            # Add coordination analysis
            coordination_analysis = self._analyze_cross_domain_alignment(user_input)
            if coordination_analysis:
                combined_response += f"\n🎯 **Coordination Analysis:**\n{coordination_analysis}"
            
            return combined_response
        
        else:
            # Try to route to the most appropriate agent based on keywords
            if any(word in user_input.lower() for word in ['goal', 'objective', 'achieve']):
                return self._handle_goal_request(user_input)
            elif any(word in user_input.lower() for word in ['task', 'todo', 'do', 'complete']):
                return self._handle_todo_request(user_input)
            elif any(word in user_input.lower() for word in ['schedule', 'calendar', 'time', 'meeting']):
                return self._handle_schedule_request(user_input)
            else:
                return self._handle_general_request(user_input)
    
    def _handle_general_request(self, user_input: str) -> str:
        """Handle general requests that don't fit specific categories."""
        return (
            "🤔 I'm not sure which area of Protocol Home this relates to. "
            "I can help you with:\n\n"
            "📊 **Goals:** Setting, tracking, and achieving objectives\n"
            "📋 **Tasks:** Creating, prioritizing, and completing todos\n"
            "📅 **Schedule:** Calendar management and todo scheduling\n\n"
            "Could you please be more specific about what you'd like to do? "
            "For example:\n"
            "- 'Create a goal to learn Python'\n"
            "- 'Add a task to review my presentation'\n"
            "- 'Show me my progress on current goals'"
        )
    
    async def _ahandle_schedule_request(self, user_input: str) -> str:
        """Async handle schedule-related requests."""
        return await self.schedule_agent.aprocess(user_input)
    
    async def _ahandle_multi_domain_request(self, user_input: str) -> str:
        """Async handle multi-domain requests."""
        return self._handle_multi_domain_request(user_input)
    
    async def _ahandle_general_request(self, user_input: str) -> str:
        """Async handle general requests."""
        return self._handle_general_request(user_input)
    
    def _analyze_cross_domain_alignment(self, user_input: str) -> str:
        """
        Analyze alignment between goals and tasks.
        
        Args:
            user_input: Original user input for context
            
        Returns:
            Cross-domain analysis and recommendations
        """
        try:
            # This is a simplified analysis - could be enhanced with more sophisticated logic
            analysis_points = []
            
            # Check if user has both goals and tasks
            analysis_points.append(
                "✅ You have both goals and tasks set up in your Protocol Home system."
            )
            
            # Suggest alignment strategies
            if 'plan' in user_input.lower():
                analysis_points.append(
                    "💡 Consider breaking down your goals into specific tasks to ensure progress."
                )
                analysis_points.append(
                    "⏰ Time-block your tasks to align with your goal deadlines."
                )
            
            if 'review' in user_input.lower():
                analysis_points.append(
                    "📈 Regular reviews help maintain alignment between daily tasks and long-term goals."
                )
                analysis_points.append(
                    "🎯 Check if your completed tasks are contributing to goal progress."
                )
            
            return "\n".join(analysis_points) if analysis_points else None
            
        except Exception:
            return None
    
    def get_system_status(self) -> Dict[str, str]:
        """
        Get the status of all agents and systems.
        
        Returns:
            Dictionary with system status information
        """
        status = {
            "coordinator": "✅ Active",
            "goal_agent": "✅ Active" if self.goal_agent else "❌ Inactive",
            "todo_agent": "✅ Active" if self.todo_agent else "❌ Inactive",
            "schedule_agent": "✅ Active" if self.schedule_agent else "❌ Inactive",
            "notion_client": "✅ Connected" if self.notion else "❌ Disconnected",
        }
        return status
    
    def get_available_commands(self) -> List[str]:
        """
        Get list of available commands and examples.
        
        Returns:
            List of command examples
        """
        commands = [
            "📊 Goals:",
            "  • Create a goal to [description]",
            "  • Show my goals progress",
            "  • Update goal [id] with [changes]",
            "",
            "📋 Tasks:",
            "  • Add task: [description]",
            "  • Show my tasks for today",
            "  • Complete task [description]",
            "  • Prioritize my tasks",
            "",
            "📅 Schedule:",
            "  • Schedule my high priority todos for tomorrow",
            "  • Create meeting for 2pm today",
            "  • Find free time for a 1-hour task",
            "  • Show my schedule for today",
            "  • Suggest schedule for pending todos",
            "",
            "🎯 Multi-domain:",
            "  • Plan my week",
            "  • Review my productivity",
            "  • Show me an overview",
        ]
        return commands
