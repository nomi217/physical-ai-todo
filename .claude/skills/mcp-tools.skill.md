# MCP Tools Development Skill

## Purpose
Create Model Context Protocol (MCP) tools that expose application functionality to AI agents in a standardized way.

## When to Use
- Building AI-powered features
- Exposing backend operations to LLMs
- Creating tool-calling interfaces
- Implementing agentic workflows

## Inputs Required
- **Tool Name**: Descriptive function name
- **Parameters**: Input parameters with types
- **Database Models**: SQLModel classes
- **Business Logic**: What the tool should do

## Process

### 1. Install MCP SDK
```bash
pip install mcp
```

### 2. Tool Definition Pattern
```python
from mcp.server import Server
from mcp.types import Tool
from typing import Any, Optional
import asyncio

mcp = Server("your-app-mcp-server")

@mcp.tool()
async def tool_name(
    user_id: str,
    param1: str,
    param2: Optional[int] = None
) -> dict[str, Any]:
    """
    Clear, descriptive docstring for the AI.
    The AI reads this to understand when and how to use the tool.

    Args:
        user_id: User identifier (always required for multi-user apps)
        param1: Description of parameter
        param2: Optional parameter description

    Returns:
        Structured response with status and data
    """
    try:
        # 1. Validate inputs
        if not param1:
            raise ValueError("param1 is required")

        # 2. Execute business logic
        result = await perform_operation(user_id, param1, param2)

        # 3. Return structured response
        return {
            "status": "success",
            "data": result,
            "message": "Operation completed successfully"
        }

    except Exception as e:
        # Always return structured errors
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to execute tool: {str(e)}"
        }
```

### 3. CRUD Tools Pattern

#### Create Tool
```python
@mcp.tool()
async def create_resource(
    user_id: str,
    name: str,
    description: str = ""
) -> dict[str, Any]:
    """
    Create a new resource for the user.

    Args:
        user_id: The user's ID
        name: Resource name
        description: Optional description

    Returns:
        Created resource with ID
    """
    from app.database import get_session
    from app.models import Resource

    session = next(get_session())

    try:
        resource = Resource(
            user_id=user_id,
            name=name,
            description=description
        )

        session.add(resource)
        session.commit()
        session.refresh(resource)

        return {
            "status": "created",
            "resource_id": resource.id,
            "name": resource.name
        }

    except Exception as e:
        session.rollback()
        raise

    finally:
        session.close()
```

#### Read/List Tool
```python
@mcp.tool()
async def list_resources(
    user_id: str,
    filter_by: Optional[str] = None,
    limit: int = 50
) -> list[dict[str, Any]]:
    """
    Retrieve user's resources with optional filtering.

    Args:
        user_id: The user's ID
        filter_by: Optional filter criteria
        limit: Maximum number of results (default 50)

    Returns:
        List of resource objects
    """
    from app.database import get_session
    from app.models import Resource
    from sqlmodel import select

    session = next(get_session())

    try:
        query = select(Resource).where(Resource.user_id == user_id)

        if filter_by:
            query = query.where(Resource.name.contains(filter_by))

        query = query.limit(limit)

        resources = session.execute(query).scalars().all()

        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "created_at": r.created_at.isoformat()
            }
            for r in resources
        ]

    finally:
        session.close()
```

#### Update Tool
```python
@mcp.tool()
async def update_resource(
    user_id: str,
    resource_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> dict[str, Any]:
    """
    Update a resource's properties.

    Args:
        user_id: The user's ID
        resource_id: ID of resource to update
        name: New name (optional)
        description: New description (optional)

    Returns:
        Updated resource data
    """
    from app.database import get_session
    from app.models import Resource
    from datetime import datetime

    session = next(get_session())

    try:
        resource = session.get(Resource, resource_id)

        if not resource or resource.user_id != user_id:
            raise ValueError(f"Resource {resource_id} not found")

        if name is not None:
            resource.name = name

        if description is not None:
            resource.description = description

        resource.updated_at = datetime.utcnow()

        session.add(resource)
        session.commit()
        session.refresh(resource)

        return {
            "status": "updated",
            "resource_id": resource.id,
            "name": resource.name
        }

    except Exception as e:
        session.rollback()
        raise

    finally:
        session.close()
```

#### Delete Tool
```python
@mcp.tool()
async def delete_resource(
    user_id: str,
    resource_id: int
) -> dict[str, Any]:
    """
    Delete a resource.

    Args:
        user_id: The user's ID
        resource_id: ID of resource to delete

    Returns:
        Deletion confirmation
    """
    from app.database import get_session
    from app.models import Resource

    session = next(get_session())

    try:
        resource = session.get(Resource, resource_id)

        if not resource or resource.user_id != user_id:
            raise ValueError(f"Resource {resource_id} not found")

        name = resource.name

        session.delete(resource)
        session.commit()

        return {
            "status": "deleted",
            "resource_id": resource_id,
            "name": name
        }

    except Exception as e:
        session.rollback()
        raise

    finally:
        session.close()
```

### 4. Complex Multi-Step Tools
```python
@mcp.tool()
async def bulk_complete_tasks(
    user_id: str,
    task_ids: list[int]
) -> dict[str, Any]:
    """
    Mark multiple tasks as complete in one operation.

    Args:
        user_id: The user's ID
        task_ids: List of task IDs to complete

    Returns:
        Summary of completed tasks
    """
    from app.database import get_session
    from app.models import Task
    from datetime import datetime

    session = next(get_session())

    try:
        completed = []
        failed = []

        for task_id in task_ids:
            task = session.get(Task, task_id)

            if task and task.user_id == user_id:
                task.completed = True
                task.updated_at = datetime.utcnow()
                session.add(task)
                completed.append({"id": task.id, "title": task.title})
            else:
                failed.append(task_id)

        session.commit()

        return {
            "status": "completed",
            "completed_count": len(completed),
            "failed_count": len(failed),
            "completed_tasks": completed,
            "failed_task_ids": failed
        }

    except Exception as e:
        session.rollback()
        raise

    finally:
        session.close()
```

### 5. Search/Filter Tools
```python
@mcp.tool()
async def search_tasks(
    user_id: str,
    query: str,
    status: Optional[str] = "all",
    limit: int = 20
) -> list[dict[str, Any]]:
    """
    Search tasks by title or description.

    Args:
        user_id: The user's ID
        query: Search query string
        status: Filter by status ("all", "pending", "completed")
        limit: Maximum results

    Returns:
        Matching tasks
    """
    from app.database import get_session
    from app.models import Task
    from sqlmodel import select, or_

    session = next(get_session())

    try:
        stmt = select(Task).where(Task.user_id == user_id)

        # Text search
        stmt = stmt.where(
            or_(
                Task.title.ilike(f"%{query}%"),
                Task.description.ilike(f"%{query}%")
            )
        )

        # Status filter
        if status == "pending":
            stmt = stmt.where(Task.completed == False)
        elif status == "completed":
            stmt = stmt.where(Task.completed == True)

        stmt = stmt.limit(limit)

        tasks = session.execute(stmt).scalars().all()

        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "relevance": "high" if query.lower() in t.title.lower() else "medium"
            }
            for t in tasks
        ]

    finally:
        session.close()
```

### 6. Analytics/Aggregation Tools
```python
@mcp.tool()
async def get_task_statistics(
    user_id: str
) -> dict[str, Any]:
    """
    Get user's task completion statistics.

    Args:
        user_id: The user's ID

    Returns:
        Task statistics and insights
    """
    from app.database import get_session
    from app.models import Task
    from sqlmodel import select, func

    session = next(get_session())

    try:
        # Total tasks
        total = session.execute(
            select(func.count()).select_from(Task).where(Task.user_id == user_id)
        ).scalar()

        # Completed tasks
        completed = session.execute(
            select(func.count()).select_from(Task).where(
                Task.user_id == user_id,
                Task.completed == True
            )
        ).scalar()

        # Pending tasks
        pending = total - completed

        # Completion rate
        completion_rate = (completed / total * 100) if total > 0 else 0

        return {
            "total_tasks": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": round(completion_rate, 2),
            "status": "success"
        }

    finally:
        session.close()
```

### 7. Exporting Tools for OpenAI
```python
# mcp_server/server.py
from mcp.server import Server

mcp = Server("todo-mcp-server")

# ... define all tools with @mcp.tool() ...

def get_mcp_tools_for_openai():
    """
    Export MCP tools in OpenAI function calling format.

    Returns:
        List of tool definitions for OpenAI API
    """
    tools = []

    for tool in mcp.list_tools():
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        })

    return tools
```

### 8. Tool Execution Router
```python
async def execute_mcp_tool(tool_name: str, arguments: dict) -> Any:
    """
    Execute an MCP tool by name with given arguments.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments

    Returns:
        Tool execution result
    """
    from mcp_server.server import mcp

    # Get tool by name
    tool_func = getattr(mcp, tool_name, None)

    if not tool_func:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Execute tool
    result = await tool_func(**arguments)

    return result
```

## Best Practices

### Tool Design
- **Single Responsibility**: Each tool does ONE thing well
- **Clear Naming**: Use verb_noun pattern (create_task, list_tasks)
- **Comprehensive Docs**: AI reads docstrings to understand usage
- **Structured Returns**: Always return consistent format
- **User Isolation**: Always include user_id for multi-user apps

### Error Handling
- Return structured errors, never raise to AI
- Include helpful error messages
- Log all tool executions
- Validate inputs before execution
- Use database transactions

### Performance
- Use database indexes on user_id
- Limit query results (default max 50-100)
- Close database sessions properly
- Use connection pooling
- Cache frequently-accessed data

### Security
- Validate user_id matches authenticated user
- Sanitize all inputs (prevent SQL injection)
- Never expose sensitive data
- Log security events
- Implement rate limiting

## Testing Tools
```python
import pytest
from mcp_server.server import add_task, list_tasks

@pytest.mark.asyncio
async def test_add_task():
    result = await add_task(
        user_id="test_user",
        title="Test Task"
    )

    assert result["status"] == "created"
    assert "task_id" in result

@pytest.mark.asyncio
async def test_list_tasks():
    tasks = await list_tasks(
        user_id="test_user",
        status="all"
    )

    assert isinstance(tasks, list)
```

## Output
- Standardized MCP tools
- Database-backed operations
- Error handling and validation
- OpenAI-compatible exports
- Comprehensive testing
