"""
Schedule management tools for Protocol Home.

This module provides tools for calendar management, scheduling todos,
finding free time, and managing scheduling constraints.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Type, Optional, Any, Dict
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import pytz

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CreateEventInput(BaseModel):
    """Input for creating calendar events."""
    title: str = Field(description="Event title")
    start_datetime: str = Field(description="Start date and time (YYYY-MM-DDTHH:MM)")
    end_datetime: Optional[str] = Field(description="End date and time (YYYY-MM-DDTHH:MM)")
    event_type: str = Field(description="Type of event (Meeting, Call, etc.)", default="Meeting")
    location: Optional[str] = Field(description="Event location")


class CreateEventTool(BaseTool):
    """Tool for creating calendar events in Notion."""
    
    name: str = "create_calendar_event"
    description: str = "Create a new calendar event in the calendar database"
    notion_client: Any = Field(exclude=True)
    calendar_database_id: str = Field(description="ID of the calendar database")
    
    args_schema: type[BaseModel] = CreateEventInput
    
    def _run(self, title: str, start_datetime: str, end_datetime: str = None, 
             event_type: str = "Meeting", location: str = None) -> str:
        """Create a calendar event in Notion."""
        try:
            # Parse datetime
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            
            if end_datetime:
                end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            else:
                # Default to 1 hour duration
                end_dt = start_dt + timedelta(hours=1)
            
            # Create event properties
            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
                "Event Type": {"select": {"name": event_type}},
                "Start Date": {"date": {"start": start_dt.isoformat()}},
                "End Date": {"date": {"end": end_dt.isoformat()}},
                "Status": {"select": {"name": "Scheduled"}}
            }
            
            if location:
                properties["Location"] = {"rich_text": [{"text": {"content": location}}]}
            
            # Create the event
            event = self.notion_client.pages.create(
                parent={"database_id": self.calendar_database_id},
                properties=properties
            )
            
            return f"✅ Created calendar event '{title}' for {start_dt.strftime('%Y-%m-%d %H:%M')}"
            
        except Exception as e:
            return f"❌ Error creating calendar event: {str(e)}"


class ScheduleTodoInput(BaseModel):
    """Input for scheduling todos."""
    todo_id: str = Field(description="ID of the todo to schedule")
    start_datetime: str = Field(description="Start date and time (YYYY-MM-DDTHH:MM)")
    duration_minutes: Optional[int] = Field(description="Duration in minutes", default=60)


class ScheduleTodoTool(BaseTool):
    """Tool for scheduling todos as calendar events."""
    
    name: str = "schedule_todo"
    description: str = "Schedule a todo as a calendar event for focused work time"
    notion_client: Any = Field(exclude=True)
    calendar_database_id: str = Field(description="ID of the calendar database")
    
    args_schema: type[BaseModel] = ScheduleTodoInput
    
    def _run(self, todo_id: str, start_datetime: str, duration_minutes: int = 60) -> str:
        """Schedule a todo as a calendar event."""
        try:
            # Parse the start datetime
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            
            # Convert to CDT timezone
            cdt_tz = pytz.timezone('America/Chicago')
            if start_dt.tzinfo is None:
                # If no timezone info, assume it's local time and convert to CDT
                start_dt = cdt_tz.localize(start_dt)
            else:
                # Convert from UTC to CDT
                start_dt = start_dt.astimezone(cdt_tz)
            
            # Calculate end time
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            # Get todo title
            todo_title = f"Todo {todo_id[:8]}"
            try:
                # Try to get the actual todo title from Notion
                todo_page = self.notion_client.pages.retrieve(todo_id)
                if todo_page.properties.get("Task", {}).get("title"):
                    todo_title = "".join([
                        text.get("plain_text", "") 
                        for text in todo_page.properties["Task"]["title"]
                    ])
                elif todo_page.properties.get("Name", {}).get("title"):
                    todo_title = "".join([
                        text.get("plain_text", "") 
                        for text in todo_page.properties["Name"]["title"]
                    ])
            except:
                todo_title = f"Todo {todo_id[:8]}"
            
            # Create event properties with CDT timezone
            properties = {
                "Event Title": {"title": [{"text": {"content": f"📋 {todo_title}"}}]},
                "Event Type": {"select": {"name": "Work Session"}},
                "Start Date & Time": {"date": {"start": start_dt.isoformat()}},
                "End Date & Time": {"date": {"start": end_dt.isoformat()}},
                "Status": {"select": {"name": "Confirmed"}},
                "Priority": {"select": {"name": "High"}},
                "Notes": {"rich_text": [{"text": {"content": f"Related Todo: {todo_id}"}}]}
            }
            
            # Create the scheduled event
            event = self.notion_client.pages.create(
                parent={"database_id": self.calendar_database_id},
                properties=properties
            )
            
            # Update todo status to "In Progress" if it exists
            try:
                self.notion_client.pages.update(
                    todo_id,
                    properties={
                        "Status": {"select": {"name": "In Progress"}},
                        "Scheduled": {"date": {"start": start_dt.isoformat()}}
                    }
                )
            except:
                pass  # Todo might not exist or not have these properties
            
            return f"📅 Scheduled todo '{todo_title}' for {start_dt.strftime('%Y-%m-%d %H:%M')} ({duration_minutes} minutes)"
            
        except Exception as e:
            return f"❌ Error scheduling todo: {str(e)}"


class GetEventsInput(BaseModel):
    """Input for getting events."""
    date: str = Field(description="Date to get events for (YYYY-MM-DD)")


class GetEventsTool(BaseTool):
    """Tool for retrieving calendar events."""
    
    name: str = "get_calendar_events"
    description: str = "Get calendar events for a specific date"
    notion_client: Any = Field(exclude=True)
    calendar_database_id: str = Field(description="ID of the calendar database")
    
    args_schema: type[BaseModel] = GetEventsInput
    
    def _run(self, date: str) -> str:
        """Get calendar events for a specific date."""
        try:
            # Query events for the date
            start_date = f"{date}T00:00:00"
            end_date = f"{date}T23:59:59"
            
            response = self.notion_client.databases.query(
                database_id=self.calendar_database_id,
                filter={
                    "and": [
                        {
                            "property": "Start Date",
                            "date": {
                                "on_or_before": end_date
                            }
                        },
                        {
                            "property": "End Date", 
                            "date": {
                                "on_or_after": start_date
                            }
                        }
                    ]
                },
                sorts=[{"property": "Start Date", "direction": "ascending"}]
            )
            
            if not response.results:
                return f"📅 No events scheduled for {date}"
            
            events = []
            for event in response.results:
                # Extract event details
                title = ""
                if event.properties.get("Title"):
                    title = "".join([
                        text.get("plain_text", "") 
                        for text in event.properties["Title"]["title"]
                    ])
                
                start_time = ""
                if event.properties.get("Start Date", {}).get("date"):
                    start_dt = datetime.fromisoformat(event.properties["Start Date"]["date"]["start"])
                    start_time = start_dt.strftime("%H:%M")
                
                end_time = ""
                if event.properties.get("End Date", {}).get("date"):
                    end_dt = datetime.fromisoformat(event.properties["End Date"]["date"]["start"])
                    end_time = end_dt.strftime("%H:%M")
                
                event_type = ""
                if event.properties.get("Event Type", {}).get("select"):
                    event_type = event.properties["Event Type"]["select"]["name"]
                
                events.append(f"• **{title}** ({event_type}): {start_time}-{end_time}")
            
            return f"📅 **Events for {date}:**\n\n" + "\n".join(events)
            
        except Exception as e:
            return f"❌ Error getting events: {str(e)}"


class FindFreeTimeInput(BaseModel):
    """Input for finding free time."""
    date: str = Field(description="Date to find free time (YYYY-MM-DD)")
    duration_minutes: int = Field(description="Duration needed in minutes")
    preferred_start: Optional[str] = Field(description="Preferred start time (HH:MM)", default="09:00")
    preferred_end: Optional[str] = Field(description="Preferred end time (HH:MM)", default="17:00")


class FindFreeTimeTool(BaseTool):
    """Tool for finding available time slots."""
    
    name: str = "find_free_time"
    description: str = "Find available time slots for scheduling"
    notion_client: Any = Field(exclude=True)
    calendar_database_id: str = Field(description="ID of the calendar database")
    
    args_schema: type[BaseModel] = FindFreeTimeInput
    
    def _run(self, date: str, duration_minutes: int, preferred_start: str = "09:00", 
             preferred_end: str = "17:00") -> str:
        """Find available time slots for scheduling."""
        try:
            # Get events for the date
            start_date = f"{date}T00:00:00"
            end_date = f"{date}T23:59:59"
            
            response = self.notion_client.databases.query(
                database_id=self.calendar_database_id,
                filter={
                    "and": [
                        {
                            "property": "Start Date",
                            "date": {
                                "on_or_before": end_date
                            }
                        },
                        {
                            "property": "End Date", 
                            "date": {
                                "on_or_after": start_date
                            }
                        }
                    ]
                },
                sorts=[{"property": "Start Date", "direction": "ascending"}]
            )
            
            # Parse preferred times
            preferred_start_dt = datetime.strptime(preferred_start, "%H:%M")
            preferred_end_dt = datetime.strptime(preferred_end, "%H:%M")
            
            # Create time slots
            time_slots = []
            current_time = preferred_start_dt
            
            while current_time + timedelta(minutes=duration_minutes) <= preferred_end_dt:
                slot_start = current_time
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                # Check if this slot conflicts with existing events
                slot_available = True
                for event in response.results:
                    if event.properties.get("Start Date", {}).get("date") and event.properties.get("End Date", {}).get("date"):
                        event_start = datetime.fromisoformat(event.properties["Start Date"]["date"]["start"])
                        event_end = datetime.fromisoformat(event.properties["End Date"]["date"]["start"])
                        
                        # Check for overlap
                        if not (slot_end <= event_start or slot_start >= event_end):
                            slot_available = False
                            break
                
                if slot_available:
                    time_slots.append(f"{slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}")
                
                current_time += timedelta(minutes=30)  # 30-minute increments
            
            if not time_slots:
                return f"❌ No {duration_minutes}-minute free time slots found on {date} between {preferred_start} and {preferred_end}"
            
            return f"🕐 **Available {duration_minutes}-minute slots on {date}:**\n\n" + "\n".join(time_slots[:5])  # Show first 5 slots
            
        except Exception as e:
            return f"❌ Error finding free time: {str(e)}"


class SuggestScheduleInput(BaseModel):
    """Input for suggesting schedules."""
    date: Optional[str] = Field(description="Date to suggest schedule for (YYYY-MM-DD)")
    priority_filter: Optional[str] = Field(description="Only suggest todos with this priority")
    project_filter: Optional[str] = Field(description="Only suggest todos from this project")


class SuggestScheduleTool(BaseTool):
    """Tool for suggesting optimal schedules."""
    
    name: str = "suggest_schedule"
    description: str = "Suggest an optimal schedule for pending todos"
    notion_client: Any = Field(exclude=True)
    calendar_database_id: str = Field(description="ID of the calendar database")
    todos_database_id: str = Field(description="ID of the todos database")
    
    args_schema: type[BaseModel] = SuggestScheduleInput
    
    def _run(self, date: str = None, priority_filter: str = None, 
             project_filter: str = None) -> str:
        """Suggest an optimal schedule for pending todos."""
        try:
            # Build filter for todos
            filter_conditions = [
                {
                    "property": "Status",
                    "select": {
                        "does_not_equal": "Done"
                    }
                }
            ]
            
            if priority_filter:
                filter_conditions.append({
                    "property": "Priority",
                    "select": {
                        "equals": priority_filter
                    }
                })
            
            if project_filter:
                filter_conditions.append({
                    "property": "Project",
                    "select": {
                        "equals": project_filter
                    }
                })
            
            # Get pending todos
            todos_response = self.notion_client.databases.query(
                database_id=self.todos_database_id,
                filter={"and": filter_conditions} if len(filter_conditions) > 1 else filter_conditions[0],
                sorts=[{"property": "Priority", "direction": "descending"}]
            )
            
            if not todos_response.results:
                return "📋 No pending todos found to schedule"
            
            # Group todos by priority
            high_priority = []
            medium_priority = []
            low_priority = []
            
            for todo in todos_response.results:
                title = ""
                if todo.properties.get("Task"):
                    title = "".join([
                        text.get("plain_text", "") 
                        for text in todo.properties["Task"]["title"]
                    ])
                elif todo.properties.get("Title"):
                    title = "".join([
                        text.get("plain_text", "") 
                        for text in todo.properties["Title"]["title"]
                    ])
                
                priority = "Medium"
                if todo.properties.get("Priority", {}).get("select"):
                    priority = todo.properties["Priority"]["select"]["name"]
                
                time_estimate = 60
                if todo.properties.get("Time Estimate", {}).get("number"):
                    time_estimate = todo.properties["Time Estimate"]["number"]
                
                todo_info = {"title": title, "priority": priority, "time_estimate": time_estimate}
                
                if priority in ["High", "Urgent"]:
                    high_priority.append(todo_info)
                elif priority == "Medium":
                    medium_priority.append(todo_info)
                else:
                    low_priority.append(todo_info)
            
            # Build schedule suggestion
            schedule_suggestions = []
            current_time = datetime.strptime("09:00", "%H:%M")
            
            # Schedule high priority first
            for todo in high_priority:
                schedule_suggestions.append(f"• **{todo['title']}** ({todo['priority']}): {current_time.strftime('%H:%M')} ({todo['time_estimate']} min)")
                current_time += timedelta(minutes=todo['time_estimate'] + 10)  # Add 10 min buffer
            
            # Schedule medium priority
            for todo in medium_priority:
                schedule_suggestions.append(f"• **{todo['title']}** ({todo['priority']}): {current_time.strftime('%H:%M')} ({todo['time_estimate']} min)")
                current_time += timedelta(minutes=todo['time_estimate'] + 10)
            
            # Schedule low priority if time allows
            for todo in low_priority:
                if current_time <= datetime.strptime("17:00", "%H:%M"):
                    schedule_suggestions.append(f"• **{todo['title']}** ({todo['priority']}): {current_time.strftime('%H:%M')} ({todo['time_estimate']} min)")
                    current_time += timedelta(minutes=todo['time_estimate'] + 10)
            
            return f"📅 **Suggested Schedule for {date or 'today'}:**\n\n" + "\n".join(schedule_suggestions)
            
        except Exception as e:
            return f"❌ Error suggesting schedule: {str(e)}"


class ManageConstraintsInput(BaseModel):
    """Input for managing scheduling constraints."""
    action: str = Field(description="Action to perform: 'view', 'update', 'reset'")
    month: Optional[str] = Field(description="Month for month-specific operations")
    constraints_data: Optional[Dict[str, Any]] = Field(description="Constraints data for updates")


class ManageConstraintsTool(BaseTool):
    """Tool for managing scheduling constraints."""
    
    name: str = "manage_scheduling_constraints"
    description: str = "View, update, or reset scheduling constraints for the schedule agent"
    notion_client: Any = Field(exclude=True)
    schedule_agent: Any = Field(exclude=True)
    
    args_schema: type[BaseModel] = ManageConstraintsInput
    
    def _run(self, action: str, month: str = None, constraints_data: Dict[str, Any] = None) -> str:
        """Manage scheduling constraints."""
        try:
            if action == "view":
                constraints = self.schedule_agent.scheduling_constraints.to_dict()
                return f"📋 **Current Scheduling Constraints:**\n\n" + \
                       f"Working Hours: {constraints['working_hours']['core_hours']['start']}-{constraints['working_hours']['core_hours']['end']}\n" + \
                       f"Buffer Time: {constraints['working_hours']['buffer_time']} minutes\n" + \
                       f"ML Work: {constraints['health_optimized_timing']['ml_deep_work']}\n" + \
                       f"Strength Training: {constraints['health_optimized_timing']['strength_training']}\n" + \
                       f"Monthly Adjustments: {len(constraints.get('monthly_adjustments', {}))} months"
            
            elif action == "update" and month and constraints_data:
                self.schedule_agent.update_monthly_constraints(month, constraints_data)
                return f"✅ Updated constraints for {month}"
            
            elif action == "reset" and month:
                if month.lower() == "all":
                    self.schedule_agent.scheduling_constraints.monthly_adjustments.clear()
                    return "✅ Reset all monthly constraint adjustments"
                else:
                    self.schedule_agent.scheduling_constraints.monthly_adjustments.pop(month.lower(), None)
                    return f"✅ Reset constraints for {month}"
            
            else:
                return "❌ Invalid action or missing parameters. Use 'view', 'update', or 'reset'"
            
        except Exception as e:
            return f"❌ Error managing constraints: {str(e)}"
