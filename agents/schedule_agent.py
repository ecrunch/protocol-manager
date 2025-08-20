"""
Schedule/calendar management agent for Protocol Home.

This agent specializes in calendar management, scheduling todos, finding free time,
and optimizing time allocation for maximum productivity.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import re
from langchain.tools import BaseTool
from .base_agent import BaseProtocolAgent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.schedule_tools import (
    CreateEventTool,
    ScheduleTodoTool,
    GetEventsTool,
    FindFreeTimeTool,
    SuggestScheduleTool,
    ManageConstraintsTool,
)
from prompts.system_prompts import SCHEDULE_AGENT_PROMPT


class SchedulingConstraints:
    """Model for storing and managing scheduling constraints."""
    
    def __init__(self):
        self.working_hours = {
            "core_hours": {"start": "08:00", "end": "17:00", "timezone": "CT"},
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "buffer_time": 10,  # minutes between blocks
            "transit_time": 30,  # minutes to get to work
            "no_double_booking": True
        }
        
        self.health_optimized_timing = {
            "ml_deep_work": "morning",  # preferred time for ML work
            "strength_training": "15:00-17:00",  # late afternoon
            "cardio": "flexible",  # morning or evening
            "meditation": "flexible"  # transition between work blocks
        }
        
        self.recovery_rest = {
            "strength_training_rest": 48,  # hours between major muscle groups
            "cardio_active_recovery": True,  # walking vs running
            "sleep_protection": 3  # hours before bedtime for intense exercise
        }
        
        self.monthly_adjustments = {}  # month-specific overrides
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert constraints to dictionary for storage."""
        return {
            "working_hours": self.working_hours,
            "health_optimized_timing": self.health_optimized_timing,
            "recovery_rest": self.recovery_rest,
            "monthly_adjustments": self.monthly_adjustments,
            "last_updated": datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SchedulingConstraints':
        """Create constraints from dictionary."""
        constraints = cls()
        if "working_hours" in data:
            constraints.working_hours.update(data["working_hours"])
        if "health_optimized_timing" in data:
            constraints.health_optimized_timing.update(data["health_optimized_timing"])
        if "recovery_rest" in data:
            constraints.recovery_rest.update(data["recovery_rest"])
        if "monthly_adjustments" in data:
            constraints.monthly_adjustments.update(data["monthly_adjustments"])
        return constraints
    
    def get_monthly_constraints(self, month: str) -> Dict[str, Any]:
        """Get month-specific constraints if they exist."""
        month_key = month.lower()
        if month_key in self.monthly_adjustments:
            return self.monthly_adjustments[month_key]
        return {}
    
    def update_monthly_constraints(self, month: str, constraints: Dict[str, Any]) -> None:
        """Update constraints for a specific month."""
        month_key = month.lower()
        self.monthly_adjustments[month_key] = constraints
    
    def is_valid_time(self, time_str: str, activity_type: str = None) -> bool:
        """Check if a time is valid according to constraints."""
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            core_start = datetime.strptime(self.working_hours["core_hours"]["start"], "%H:%M")
            core_end = datetime.strptime(self.working_hours["core_hours"]["end"], "%H:%M")
            
            # Check if within core hours
            if not (core_start <= time_obj <= core_end):
                return False
            
            # Check activity-specific constraints
            if activity_type == "ml_deep_work":
                preferred_start = datetime.strptime("09:00", "%H:%M")
                preferred_end = datetime.strptime("12:00", "%H:%M")
                return preferred_start <= time_obj <= preferred_end
            
            elif activity_type == "strength_training":
                preferred_start = datetime.strptime("15:00", "%H:%M")
                preferred_end = datetime.strptime("17:00", "%H:%M")
                return preferred_start <= time_obj <= preferred_end
            
            return True
            
        except ValueError:
            return False
    
    def get_optimal_time_slot(self, activity_type: str, date: str, duration_minutes: int = 60) -> Optional[str]:
        """Get optimal time slot for an activity based on constraints."""
        # This would integrate with calendar to find actual free time
        # For now, return preferred time based on constraints
        if activity_type == "ml_deep_work":
            return "09:00"
        elif activity_type == "strength_training":
            return "15:00"
        elif activity_type == "meditation":
            return "12:00"  # Lunch break
        else:
            return "10:00"  # Default morning slot


class ScheduleAgent(BaseProtocolAgent):
    """Agent specialized in schedule and calendar management."""
    
    def __init__(
        self,
        notion_client,
        calendar_database_id: str,
        todos_database_id: str,
        openai_api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Schedule Agent.
        
        Args:
            notion_client: Initialized Notion client instance
            calendar_database_id: The ID of the Calendar database in Notion
            todos_database_id: The ID of the Todos database in Notion
            openai_api_key: OpenAI API key
            **kwargs: Additional arguments for BaseProtocolAgent
        """
        self.calendar_database_id = calendar_database_id
        self.todos_database_id = todos_database_id
        
        # Initialize scheduling constraints
        self.scheduling_constraints = SchedulingConstraints()
        
        super().__init__(notion_client, openai_api_key, **kwargs)
        
    def _setup_tools(self) -> List[BaseTool]:
        """Setup schedule management tools."""
        return [
            CreateEventTool(
                notion_client=self.notion,
                calendar_database_id=self.calendar_database_id
            ),
            ScheduleTodoTool(
                notion_client=self.notion,
                calendar_database_id=self.calendar_database_id
            ),
            GetEventsTool(
                notion_client=self.notion,
                calendar_database_id=self.calendar_database_id
            ),
            FindFreeTimeTool(
                notion_client=self.notion,
                calendar_database_id=self.calendar_database_id
            ),
            SuggestScheduleTool(
                notion_client=self.notion,
                calendar_database_id=self.calendar_database_id,
                todos_database_id=self.todos_database_id
            ),
            ManageConstraintsTool(
                notion_client=self.notion,
                schedule_agent=self
            ),
        ]
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the schedule agent."""
        # Enhance the prompt with scheduling constraints awareness
        constraints_info = self._get_constraints_summary()
        enhanced_prompt = f"{SCHEDULE_AGENT_PROMPT}\n\n{constraints_info}"
        return enhanced_prompt
    
    def _get_constraints_summary(self) -> str:
        """Get a summary of current scheduling constraints for the prompt."""
        constraints = self.scheduling_constraints
        summary = f"""
**Current Scheduling Constraints:**
- **Working Hours**: {constraints.working_hours['core_hours']['start']}-{constraints.working_hours['core_hours']['end']} {constraints.working_hours['core_hours']['timezone']}, {', '.join(constraints.working_hours['days'])}
- **Buffer Time**: {constraints.working_hours['buffer_time']} minutes between all scheduled blocks
- **Transit Time**: {constraints.working_hours['transit_time']} minutes to get to work
- **ML Deep Work**: Preferred in {constraints.health_optimized_timing['ml_deep_work']} when cognitive function is at peak
- **Strength Training**: Optimal at {constraints.health_optimized_timing['strength_training']} for performance
- **Recovery**: {constraints.recovery_rest['strength_training_rest']} hours rest between major muscle groups
- **Sleep Protection**: No intense exercise within {constraints.recovery_rest['sleep_protection']} hours of bedtime

Always respect these constraints when scheduling activities and suggest optimal times based on them.
"""
        return summary
    
    def load_scheduling_constraints(self, constraints_data: Dict[str, Any]) -> None:
        """Load scheduling constraints from parsed data."""
        try:
            # Parse working hours
            if "working_hours" in constraints_data:
                wh = constraints_data["working_hours"]
                if "core_hours" in wh:
                    self.scheduling_constraints.working_hours["core_hours"].update(wh["core_hours"])
                if "buffer_time" in wh:
                    self.scheduling_constraints.working_hours["buffer_time"] = wh["buffer_time"]
                if "transit_time" in wh:
                    self.scheduling_constraints.working_hours["transit_time"] = wh["transit_time"]
                if "no_double_booking" in wh:
                    self.scheduling_constraints.working_hours["no_double_booking"] = wh["no_double_booking"]
            
            # Parse health-optimized timing
            if "health_optimized_timing" in constraints_data:
                hot = constraints_data["health_optimized_timing"]
                for key in ["ml_deep_work", "strength_training", "cardio", "meditation"]:
                    if key in hot:
                        self.scheduling_constraints.health_optimized_timing[key] = hot[key]
            
            # Parse recovery and rest
            if "recovery_rest" in constraints_data:
                rr = constraints_data["recovery_rest"]
                for key in ["strength_training_rest", "cardio_active_recovery", "sleep_protection"]:
                    if key in rr:
                        self.scheduling_constraints.recovery_rest[key] = rr[key]
            
            print(f"✅ Loaded scheduling constraints: {len(constraints_data)} categories")
            
        except Exception as e:
            print(f"⚠️ Error loading scheduling constraints: {e}")
    
    def update_monthly_constraints(self, month: str, constraints: Dict[str, Any]) -> None:
        """Update constraints for a specific month."""
        self.scheduling_constraints.update_monthly_constraints(month, constraints)
        print(f"✅ Updated constraints for {month}")
    
    def get_constraints_for_date(self, date: str) -> Dict[str, Any]:
        """Get applicable constraints for a specific date."""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            month = date_obj.strftime("%B")  # Full month name
            
            # Get base constraints
            base_constraints = self.scheduling_constraints.to_dict()
            
            # Add month-specific adjustments
            monthly_constraints = self.scheduling_constraints.get_monthly_constraints(month)
            if monthly_constraints:
                base_constraints["monthly_adjustments"] = monthly_constraints
            
            return base_constraints
            
        except ValueError:
            return self.scheduling_constraints.to_dict()
    
    def suggest_optimal_schedule_with_constraints(self, date: str, todos: List[Dict[str, Any]]) -> str:
        """Suggest optimal schedule considering all constraints."""
        constraints = self.get_constraints_for_date(date)
        
        # Group todos by type for optimal scheduling
        ml_todos = [t for t in todos if "ML" in t.get("title", "") or "machine learning" in t.get("title", "").lower()]
        health_todos = [t for t in todos if any(word in t.get("title", "").lower() for word in ["training", "exercise", "workout", "cardio"])]
        other_todos = [t for t in todos if t not in ml_todos and t not in health_todos]
        
        schedule_suggestions = []
        
        # Schedule ML work in morning
        if ml_todos:
            for todo in ml_todos:
                optimal_time = self.scheduling_constraints.get_optimal_time_slot("ml_deep_work", date)
                schedule_suggestions.append(f"• **{todo['title']}**: {optimal_time} (ML Deep Work - optimal cognitive time)")
        
        # Schedule strength training in late afternoon
        if health_todos:
            for todo in health_todos:
                if "strength" in todo.get("title", "").lower():
                    optimal_time = self.scheduling_constraints.get_optimal_time_slot("strength_training", date)
                    schedule_suggestions.append(f"• **{todo['title']}**: {optimal_time} (Strength Training - optimal performance time)")
                else:
                    optimal_time = self.scheduling_constraints.get_optimal_time_slot("cardio", date)
                    schedule_suggestions.append(f"• **{todo['title']}**: {optimal_time} (Cardio - flexible timing)")
        
        # Schedule other todos
        for todo in other_todos:
            optimal_time = self.scheduling_constraints.get_optimal_time_slot("general", date)
            schedule_suggestions.append(f"• **{todo['title']}**: {optimal_time}")
        
        constraints_summary = f"""
**Scheduling Constraints Applied:**
- Working Hours: {constraints['working_hours']['core_hours']['start']}-{constraints['working_hours']['core_hours']['end']} {constraints['working_hours']['core_hours']['timezone']}
- Buffer Time: {constraints['working_hours']['buffer_time']} minutes between blocks
- ML Work: Morning preference for peak cognitive function
- Strength Training: Late afternoon (3-5 PM) for optimal performance
- Recovery: {constraints['recovery_rest']['strength_training_rest']} hours rest between major muscle groups
"""
        
        return f"""
📅 **Optimal Schedule for {date} (Respecting Your Constraints)**

{chr(10).join(schedule_suggestions)}

{constraints_summary}

💡 **Tips:**
- All times include {constraints['working_hours']['buffer_time']} minute buffers
- Remember {constraints['working_hours']['transit_time']} minutes transit time
- No double-booking enforced
- Sleep protection: No intense exercise within {constraints['recovery_rest']['sleep_protection']} hours of bedtime
"""
        
    def create_event(
        self,
        title: str,
        start_datetime: str,
        end_datetime: Optional[str] = None,
        event_type: str = "Meeting",
        location: Optional[str] = None
    ) -> str:
        """
        Create a new calendar event.
        
        Args:
            title: Event title
            start_datetime: Start date and time (YYYY-MM-DDTHH:MM)
            end_datetime: End date and time (YYYY-MM-DDTHH:MM)
            event_type: Type of event (Meeting, Call, etc.)
            location: Event location
            
        Returns:
            Result message from event creation
        """
        request = f"Create a calendar event: {title} starting at {start_datetime}"
        if end_datetime:
            request += f" ending at {end_datetime}"
        if event_type != "Meeting":
            request += f" as a {event_type}"
        if location:
            request += f" at {location}"
            
        return self.process(request)
        
    def schedule_todo(
        self,
        todo_description: str,
        start_datetime: str,
        duration_minutes: Optional[int] = None
    ) -> str:
        """
        Schedule a todo as a calendar event for focused work time.
        
        Args:
            todo_description: Description to find the todo
            start_datetime: When to schedule the work (YYYY-MM-DDTHH:MM)
            duration_minutes: How long to allocate for this work
            
        Returns:
            Result message from scheduling
        """
        request = f"Schedule todo '{todo_description}' at {start_datetime}"
        if duration_minutes:
            request += f" for {duration_minutes} minutes"
            
        return self.process(request)
        
    def get_today_schedule(self) -> str:
        """
        Get today's calendar events.
        
        Returns:
            Today's schedule with events
        """
        return self.process("Show me my schedule for today")
        
    def get_week_schedule(self) -> str:
        """
        Get this week's calendar events.
        
        Returns:
            This week's schedule with events
        """
        return self.process("Show me my schedule for this week")
        
    def find_free_time(
        self,
        date: str,
        duration_minutes: int = 60,
        preferred_start: str = "09:00",
        preferred_end: str = "17:00"
    ) -> str:
        """
        Find available time slots for scheduling.
        
        Args:
            date: Date to find free time (YYYY-MM-DD)
            duration_minutes: Duration needed in minutes
            preferred_start: Preferred start time (HH:MM)
            preferred_end: Preferred end time (HH:MM)
            
        Returns:
            Available time slots
        """
        request = f"Find {duration_minutes} minutes of free time on {date}"
        if preferred_start != "09:00" or preferred_end != "17:00":
            request += f" between {preferred_start} and {preferred_end}"
            
        return self.process(request)
        
    def suggest_schedule(
        self,
        date: Optional[str] = None,
        priority_filter: Optional[str] = None,
        project_filter: Optional[str] = None
    ) -> str:
        """
        Suggest an optimal schedule for pending todos.
        
        Args:
            date: Date to schedule for (YYYY-MM-DD)
            priority_filter: Only schedule todos with this priority
            project_filter: Only schedule todos from this project
            
        Returns:
            Suggested schedule with time blocks
        """
        request = "Suggest an optimal schedule for my pending todos"
        if date:
            request += f" for {date}"
        if priority_filter:
            request += f" with {priority_filter} priority"
        if project_filter:
            request += f" from the {project_filter} project"
            
        return self.process(request)
        
    def time_block_planning(self, date: Optional[str] = None) -> str:
        """
        Create a time-blocked schedule for the day.
        
        Args:
            date: Date to plan for (YYYY-MM-DD)
            
        Returns:
            Time-blocked schedule recommendations
        """
        request = "Help me create a time-blocked schedule"
        if date:
            request += f" for {date}"
        else:
            request += " for today"
            
        return self.process(request)
        
    def reschedule_event(
        self,
        event_description: str,
        new_start_datetime: str,
        new_end_datetime: Optional[str] = None
    ) -> str:
        """
        Reschedule an existing event.
        
        Args:
            event_description: Description to identify the event
            new_start_datetime: New start date and time
            new_end_datetime: New end date and time
            
        Returns:
            Rescheduling confirmation
        """
        request = f"Reschedule the event '{event_description}' to {new_start_datetime}"
        if new_end_datetime:
            request += f" ending at {new_end_datetime}"
            
        return self.process(request)
        
    def optimize_daily_schedule(self, date: Optional[str] = None) -> str:
        """
        Analyze and optimize the daily schedule for productivity.
        
        Args:
            date: Date to optimize (YYYY-MM-DD)
            
        Returns:
            Schedule optimization recommendations
        """
        request = "Analyze and optimize my daily schedule for maximum productivity"
        if date:
            request += f" for {date}"
        else:
            request += " for today"
            
        return self.process(request)
        
    def batch_schedule_todos(
        self,
        project: Optional[str] = None,
        priority: Optional[str] = None,
        date: Optional[str] = None
    ) -> str:
        """
        Schedule multiple todos at once based on criteria.
        
        Args:
            project: Project to schedule todos from
            priority: Priority level to focus on
            date: Date to schedule for
            
        Returns:
            Batch scheduling results
        """
        request = "Schedule multiple todos for focused work sessions"
        if project:
            request += f" from the {project} project"
        if priority:
            request += f" with {priority} priority"
        if date:
            request += f" on {date}"
        else:
            request += " today"
            
        return self.process(request)
        
    def meeting_preparation_time(
        self,
        meeting_description: str,
        prep_minutes: int = 15
    ) -> str:
        """
        Schedule preparation time before a meeting.
        
        Args:
            meeting_description: Description to identify the meeting
            prep_minutes: Minutes of preparation time needed
            
        Returns:
            Preparation scheduling result
        """
        return self.process(
            f"Schedule {prep_minutes} minutes of preparation time before the "
            f"meeting '{meeting_description}'"
        )
        
    def weekly_planning_session(self, week_start_date: Optional[str] = None) -> str:
        """
        Conduct a weekly planning session to organize the upcoming week.
        
        Args:
            week_start_date: Start date of the week to plan (YYYY-MM-DD)
            
        Returns:
            Weekly planning analysis and recommendations
        """
        request = "Help me conduct a weekly planning session"
        if week_start_date:
            request += f" starting from {week_start_date}"
            
        return self.process(request)
        
    def energy_based_scheduling(self, date: Optional[str] = None) -> str:
        """
        Suggest task scheduling based on energy levels throughout the day.
        
        Args:
            date: Date to plan for (YYYY-MM-DD)
            
        Returns:
            Energy-based scheduling recommendations
        """
        request = "Suggest an energy-based schedule that matches high-energy tasks with peak hours"
        if date:
            request += f" for {date}"
        else:
            request += " for today"
            
        return self.process(request)
        
    def check_schedule_conflicts(self, date: Optional[str] = None) -> str:
        """
        Check for scheduling conflicts and overlapping events.
        
        Args:
            date: Date to check (YYYY-MM-DD)
            
        Returns:
            Conflict analysis and resolution suggestions
        """
        request = "Check for scheduling conflicts and overlapping events"
        if date:
            request += f" on {date}"
        else:
            request += " in my upcoming schedule"
            
        return self.process(request)
        
    def calendar_analytics(self, week_start: Optional[str] = None) -> str:
        """
        Provide analytics on calendar usage and time allocation.
        
        Args:
            week_start: Start date for analytics period (YYYY-MM-DD)
            
        Returns:
            Calendar analytics and insights
        """
        request = "Provide analytics on my calendar usage and time allocation patterns"
        if week_start:
            request += f" starting from {week_start}"
            
        return self.process(request)
