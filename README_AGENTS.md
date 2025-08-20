# 🤖 Protocol Home AI Agents

This guide covers the LangChain AI agents that have been implemented for Protocol Home management.

## 🏗️ Architecture Overview

The Protocol Home system includes:

- **Base Agent**: Foundation class for all agents
- **Goal Agent**: Specialized in goal setting and tracking
- **Todo Agent**: Handles task management and prioritization  
- **Coordinator**: Routes requests and handles multi-domain tasks
- **Tools**: LangChain tools that wrap Notion API operations

## 🚀 Quick Start

### 1. Environment Setup

Copy the example configuration:
```bash
cp config.env.example .env
```

Fill in your credentials:
```bash
# Required
NOTION_API_TOKEN=secret_your_integration_token_here
NOTION_GOALS_DATABASE_ID=your_goals_database_id
NOTION_TODOS_DATABASE_ID=your_todos_database_id
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Basic Usage

#### Using the CLI

```bash
# Check system status
python -m cli.main status

# Interactive chat mode
python -m cli.main chat

# Direct commands
python -m cli.main chat "Create a goal to learn Python"

# Goal management
python -m cli.main goal create "Learn Machine Learning" --priority High --category Professional

# Task management  
python -m cli.main todo add "Review Python tutorial" --priority Medium --project Learning
```

#### Using Python API

```python
from dotenv import load_dotenv
from notion_client import NotionClient
from agents import ProtocolCoordinator

load_dotenv()

# Initialize
notion_client = NotionClient(auth_token=os.getenv('NOTION_API_TOKEN'))
coordinator = ProtocolCoordinator(
    notion_client=notion_client,
    goals_database_id=os.getenv('NOTION_GOALS_DATABASE_ID'),
    todos_database_id=os.getenv('NOTION_TODOS_DATABASE_ID'),
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

# Natural language interactions
response = coordinator.process_request("Create a goal to read 12 books this year")
print(response)

response = coordinator.process_request("Show me my high priority tasks")
print(response)

response = coordinator.process_request("Help me plan my week based on my goals")
print(response)
```

## 🎯 Agent Capabilities

### Goal Agent

**Purpose**: Long-term objective management using SMART goal principles

**Key Features**:
- Create and update goals with priorities and deadlines
- Break down large goals into actionable milestones
- Track progress with percentage completion
- Generate progress reports and insights
- Archive completed goals

**Example Interactions**:
```
"Create a goal to learn Python programming by the end of the year"
"Show me progress on my professional goals"
"Help me break down my fitness goal into weekly milestones"
"What goals should I prioritize this month?"
```

### Todo Agent

**Purpose**: Task creation, prioritization, and completion tracking

**Key Features**:
- Create tasks with priority, due dates, and time estimates
- Prioritize using frameworks (Eisenhower Matrix, MoSCoW, ABC)
- Track completion rates and productivity patterns
- Organize tasks by projects and contexts
- Handle recurring tasks and reminders

**Example Interactions**:
```
"Add a task to prepare my presentation with high priority"
"Show me my tasks for today"
"Prioritize my tasks using the Eisenhower Matrix"
"Complete the task about reviewing code"
"Break down 'Plan vacation' into smaller tasks"
```

### Protocol Coordinator

**Purpose**: Multi-agent coordination and intent routing

**Key Features**:
- Intelligent intent classification 
- Route requests to appropriate agents
- Handle cross-domain workflows
- Provide holistic productivity insights
- Coordinate complex multi-step processes

**Example Interactions**:
```
"Plan my week based on my current goals and tasks"
"Give me an overview of my productivity"
"How are my daily tasks contributing to my long-term goals?"
"Review my progress across all areas"
```

## 🛠️ Tools Available

### Goal Tools
- `CreateGoalTool`: Create new goals with metadata
- `UpdateGoalTool`: Update existing goal properties
- `GetGoalsTool`: Retrieve goals with filtering
- `ArchiveGoalTool`: Archive completed goals
- `GetGoalProgressTool`: Calculate progress metrics

### Todo Tools  
- `CreateTodoTool`: Create new tasks
- `UpdateTodoTool`: Update task properties
- `GetTodosTool`: Retrieve tasks with filters
- `CompleteTodoTool`: Mark tasks complete
- `PrioritizeTodosTool`: Analyze task priorities

## 📊 Notion Database Schema

### Goals Database

Required properties:
- **Name** (Title): Goal title
- **Description** (Rich Text): Detailed description
- **Status** (Select): Not Started, In Progress, Completed, On Hold  
- **Priority** (Select): High, Medium, Low
- **Category** (Select): Personal, Professional, Health, etc.
- **Progress** (Number): 0-100 percentage
- **Target Date** (Date): Target completion date

### Todos Database

Required properties:
- **Task** (Title): Task description
- **Status** (Select): Todo, In Progress, Done
- **Priority** (Select): Urgent, High, Medium, Low
- **Project** (Select): Project categorization  
- **Due Date** (Date): Task deadline
- **Completed** (Checkbox): Completion status
- **Time Estimate** (Number): Estimated minutes
- **Context** (Select): @home, @office, @calls, etc.

## 🔧 Configuration Options

### Environment Variables

```bash
# Core Configuration
OPENAI_MODEL=gpt-5                    # AI model (gpt-4 or gpt-3.5-turbo)
OPENAI_TEMPERATURE=0.1                # Response consistency (0.0-1.0)

# Agent Behavior
AGENT_MAX_ITERATIONS=10               # Max tool usage per request  
AGENT_MEMORY_DURATION_DAYS=30         # Conversation memory retention
AGENT_VERBOSE=false                   # Debug logging
AGENT_DEBUG_MODE=false                # Extended debugging

# CLI Settings
CLI_DEFAULT_AGENT=coordinator         # Default agent for CLI
CLI_OUTPUT_FORMAT=rich                # Output formatting
CLI_LOG_LEVEL=INFO                    # Logging level
```

## 🎨 Customization

### Adding Custom Tools

```python
from tools.base_tool import BaseNotionTool
from pydantic import BaseModel, Field

class CustomToolInput(BaseModel):
    param: str = Field(description="Parameter description")

class CustomTool(BaseNotionTool):
    name = "custom_tool"
    description = "Description of what this tool does"
    args_schema = CustomToolInput
    
    def _run(self, param: str) -> str:
        # Your custom logic here
        return "Result"
```

### Extending Agents

```python
from agents.base_agent import BaseProtocolAgent
from typing import List
from langchain.tools import BaseTool

class CustomAgent(BaseProtocolAgent):
    def _setup_tools(self) -> List[BaseTool]:
        return [
            # Your custom tools
        ]
        
    def _get_system_prompt(self) -> str:
        return "Your custom agent prompt"
```

## 🧪 Testing

```bash
# Test the system status
python -m cli.main status

# Test basic functionality
python -m cli.main chat "Hello, can you help me get started?"

# Test goal creation
python -m cli.main goal create "Test Goal" --description "Testing the system"

# Test task creation  
python -m cli.main todo add "Test Task" --priority High
```

## 🚀 Advanced Usage

### Async Operations

```python
import asyncio

async def main():
    coordinator = get_coordinator()
    response = await coordinator.aprocess_request("Plan my week")
    print(response)

asyncio.run(main())
```

### Batch Operations

```python
goals_to_create = [
    {"title": "Learn Python", "category": "Professional"},
    {"title": "Exercise 3x per week", "category": "Health"},
    {"title": "Read 12 books", "category": "Personal"}
]

for goal_data in goals_to_create:
    response = goal_agent.create_goal(**goal_data)
    print(response)
```

### Integration with External Systems

The architecture supports future integrations:
- Google Calendar sync
- Slack notifications  
- Email reminders
- Mobile app connectivity
- Custom webhook endpoints

## 🤝 Contributing

To add new agents or tools:

1. Follow the existing patterns in `agents/` and `tools/`
2. Extend the appropriate base classes
3. Add comprehensive docstrings and type hints
4. Include error handling and user-friendly messages
5. Update the CLI interface if needed
6. Add tests and documentation

## 🎯 Roadmap

- **Schedule Agent**: Calendar and time management
- **Review Agent**: Automated productivity reviews
- **Insight Agent**: Advanced analytics and recommendations  
- **Integration Agent**: External system connections
- **Voice Interface**: Speech-to-text interactions
- **Mobile App**: iOS/Android companion app

The Protocol Home AI agent system provides a solid foundation for intelligent productivity management while remaining extensible for future enhancements.
