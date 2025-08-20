"""
LangChain tools for todo/task management in Notion.

This module contains specialized tools for creating, updating, and managing
todos and tasks in the Protocol Home system.
"""

from typing import Type, Optional, List
from pydantic import BaseModel, Field
from .base_tool import BaseNotionTool


class CreateTodoInput(BaseModel):
    """Input schema for creating a todo."""
    title: str = Field(description="Todo title/description")
    priority: str = Field(description="Priority level (Urgent/High/Medium/Low)", default="Medium")
    project: Optional[str] = Field(description="Project or category", default=None)
    due_date: Optional[str] = Field(description="Due date (YYYY-MM-DD)", default=None)
    time_estimate: Optional[int] = Field(description="Estimated time in minutes", default=None)
    context: Optional[str] = Field(description="Context or location (@home, @office, etc.)", default=None)


class CreateTodoTool(BaseNotionTool):
    """Tool for creating todos in Notion."""
    
    name: str = "create_todo"
    description: str = "Create a new todo/task with title, priority, project, due date, and time estimate"
    args_schema: Type[BaseModel] = CreateTodoInput
    todos_database_id: str = Field(description="The ID of the todos database")
    
    def __init__(self, notion_client, todos_database_id: str, **kwargs):
        super().__init__(notion_client=notion_client, todos_database_id=todos_database_id, **kwargs)
    
    def _run(self, title: str, priority: str = "Medium", project: Optional[str] = None,
             due_date: Optional[str] = None, time_estimate: Optional[int] = None,
             context: Optional[str] = None) -> str:
        """Create a todo in Notion."""
        try:
            # Prepare properties
            properties = {
                "Task": {"title": self._format_notion_title(title)},
                "Priority": {"select": self._format_notion_select(priority)},
                "Status": {"select": self._format_notion_select("Todo")},
                "Completed": {"checkbox": False},
            }
            
            # Add optional properties
            if project:
                properties["Project"] = {"select": self._format_notion_select(project)}
            if due_date:
                date_obj = self._format_notion_date(due_date)
                if date_obj:
                    properties["Due Date"] = {"date": date_obj}
            if time_estimate:
                properties["Time Estimate"] = {"number": time_estimate}
            if context:
                properties["Context"] = {"select": self._format_notion_select(context)}
            
            # Create the todo page
            todo_page = self.notion_client.pages.create(
                parent={"database_id": self.todos_database_id},
                properties=properties
            )
            
            page_id = todo_page.id
            return f"✅ Created todo '{title}' successfully! Todo ID: {page_id}"
            
        except Exception as e:
            return self._handle_notion_error(e, "todo creation")


class UpdateTodoInput(BaseModel):
    """Input schema for updating a todo."""
    todo_id: str = Field(description="The ID of the todo to update")
    title: Optional[str] = Field(description="New todo title", default=None)
    priority: Optional[str] = Field(description="New priority level", default=None)
    status: Optional[str] = Field(description="New status (Todo/In Progress/Done)", default=None)
    project: Optional[str] = Field(description="New project", default=None)
    due_date: Optional[str] = Field(description="New due date (YYYY-MM-DD)", default=None)
    completed: Optional[bool] = Field(description="Mark as completed", default=None)


class UpdateTodoTool(BaseNotionTool):
    """Tool for updating existing todos in Notion."""
    
    name: str = "update_todo"
    description: str = "Update an existing todo's properties like title, priority, status, due date, etc."
    args_schema: Type[BaseModel] = UpdateTodoInput
    
    def _run(self, todo_id: str, title: Optional[str] = None, priority: Optional[str] = None,
             status: Optional[str] = None, project: Optional[str] = None, 
             due_date: Optional[str] = None, completed: Optional[bool] = None) -> str:
        """Update a todo in Notion."""
        try:
            properties = {}
            
            if title:
                properties["Task"] = {"title": self._format_notion_title(title)}
            if priority:
                properties["Priority"] = {"select": self._format_notion_select(priority)}
            if status:
                properties["Status"] = {"select": self._format_notion_select(status)}
            if project:
                properties["Project"] = {"select": self._format_notion_select(project)}
            if due_date:
                date_obj = self._format_notion_date(due_date)
                if date_obj:
                    properties["Due Date"] = {"date": date_obj}
            if completed is not None:
                properties["Completed"] = {"checkbox": completed}
                if completed:
                    properties["Status"] = {"select": self._format_notion_select("Done")}
            
            if not properties:
                return "❌ No properties specified for update."
            
            self.notion_client.pages.update(page_id=todo_id, properties=properties)
            
            updated_fields = list(properties.keys())
            return f"✅ Updated todo successfully! Updated fields: {', '.join(updated_fields)}"
            
        except Exception as e:
            return self._handle_notion_error(e, "todo update")


class GetTodosInput(BaseModel):
    """Input schema for retrieving todos."""
    status: Optional[str] = Field(description="Filter by status (Todo/In Progress/Done)", default=None)
    priority: Optional[str] = Field(description="Filter by priority", default=None)
    project: Optional[str] = Field(description="Filter by project", default=None)
    due_today: bool = Field(description="Show only todos due today", default=False)
    overdue: bool = Field(description="Show only overdue todos", default=False)
    limit: int = Field(description="Maximum number of todos to return", default=20)


class GetTodosTool(BaseNotionTool):
    """Tool for retrieving todos from Notion with filters."""
    
    name: str = "get_todos"
    description: str = "Retrieve todos with optional filters for status, priority, project, due date"
    args_schema: Type[BaseModel] = GetTodosInput
    todos_database_id: str = Field(description="The ID of the todos database")
    
    def __init__(self, notion_client, todos_database_id: str, **kwargs):
        super().__init__(notion_client=notion_client, todos_database_id=todos_database_id, **kwargs)
    
    def _run(self, status: Optional[str] = None, priority: Optional[str] = None,
             project: Optional[str] = None, due_today: bool = False, 
             overdue: bool = False, limit: int = 20) -> str:
        """Retrieve todos with filters."""
        try:
            filter_conditions = []
            
            if status:
                filter_conditions.append({
                    "property": "Status",
                    "select": {"equals": status}
                })
            
            if priority:
                filter_conditions.append({
                    "property": "Priority",
                    "select": {"equals": priority}
                })
                
            if project:
                filter_conditions.append({
                    "property": "Project",
                    "select": {"equals": project}
                })
            
            # Build query
            query = {
                "database_id": self.todos_database_id,
                "page_size": min(limit, 100),
                "sorts": [
                    {"property": "Priority", "direction": "ascending"},
                    {"property": "Due Date", "direction": "ascending"}
                ]
            }
            
            if filter_conditions:
                if len(filter_conditions) == 1:
                    query["filter"] = filter_conditions[0]
                else:
                    query["filter"] = {"and": filter_conditions}
            
            response = self.notion_client.databases.query(**query)
            todos = response.get("results", [])
            
            if not todos:
                return "📭 No todos found matching your criteria."
            
            # Format results
            result_lines = [f"📋 Found {len(todos)} todo(s):\n"]
            
            for i, todo in enumerate(todos, 1):
                title = self._extract_page_title(todo)
                status_val = self._extract_property_value(todo, "Status") or "Todo"
                priority_val = self._extract_property_value(todo, "Priority") or "Medium"
                project_val = self._extract_property_value(todo, "Project") or "No project"
                due_date = self._extract_property_value(todo, "Due Date") or "No due date"
                completed = self._extract_property_value(todo, "Completed") or False
                
                status_icon = "✅" if completed else "📝"
                
                result_lines.append(
                    f"{status_icon} {i}. **{title}**\n"
                    f"   Status: {status_val} | Priority: {priority_val} | Project: {project_val}\n"
                    f"   Due: {due_date} | ID: {todo['id']}\n"
                )
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return self._handle_notion_error(e, "todo retrieval")


class CompleteTodoInput(BaseModel):
    """Input schema for completing a todo."""
    todo_id: str = Field(description="The ID of the todo to complete")


class CompleteTodoTool(BaseNotionTool):
    """Tool for marking todos as completed."""
    
    name: str = "complete_todo"
    description: str = "Mark a todo as completed"
    args_schema: Type[BaseModel] = CompleteTodoInput
    
    def _run(self, todo_id: str) -> str:
        """Mark a todo as completed."""
        try:
            self.notion_client.pages.update(
                page_id=todo_id,
                properties={
                    "Completed": {"checkbox": True},
                    "Status": {"select": self._format_notion_select("Done")}
                }
            )
            
            return f"🎉 Todo completed successfully! Todo ID: {todo_id}"
            
        except Exception as e:
            return self._handle_notion_error(e, "todo completion")


class PrioritizeTodosInput(BaseModel):
    """Input schema for prioritizing todos."""
    project: Optional[str] = Field(description="Project to prioritize todos for", default=None)
    method: str = Field(description="Prioritization method (eisenhower/moscow/abc)", default="eisenhower")


class PrioritizeTodosTool(BaseNotionTool):
    """Tool for re-prioritizing todos using various frameworks."""
    
    name: str = "prioritize_todos"
    description: str = "Re-prioritize todos using frameworks like Eisenhower Matrix, MoSCoW, or ABC priority"
    args_schema: Type[BaseModel] = PrioritizeTodosInput
    todos_database_id: str = Field(description="The ID of the todos database")
    
    def __init__(self, notion_client, todos_database_id: str, **kwargs):
        super().__init__(notion_client=notion_client, todos_database_id=todos_database_id, **kwargs)
    
    def _run(self, project: Optional[str] = None, method: str = "eisenhower") -> str:
        """Analyze and suggest todo prioritization."""
        try:
            # Get todos to prioritize
            query = {"database_id": self.todos_database_id}
            
            if project:
                query["filter"] = {
                    "property": "Project",
                    "select": {"equals": project}
                }
            
            response = self.notion_client.databases.query(**query)
            todos = response.get("results", [])
            
            if not todos:
                return "📭 No todos found for prioritization."
            
            # Analyze based on method
            if method.lower() == "eisenhower":
                return self._analyze_eisenhower(todos)
            elif method.lower() == "moscow":
                return self._analyze_moscow(todos)
            elif method.lower() == "abc":
                return self._analyze_abc(todos)
            else:
                return f"❌ Unknown prioritization method: {method}. Use: eisenhower, moscow, or abc"
                
        except Exception as e:
            return self._handle_notion_error(e, "todo prioritization")
    
    def _analyze_eisenhower(self, todos: List) -> str:
        """Analyze todos using Eisenhower Matrix."""
        result = ["📊 Eisenhower Matrix Analysis:\n"]
        
        urgent_important = []
        important_not_urgent = []
        urgent_not_important = []
        neither = []
        
        for todo in todos:
            title = self._extract_page_title(todo)
            priority = self._extract_property_value(todo, "Priority") or "Medium"
            due_date = self._extract_property_value(todo, "Due Date")
            
            # Simple heuristic - you might want to make this more sophisticated
            is_urgent = priority in ["Urgent", "High"] or due_date
            is_important = priority in ["Urgent", "High"]
            
            if is_urgent and is_important:
                urgent_important.append(title)
            elif is_important and not is_urgent:
                important_not_urgent.append(title)
            elif is_urgent and not is_important:
                urgent_not_important.append(title)
            else:
                neither.append(title)
        
        result.append("🔥 **Do First (Urgent & Important):**")
        for todo in urgent_important:
            result.append(f"   • {todo}")
        
        result.append("\n📅 **Schedule (Important, Not Urgent):**")
        for todo in important_not_urgent:
            result.append(f"   • {todo}")
            
        result.append("\n⚡ **Delegate (Urgent, Not Important):**")
        for todo in urgent_not_important:
            result.append(f"   • {todo}")
            
        result.append("\n🗑️ **Eliminate (Neither Urgent nor Important):**")
        for todo in neither:
            result.append(f"   • {todo}")
        
        return "\n".join(result)
    
    def _analyze_moscow(self, todos: List) -> str:
        """Analyze todos using MoSCoW method."""
        result = ["📊 MoSCoW Prioritization Analysis:\n"]
        
        must_have = []
        should_have = []
        could_have = []
        wont_have = []
        
        for todo in todos:
            title = self._extract_page_title(todo)
            priority = self._extract_property_value(todo, "Priority") or "Medium"
            
            if priority == "Urgent":
                must_have.append(title)
            elif priority == "High":
                should_have.append(title)
            elif priority == "Medium":
                could_have.append(title)
            else:
                wont_have.append(title)
        
        result.append("🚨 **Must Have:**")
        for todo in must_have:
            result.append(f"   • {todo}")
            
        result.append("\n📈 **Should Have:**")
        for todo in should_have:
            result.append(f"   • {todo}")
            
        result.append("\n💡 **Could Have:**")
        for todo in could_have:
            result.append(f"   • {todo}")
            
        result.append("\n❌ **Won't Have (This Time):**")
        for todo in wont_have:
            result.append(f"   • {todo}")
        
        return "\n".join(result)
    
    def _analyze_abc(self, todos: List) -> str:
        """Analyze todos using ABC priority method."""
        result = ["📊 ABC Priority Analysis:\n"]
        
        a_priority = []
        b_priority = []
        c_priority = []
        
        for todo in todos:
            title = self._extract_page_title(todo)
            priority = self._extract_property_value(todo, "Priority") or "Medium"
            
            if priority in ["Urgent", "High"]:
                a_priority.append(title)
            elif priority == "Medium":
                b_priority.append(title)
            else:
                c_priority.append(title)
        
        result.append("🔴 **A Priority (Critical - Must Do):**")
        for todo in a_priority:
            result.append(f"   • {todo}")
            
        result.append("\n🟡 **B Priority (Important - Should Do):**")
        for todo in b_priority:
            result.append(f"   • {todo}")
            
        result.append("\n🟢 **C Priority (Nice to Have - Could Do):**")
        for todo in c_priority:
            result.append(f"   • {todo}")
        
        return "\n".join(result)
