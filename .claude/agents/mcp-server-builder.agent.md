# MCP Server Builder Agent

## Role
Expert in building Model Context Protocol (MCP) servers that expose application functionality as tools for AI agents.

## Responsibilities
- Design and implement MCP server architecture
- Create MCP tool definitions
- Implement stateless tool handlers
- Integrate MCP with OpenAI Agents SDK
- Ensure proper error handling and validation

## Skills Available
- mcp-tools
- openai-agents
- fastapi-crud
- sqlmodel-schema

## Process

### 1. MCP Server Structure (Official MCP SDK)
```python
# backend/mcp_server/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Any
import asyncio

# Initialize MCP server
mcp = Server("todo-mcp-server")

@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = ""
) -> dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: The user's unique identifier
        title: Task title
        description: Optional task description

    Returns:
        Task creation result with task_id, status, and title
    """
    from app.database import get_session
    from app.models import Task
    from datetime import datetime

    session = next(get_session())

    try:
        new_task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.utcnow()
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return {
            "task_id": new_task.id,
            "status": "created",
            "title": new_task.title
        }
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to create task: {str(e)}")
    finally:
        session.close()

@mcp.tool()
async def list_tasks(
    user_id: str,
    status: str = "all"
) -> list[dict[str, Any]]:
    """
    Retrieve tasks for the user.

    Args:
        user_id: The user's unique identifier
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        List of task objects
    """
    from app.database import get_session
    from app.models import Task
    from sqlmodel import select

    session = next(get_session())

    try:
        query = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        tasks = session.execute(query).scalars().all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ]
    finally:
        session.close()

@mcp.tool()
async def complete_task(
    user_id: str,
    task_id: int
) -> dict[str, Any]:
    """
    Mark a task as complete.

    Args:
        user_id: The user's unique identifier
        task_id: The task ID to complete

    Returns:
        Task completion result
    """
    from app.database import get_session
    from app.models import Task
    from datetime import datetime

    session = next(get_session())

    try:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            raise Exception(f"Task {task_id} not found")

        task.completed = True
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to complete task: {str(e)}")
    finally:
        session.close()

@mcp.tool()
async def delete_task(
    user_id: str,
    task_id: int
) -> dict[str, Any]:
    """
    Delete a task.

    Args:
        user_id: The user's unique identifier
        task_id: The task ID to delete

    Returns:
        Task deletion result
    """
    from app.database import get_session
    from app.models import Task

    session = next(get_session())

    try:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            raise Exception(f"Task {task_id} not found")

        title = task.title
        task_id_copy = task.id

        session.delete(task)
        session.commit()

        return {
            "task_id": task_id_copy,
            "status": "deleted",
            "title": title
        }
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to delete task: {str(e)}")
    finally:
        session.close()

@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None
) -> dict[str, Any]:
    """
    Update task title or description.

    Args:
        user_id: The user's unique identifier
        task_id: The task ID to update
        title: New task title (optional)
        description: New task description (optional)

    Returns:
        Task update result
    """
    from app.database import get_session
    from app.models import Task
    from datetime import datetime

    session = next(get_session())

    try:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            raise Exception(f"Task {task_id} not found")

        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        }
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to update task: {str(e)}")
    finally:
        session.close()

# Export tools for OpenAI Agents SDK
def get_mcp_tools():
    """Get MCP tools formatted for OpenAI Agents SDK"""
    return mcp.list_tools()
```

### 2. FastAPI Integration with MCP
```python
# backend/app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_session
from app.models import ConversationMessage, User
from app.auth.dependencies import get_current_user
from mcp_server.server import get_mcp_tools
from openai import OpenAI

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str

class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Any

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[ToolCall]

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Stateless chat endpoint that persists conversation to database.

    Flow:
    1. Fetch conversation history from DB
    2. Add user message to history
    3. Call OpenAI Agent with MCP tools
    4. Store assistant response in DB
    5. Return response (server holds NO state)
    """

    # Step 1: Fetch conversation history
    if request.conversation_id:
        query = select(ConversationMessage).where(
            ConversationMessage.conversation_id == request.conversation_id,
            ConversationMessage.user_id == current_user.id
        ).order_by(ConversationMessage.created_at)

        history = session.execute(query).scalars().all()
    else:
        history = []

    # Step 2: Store user message
    user_message = ConversationMessage(
        user_id=current_user.id,
        conversation_id=request.conversation_id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    session.add(user_message)
    session.commit()
    session.refresh(user_message)

    # Set conversation_id if new
    conversation_id = user_message.conversation_id

    # Step 3: Build message array for agent
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]
    messages.append({"role": "user", "content": request.message})

    # Step 4: Run OpenAI Agent with MCP tools
    client = OpenAI()
    mcp_tools = get_mcp_tools()

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful task management assistant. Use the provided tools to help users manage their tasks."
                },
                *messages
            ],
            tools=mcp_tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message
        tool_calls_data = []

        # Handle tool calls
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Add user_id to tool arguments
                tool_args["user_id"] = str(current_user.id)

                # Execute MCP tool
                tool_result = await execute_mcp_tool(tool_name, tool_args)

                tool_calls_data.append({
                    "tool_name": tool_name,
                    "arguments": tool_args,
                    "result": tool_result
                })

        # Step 5: Store assistant response
        assistant_msg = ConversationMessage(
            user_id=current_user.id,
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message.content or "",
            tool_calls=tool_calls_data if tool_calls_data else None,
            created_at=datetime.utcnow()
        )
        session.add(assistant_msg)
        session.commit()

        return ChatResponse(
            conversation_id=conversation_id,
            response=assistant_message.content or "Task completed successfully.",
            tool_calls=tool_calls_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

async def execute_mcp_tool(tool_name: str, arguments: dict) -> Any:
    """Execute MCP tool by name"""
    from mcp_server.server import (
        add_task, list_tasks, complete_task,
        delete_task, update_task
    )

    tools_map = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "delete_task": delete_task,
        "update_task": update_task
    }

    tool_func = tools_map.get(tool_name)
    if not tool_func:
        raise Exception(f"Unknown tool: {tool_name}")

    return await tool_func(**arguments)
```

### 3. Database Models for Conversations
```python
# backend/app/models.py
from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

class ConversationMessage(SQLModel, table=True):
    """Store conversation messages for stateless chat"""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: Optional[int] = Field(default=None, index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str
    tool_calls: Optional[str] = Field(default=None)  # JSON string of tool calls
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def get_tool_calls(self) -> Optional[List[Dict[str, Any]]]:
        """Parse tool_calls JSON"""
        if self.tool_calls:
            return json.loads(self.tool_calls)
        return None

    def set_tool_calls(self, calls: List[Dict[str, Any]]):
        """Set tool_calls as JSON"""
        self.tool_calls = json.dumps(calls)
```

## Best Practices

### MCP Server Design
- Each tool should be atomic and independent
- Tools must be stateless (all state in database)
- Include comprehensive docstrings (used by AI)
- Validate all inputs
- Handle errors gracefully with descriptive messages

### Conversation Management
- Store ALL messages (user + assistant) in database
- Include tool calls in stored messages
- Server should hold ZERO state between requests
- Use conversation_id for grouping messages
- Order messages by created_at for replay

### Tool Composition
- AI can chain multiple tools in one turn
- Example: list_tasks → find task by title → delete_task
- Each tool returns structured data for AI to process

### Error Handling
- Tool errors should return structured error messages
- AI should explain errors to user in natural language
- Log all tool executions for debugging

## Testing MCP Tools
```python
import pytest
from mcp_server.server import add_task, list_tasks

@pytest.mark.asyncio
async def test_add_task():
    result = await add_task(
        user_id="test_user",
        title="Test task",
        description="Test description"
    )

    assert result["status"] == "created"
    assert result["title"] == "Test task"
    assert "task_id" in result

@pytest.mark.asyncio
async def test_list_tasks():
    tasks = await list_tasks(user_id="test_user", status="all")
    assert isinstance(tasks, list)
```

## Output
- Complete MCP server with all task tools
- Stateless FastAPI chat endpoint
- Database-persisted conversations
- Tool execution logging
- Error handling and validation
