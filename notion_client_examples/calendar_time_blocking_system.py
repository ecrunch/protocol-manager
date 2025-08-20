"""
Complete Calendar and Time Blocking System for Notion

This script creates a comprehensive calendar system with:
- Calendar Events database
- Todo/Tasks database with time blocking
- Time Block database for focused work sessions
- Daily Planning database
- Integration between all systems
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_client import NotionClient
from notion_client.utils import (
    create_rich_text,
    create_page_parent,
    create_select_option,
    create_icon,
    format_notion_date,
)


def create_calendar_events_database(client: NotionClient, parent_page_id: str):
    """Create a database for calendar events."""
    
    print("Creating Calendar Events database...")
    
    title = [create_rich_text("📅 Calendar Events")]
    description = [create_rich_text("Manage all your calendar events, meetings, and appointments")]
    
    properties = {
        "Event Title": {
            "title": {}
        },
        
        "Start Date & Time": {
            "date": {}
        },
        
        "End Date & Time": {
            "date": {}
        },
        
        "Event Type": {
            "select": {
                "options": [
                    create_select_option("🤝 Meeting", "blue"),
                    create_select_option("📞 Call", "green"),
                    create_select_option("🎯 Workshop", "purple"),
                    create_select_option("🎉 Event", "pink"),
                    create_select_option("✈️ Travel", "orange"),
                    create_select_option("🏥 Appointment", "red"),
                    create_select_option("🎓 Learning", "yellow"),
                    create_select_option("💼 Work", "gray")
                ]
            }
        },
        
        "Location": {
            "rich_text": {}
        },
        
        "Attendees": {
            "people": {}
        },
        
        "Meeting URL": {
            "url": {}
        },
        
        "Status": {
            "select": {
                "options": [
                    create_select_option("✅ Confirmed", "green"),
                    create_select_option("❓ Tentative", "yellow"),
                    create_select_option("❌ Cancelled", "red"),
                    create_select_option("🔄 Rescheduled", "orange")
                ]
            }
        },
        
        "Priority": {
            "select": {
                "options": [
                    create_select_option("🔥 High", "red"),
                    create_select_option("⚡ Medium", "yellow"),
                    create_select_option("💧 Low", "blue")
                ]
            }
        },
        
        "Preparation Needed": {
            "checkbox": {}
        },
        
        "Notes": {
            "rich_text": {}
        },
        
        "Recurring": {
            "select": {
                "options": [
                    create_select_option("📅 Daily", "blue"),
                    create_select_option("📆 Weekly", "green"),
                    create_select_option("🗓️ Monthly", "orange"),
                    create_select_option("🚫 None", "gray")
                ]
            }
        }
    }
    
    try:
        database = client.databases.create(
            parent=create_page_parent(parent_page_id),
            title=title,
            description=description,
            properties=properties,
            icon=create_icon("emoji", "📅")
        )
        
        print(f"✅ Calendar Events database created!")
        print(f"   ID: {database.id}")
        print(f"   URL: {database.url}")
        return database
        
    except Exception as e:
        print(f"❌ Error creating Calendar Events database: {e}")
        return None


def create_time_blocks_database(client: NotionClient, parent_page_id: str):
    """Create a database for time blocking and focused work sessions."""
    
    print("\nCreating Time Blocks database...")
    
    title = [create_rich_text("⏰ Time Blocks")]
    description = [create_rich_text("Plan focused work sessions and time blocking")]
    
    properties = {
        "Block Title": {
            "title": {}
        },
        
        "Date": {
            "date": {}
        },
        
        "Start Time": {
            "date": {}
        },
        
        "End Time": {
            "date": {}
        },
        
        "Duration (Hours)": {
            "number": {
                "format": "number"
            }
        },
        
        "Block Type": {
            "select": {
                "options": [
                    create_select_option("🎯 Deep Work", "purple"),
                    create_select_option("📧 Email/Admin", "blue"),
                    create_select_option("🤝 Meetings", "green"),
                    create_select_option("📚 Learning", "orange"),
                    create_select_option("💭 Planning", "yellow"),
                    create_select_option("🎨 Creative", "pink"),
                    create_select_option("🔄 Review", "gray"),
                    create_select_option("🧘 Break", "red")
                ]
            }
        },
        
        "Energy Level Required": {
            "select": {
                "options": [
                    create_select_option("🔋 High Energy", "red"),
                    create_select_option("⚡ Medium Energy", "yellow"),
                    create_select_option("🌙 Low Energy", "blue")
                ]
            }
        },
        
        "Status": {
            "select": {
                "options": [
                    create_select_option("📝 Planned", "yellow"),
                    create_select_option("🔄 In Progress", "blue"),
                    create_select_option("✅ Completed", "green"),
                    create_select_option("❌ Skipped", "red")
                ]
            }
        },
        
        "Actual Start": {
            "date": {}
        },
        
        "Actual End": {
            "date": {}
        },
        
        "Focus Score (1-10)": {
            "number": {}
        },
        
        "Tasks Completed": {
            "rich_text": {}
        },
        
        "Notes": {
            "rich_text": {}
        },
        
        "Location": {
            "select": {
                "options": [
                    create_select_option("🏠 Home Office", "blue"),
                    create_select_option("☕ Coffee Shop", "brown"),
                    create_select_option("🏢 Office", "gray"),
                    create_select_option("📚 Library", "green"),
                    create_select_option("🌳 Outdoor", "yellow")
                ]
            }
        }
    }
    
    try:
        database = client.databases.create(
            parent=create_page_parent(parent_page_id),
            title=title,
            description=description,
            properties=properties,
            icon=create_icon("emoji", "⏰")
        )
        
        print(f"✅ Time Blocks database created!")
        print(f"   ID: {database.id}")
        print(f"   URL: {database.url}")
        return database
        
    except Exception as e:
        print(f"❌ Error creating Time Blocks database: {e}")
        return None


def create_todos_with_scheduling(client: NotionClient, parent_page_id: str):
    """Create an enhanced todo database with scheduling and time blocking."""
    
    print("\nCreating Enhanced Todos database...")
    
    title = [create_rich_text("✅ Todos & Tasks")]
    description = [create_rich_text("Task management with scheduling and time blocking integration")]
    
    properties = {
        "Task": {
            "title": {}
        },
        
        "Status": {
            "select": {
                "options": [
                    create_select_option("📝 Not Started", "red"),
                    create_select_option("🔄 In Progress", "yellow"),
                    create_select_option("⏸️ Paused", "orange"),
                    create_select_option("✅ Completed", "green"),
                    create_select_option("❌ Cancelled", "gray")
                ]
            }
        },
        
        "Priority": {
            "select": {
                "options": [
                    create_select_option("🔥 Urgent", "red"),
                    create_select_option("⚡ High", "orange"),
                    create_select_option("📊 Medium", "yellow"),
                    create_select_option("💧 Low", "blue"),
                    create_select_option("🗂️ Someday", "gray")
                ]
            }
        },
        
        "Due Date": {
            "date": {}
        },
        
        "Scheduled Date": {
            "date": {}
        },
        
        "Estimated Time (Hours)": {
            "number": {
                "format": "number"
            }
        },
        
        "Actual Time (Hours)": {
            "number": {
                "format": "number"
            }
        },
        
        "Category": {
            "select": {
                "options": [
                    create_select_option("💼 Work", "blue"),
                    create_select_option("🏠 Personal", "green"),
                    create_select_option("📚 Learning", "purple"),
                    create_select_option("💰 Finance", "yellow"),
                    create_select_option("🏥 Health", "red"),
                    create_select_option("🎯 Goals", "orange"),
                    create_select_option("🛠️ Maintenance", "gray")
                ]
            }
        },
        
        "Energy Level": {
            "select": {
                "options": [
                    create_select_option("🔋 High Energy", "red"),
                    create_select_option("⚡ Medium Energy", "yellow"),
                    create_select_option("🌙 Low Energy", "blue")
                ]
            }
        },
        
        "Context": {
            "multi_select": {
                "options": [
                    create_select_option("💻 Computer", "blue"),
                    create_select_option("📞 Phone", "green"),
                    create_select_option("🏠 Home", "yellow"),
                    create_select_option("🏢 Office", "purple"),
                    create_select_option("🚗 Errands", "orange"),
                    create_select_option("👥 People", "pink")
                ]
            }
        },
        
        "Progress %": {
            "number": {
                "format": "percent"
            }
        },
        
        "Notes": {
            "rich_text": {}
        },
        
        "Subtasks": {
            "rich_text": {}
        },
        
        "Blocked By": {
            "rich_text": {}
        }
    }
    
    try:
        database = client.databases.create(
            parent=create_page_parent(parent_page_id),
            title=title,
            description=description,
            properties=properties,
            icon=create_icon("emoji", "✅")
        )
        
        print(f"✅ Enhanced Todos database created!")
        print(f"   ID: {database.id}")
        print(f"   URL: {database.url}")
        return database
        
    except Exception as e:
        print(f"❌ Error creating Enhanced Todos database: {e}")
        return None


def create_daily_planning_database(client: NotionClient, parent_page_id: str):
    """Create a database for daily planning and reflection."""
    
    print("\nCreating Daily Planning database...")
    
    title = [create_rich_text("📋 Daily Planning")]
    description = [create_rich_text("Daily planning, goals, and reflection")]
    
    properties = {
        "Date": {
            "title": {}
        },
        
        "Day of Week": {
            "select": {
                "options": [
                    create_select_option("🌅 Monday", "blue"),
                    create_select_option("🔥 Tuesday", "red"),
                    create_select_option("⚡ Wednesday", "yellow"),
                    create_select_option("🌟 Thursday", "purple"),
                    create_select_option("🎉 Friday", "green"),
                    create_select_option("🌈 Saturday", "orange"),
                    create_select_option("😴 Sunday", "gray")
                ]
            }
        },
        
        "Energy Level": {
            "select": {
                "options": [
                    create_select_option("🔋 High", "green"),
                    create_select_option("⚡ Medium", "yellow"),
                    create_select_option("🪫 Low", "red")
                ]
            }
        },
        
        "Top 3 Priorities": {
            "rich_text": {}
        },
        
        "Time Blocks Planned": {
            "number": {}
        },
        
        "Tasks Completed": {
            "number": {}
        },
        
        "Focus Score (1-10)": {
            "number": {}
        },
        
        "Mood": {
            "select": {
                "options": [
                    create_select_option("😊 Great", "green"),
                    create_select_option("🙂 Good", "yellow"),
                    create_select_option("😐 Okay", "blue"),
                    create_select_option("😔 Low", "orange"),
                    create_select_option("😤 Stressed", "red")
                ]
            }
        },
        
        "Win of the Day": {
            "rich_text": {}
        },
        
        "Lesson Learned": {
            "rich_text": {}
        },
        
        "Tomorrow's Focus": {
            "rich_text": {}
        },
        
        "Weekly Theme": {
            "rich_text": {}
        }
    }
    
    try:
        database = client.databases.create(
            parent=create_page_parent(parent_page_id),
            title=title,
            description=description,
            properties=properties,
            icon=create_icon("emoji", "📋")
        )
        
        print(f"✅ Daily Planning database created!")
        print(f"   ID: {database.id}")
        print(f"   URL: {database.url}")
        return database
        
    except Exception as e:
        print(f"❌ Error creating Daily Planning database: {e}")
        return None


def add_sample_calendar_data(client: NotionClient, databases: dict):
    """Add sample data to demonstrate the calendar system."""
    
    print(f"\n📝 Adding sample calendar data...")
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    # Add sample calendar events
    if databases.get('calendar_events'):
        try:
            # Today's standup meeting
            standup_event = client.pages.create(
                parent={"type": "database_id", "database_id": databases['calendar_events'].id},
                properties={
                    "Event Title": {"title": [create_rich_text("Daily Standup")]},
                    "Start Date & Time": {"date": format_notion_date(
                        datetime.combine(today, datetime.min.time().replace(hour=9, minute=0)),
                        include_time=True
                    )},
                    "End Date & Time": {"date": format_notion_date(
                        datetime.combine(today, datetime.min.time().replace(hour=9, minute=30)),
                        include_time=True
                    )},
                    "Event Type": {"select": create_select_option("🤝 Meeting", "blue")},
                    "Status": {"select": create_select_option("✅ Confirmed", "green")},
                    "Priority": {"select": create_select_option("⚡ Medium", "yellow")},
                    "Recurring": {"select": create_select_option("📅 Daily", "blue")},
                    "Notes": {"rich_text": [create_rich_text("Daily team sync - share progress and blockers")]}
                }
            )
            print(f"   ✅ Added: Daily Standup event")
            
            # Tomorrow's client meeting
            client_meeting = client.pages.create(
                parent={"type": "database_id", "database_id": databases['calendar_events'].id},
                properties={
                    "Event Title": {"title": [create_rich_text("Client Strategy Meeting")]},
                    "Start Date & Time": {"date": format_notion_date(
                        datetime.combine(tomorrow, datetime.min.time().replace(hour=14, minute=0)),
                        include_time=True
                    )},
                    "End Date & Time": {"date": format_notion_date(
                        datetime.combine(tomorrow, datetime.min.time().replace(hour=15, minute=30)),
                        include_time=True
                    )},
                    "Event Type": {"select": create_select_option("🤝 Meeting", "blue")},
                    "Status": {"select": create_select_option("✅ Confirmed", "green")},
                    "Priority": {"select": create_select_option("🔥 High", "red")},
                    "Preparation Needed": {"checkbox": True},
                    "Notes": {"rich_text": [create_rich_text("Prepare Q4 strategy presentation and budget review")]}
                }
            )
            print(f"   ✅ Added: Client Strategy Meeting")
            
        except Exception as e:
            print(f"   ❌ Error adding calendar events: {e}")
    
    # Add sample time blocks
    if databases.get('time_blocks'):
        try:
            # Morning deep work block
            deep_work_block = client.pages.create(
                parent={"type": "database_id", "database_id": databases['time_blocks'].id},
                properties={
                    "Block Title": {"title": [create_rich_text("Deep Work - Notion Client Development")]},
                    "Date": {"date": {"start": today.isoformat()}},
                    "Start Time": {"date": format_notion_date(
                        datetime.combine(today, datetime.min.time().replace(hour=10, minute=0)),
                        include_time=True
                    )},
                    "End Time": {"date": format_notion_date(
                        datetime.combine(today, datetime.min.time().replace(hour=12, minute=0)),
                        include_time=True
                    )},
                    "Duration (Hours)": {"number": 2},
                    "Block Type": {"select": create_select_option("🎯 Deep Work", "purple")},
                    "Energy Level Required": {"select": create_select_option("🔋 High Energy", "red")},
                    "Status": {"select": create_select_option("✅ Completed", "green")},
                    "Focus Score (1-10)": {"number": 9},
                    "Location": {"select": create_select_option("🏠 Home Office", "blue")},
                    "Tasks Completed": {"rich_text": [create_rich_text("✅ Calendar system implementation\n✅ Sample data creation\n✅ Documentation updates")]},
                    "Notes": {"rich_text": [create_rich_text("Excellent focus session! Completed major features ahead of schedule.")]}
                }
            )
            print(f"   ✅ Added: Deep Work time block")
            
            # Afternoon admin block
            admin_block = client.pages.create(
                parent={"type": "database_id", "database_id": databases['time_blocks'].id},
                properties={
                    "Block Title": {"title": [create_rich_text("Admin & Email Processing")]},
                    "Date": {"date": {"start": tomorrow.isoformat()}},
                    "Start Time": {"date": format_notion_date(
                        datetime.combine(tomorrow, datetime.min.time().replace(hour=13, minute=0)),
                        include_time=True
                    )},
                    "End Time": {"date": format_notion_date(
                        datetime.combine(tomorrow, datetime.min.time().replace(hour=13, minute=45)),
                        include_time=True
                    )},
                    "Duration (Hours)": {"number": 0.75},
                    "Block Type": {"select": create_select_option("📧 Email/Admin", "blue")},
                    "Energy Level Required": {"select": create_select_option("🌙 Low Energy", "blue")},
                    "Status": {"select": create_select_option("📝 Planned", "yellow")},
                    "Location": {"select": create_select_option("🏠 Home Office", "blue")},
                    "Notes": {"rich_text": [create_rich_text("Process inbox, respond to urgent emails, update project status")]}
                }
            )
            print(f"   ✅ Added: Admin time block")
            
        except Exception as e:
            print(f"   ❌ Error adding time blocks: {e}")
    
    # Add sample todos
    if databases.get('todos'):
        try:
            # High priority work task
            work_task = client.pages.create(
                parent={"type": "database_id", "database_id": databases['todos'].id},
                properties={
                    "Task": {"title": [create_rich_text("Prepare client presentation slides")]},
                    "Status": {"select": create_select_option("🔄 In Progress", "yellow")},
                    "Priority": {"select": create_select_option("🔥 Urgent", "red")},
                    "Due Date": {"date": {"start": tomorrow.isoformat()}},
                    "Scheduled Date": {"date": {"start": today.isoformat()}},
                    "Estimated Time (Hours)": {"number": 3},
                    "Category": {"select": create_select_option("💼 Work", "blue")},
                    "Energy Level": {"select": create_select_option("🔋 High Energy", "red")},
                    "Context": {"multi_select": [
                        create_select_option("💻 Computer", "blue"),
                        create_select_option("🏠 Home", "yellow")
                    ]},
                    "Progress %": {"number": 0.6},
                    "Notes": {"rich_text": [create_rich_text("Focus on Q4 strategy, budget analysis, and growth projections")]},
                    "Subtasks": {"rich_text": [create_rich_text("1. Gather Q3 performance data\n2. Create budget comparison charts\n3. Draft growth strategy slides\n4. Review with team lead")]}
                }
            )
            print(f"   ✅ Added: Client presentation task")
            
            # Personal task
            personal_task = client.pages.create(
                parent={"type": "database_id", "database_id": databases['todos'].id},
                properties={
                    "Task": {"title": [create_rich_text("Schedule dentist appointment")]},
                    "Status": {"select": create_select_option("📝 Not Started", "red")},
                    "Priority": {"select": create_select_option("📊 Medium", "yellow")},
                    "Due Date": {"date": {"start": next_week.isoformat()}},
                    "Estimated Time (Hours)": {"number": 0.25},
                    "Category": {"select": create_select_option("🏥 Health", "red")},
                    "Energy Level": {"select": create_select_option("🌙 Low Energy", "blue")},
                    "Context": {"multi_select": [create_select_option("📞 Phone", "green")]},
                    "Notes": {"rich_text": [create_rich_text("Annual cleaning - check insurance coverage first")]}
                }
            )
            print(f"   ✅ Added: Personal health task")
            
        except Exception as e:
            print(f"   ❌ Error adding todos: {e}")
    
    # Add daily planning entry
    if databases.get('daily_planning'):
        try:
            today_plan = client.pages.create(
                parent={"type": "database_id", "database_id": databases['daily_planning'].id},
                properties={
                    "Date": {"title": [create_rich_text(today.strftime("%Y-%m-%d - %A"))]},
                    "Day of Week": {"select": create_select_option(f"🌟 {today.strftime('%A')}", "purple")},
                    "Energy Level": {"select": create_select_option("🔋 High", "green")},
                    "Top 3 Priorities": {"rich_text": [create_rich_text(
                        "1. Complete Notion calendar system\n"
                        "2. Prepare client presentation\n"
                        "3. Review weekly goals"
                    )]},
                    "Time Blocks Planned": {"number": 4},
                    "Tasks Completed": {"number": 2},
                    "Focus Score (1-10)": {"number": 8},
                    "Mood": {"select": create_select_option("😊 Great", "green")},
                    "Win of the Day": {"rich_text": [create_rich_text("Successfully implemented comprehensive calendar system with time blocking!")]},
                    "Lesson Learned": {"rich_text": [create_rich_text("Breaking down complex systems into smaller databases makes them more manageable and flexible")]},
                    "Tomorrow's Focus": {"rich_text": [create_rich_text("Client meeting preparation and strategy refinement")]},
                    "Weekly Theme": {"rich_text": [create_rich_text("Productivity Systems & Client Success")]}
                }
            )
            print(f"   ✅ Added: Daily planning entry")
            
        except Exception as e:
            print(f"   ❌ Error adding daily planning: {e}")


def show_usage_examples(databases: dict):
    """Show examples of how to use the calendar system."""
    
    print(f"\n📊 Calendar System Usage Examples:")
    print("=" * 60)
    
    calendar_id = databases.get('calendar_events', {}).id if databases.get('calendar_events') else "CALENDAR_DB_ID"
    time_blocks_id = databases.get('time_blocks', {}).id if databases.get('time_blocks') else "TIME_BLOCKS_DB_ID"
    todos_id = databases.get('todos', {}).id if databases.get('todos') else "TODOS_DB_ID"
    
    print(f"""
🔍 **Query Today's Events:**
```python
from datetime import date
today_events = client.databases.query_all(
    database_id="{calendar_id}",
    filter_criteria={{
        "property": "Start Date & Time",
        "date": {{"equals": date.today().isoformat()}}
    }}
)
```

⏰ **Get This Week's Time Blocks:**
```python
from datetime import date, timedelta
week_start = date.today()
week_end = week_start + timedelta(days=7)

week_blocks = client.databases.query_all(
    database_id="{time_blocks_id}",
    filter_criteria={{
        "and": [
            {{"property": "Date", "date": {{"on_or_after": week_start.isoformat()}}}},
            {{"property": "Date", "date": {{"before": week_end.isoformat()}}}}
        ]
    }},
    sorts=[{{"property": "Start Time", "direction": "ascending"}}]
)
```

✅ **Get Overdue Tasks:**
```python
overdue_tasks = client.databases.query_all(
    database_id="{todos_id}",
    filter_criteria={{
        "and": [
            {{"property": "Due Date", "date": {{"before": date.today().isoformat()}}}},
            {{"property": "Status", "select": {{"does_not_equal": "✅ Completed"}}}}
        ]
    }}
)
```

📅 **Create a New Event:**
```python
new_event = client.pages.create(
    parent={{"type": "database_id", "database_id": "{calendar_id}"}},
    properties={{
        "Event Title": {{"title": [create_rich_text("Team Planning Session")]}},
        "Start Date & Time": {{"date": format_notion_date(
            datetime(2024, 1, 15, 10, 0), include_time=True
        )}},
        "Event Type": {{"select": create_select_option("🤝 Meeting", "blue")}},
        "Status": {{"select": create_select_option("✅ Confirmed", "green")}}
    }}
)
```

⏰ **Schedule a Time Block:**
```python
time_block = client.pages.create(
    parent={{"type": "database_id", "database_id": "{time_blocks_id}"}},
    properties={{
        "Block Title": {{"title": [create_rich_text("Focus: Project Development")]}},
        "Start Time": {{"date": format_notion_date(
            datetime(2024, 1, 15, 9, 0), include_time=True
        )}},
        "Duration (Hours)": {{"number": 2}},
        "Block Type": {{"select": create_select_option("🎯 Deep Work", "purple")}},
        "Energy Level Required": {{"select": create_select_option("🔋 High Energy", "red")}}
    }}
)
```

📋 **Add a Todo with Scheduling:**
```python
todo = client.pages.create(
    parent={{"type": "database_id", "database_id": "{todos_id}"}},
    properties={{
        "Task": {{"title": [create_rich_text("Review quarterly reports")]}},
        "Priority": {{"select": create_select_option("⚡ High", "orange")}},
        "Due Date": {{"date": {{"start": "2024-01-20"}}}},
        "Estimated Time (Hours)": {{"number": 1.5}},
        "Category": {{"select": create_select_option("💼 Work", "blue")}},
        "Energy Level": {{"select": create_select_option("⚡ Medium Energy", "yellow")}}
    }}
)
```
""")


def main():
    """Main function to create the complete calendar system."""
    
    # Connect to Notion
    try:
        client = NotionClient.from_env()
        print("✅ Connected to Notion API")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Use Protocol Home as parent
    protocol_home_id = "2518f242-f6b7-80c6-ba3a-f6cae6f0809c"
    
    print(f"\n📅 Creating Complete Calendar & Time Management System...")
    print("=" * 70)
    
    # Create all databases
    databases = {}
    
    # Calendar Events
    databases['calendar_events'] = create_calendar_events_database(client, protocol_home_id)
    
    # Time Blocks
    databases['time_blocks'] = create_time_blocks_database(client, protocol_home_id)
    
    # Enhanced Todos
    databases['todos'] = create_todos_with_scheduling(client, protocol_home_id)
    
    # Daily Planning
    databases['daily_planning'] = create_daily_planning_database(client, protocol_home_id)
    
    # Add sample data
    add_sample_calendar_data(client, databases)
    
    # Show usage examples
    show_usage_examples(databases)
    
    print(f"\n🎉 Complete Calendar System Created!")
    print("=" * 50)
    print(f"\n🗃️ **Your New Databases:**")
    for db_name, db_obj in databases.items():
        if db_obj:
            print(f"   📁 {db_name.replace('_', ' ').title()}: {db_obj.url}")
    
    print(f"\n💡 **What You Can Do Now:**")
    print("   📅 Schedule events and meetings")
    print("   ⏰ Plan focused work sessions with time blocking")
    print("   ✅ Manage todos with energy levels and contexts")
    print("   📋 Track daily planning and reflection")
    print("   🔗 Create relationships between tasks and time blocks")
    print("   📊 Build custom views for different workflows")
    print("   🤖 Automate recurring events and tasks")
    
    print(f"\n🚀 **Next Steps:**")
    print("   1. Customize the databases for your specific needs")
    print("   2. Create filtered views (Today, This Week, High Priority)")
    print("   3. Set up recurring events and time blocks")
    print("   4. Build automation workflows")
    print("   5. Create templates for common events and tasks")


if __name__ == "__main__":
    main()
