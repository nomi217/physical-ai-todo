"""
MCP Tool Functions for Phase III AI Chatbot

Implements the actual tool functions that the AI agent can call.
Each tool wraps existing CRUD operations with proper validation
and error handling.

These tools are stateless and operate directly on the database
using the existing CRUD functions from app.crud.
"""

import json
from typing import Dict, Any, List
from sqlmodel import Session
from datetime import datetime

from app.crud import (
    create_task,
    list_tasks,
    get_task,
    patch_task,
    delete_task as crud_delete_task
)
from app.schemas import TaskCreate, TaskPatch
from app.models import Notification
from app.mcp.schemas import (
    AddTaskSchema,
    ListTasksSchema,
    CompleteTaskSchema,
    DeleteTaskSchema,
    UpdateTaskSchema
)


def add_task(params: AddTaskSchema, session: Session) -> Dict[str, Any]:
    """
    MCP Tool: Add a new task to the user's todo list.

    Args:
        params: AddTaskSchema with user_id, title, description, priority
        session: Database session

    Returns:
        Dict with success status and created task details
    """
    try:
        # Create task using existing CRUD function
        task_data = TaskCreate(
            title=params.title,
            description=params.description,
            priority=params.priority,
            tags=[]  # Empty tags for now
        )

        task = create_task(task_data, session, params.user_id)

        # Create notification for task creation (instant notification)
        print(f"DEBUG add_task: Creating notification for task '{task.title}' (ID {task.id})")
        notification = Notification(
            user_id=params.user_id,
            task_id=task.id,
            type="task_created",
            title=f"✅ Task Created",
            message=f'Created task: "{task.title}"',
            is_read=False,
            created_at=datetime.utcnow()
        )
        session.add(notification)
        session.commit()
        print(f"DEBUG add_task: Notification created and committed!")

        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "message": f"Task '{task.title}' created successfully with ID {task.id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create task: {str(e)}"
        }


def list_tasks_tool(params: ListTasksSchema, session: Session) -> Dict[str, Any]:
    """
    MCP Tool: List user's tasks with optional filtering.

    Args:
        params: ListTasksSchema with user_id, status, priority, limit
        session: Database session

    Returns:
        Dict with success status and list of tasks
    """
    try:
        # DEBUG: Log the user_id being used
        print(f"DEBUG list_tasks_tool called with user_id: {params.user_id}")

        # Determine completed filter based on status
        completed_filter = None
        if params.status == "pending":
            completed_filter = False
        elif params.status == "completed":
            completed_filter = True

        # Get tasks using existing CRUD function
        tasks, total = list_tasks(
            session=session,
            user_id=params.user_id,
            limit=params.limit,
            completed=completed_filter,
            priority=params.priority
        )

        # DEBUG: Log how many tasks were returned
        print(f"DEBUG list_tasks returned {len(tasks)} tasks for user_id {params.user_id}")

        # Format tasks for response
        task_list = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
            task_list.append(task_dict)

        return {
            "success": True,
            "tasks": task_list,
            "total": total,
            "count": len(task_list),
            "message": f"Found {len(task_list)} {params.status} task(s)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tasks": [],
            "message": f"Failed to list tasks: {str(e)}"
        }


def complete_task_tool(params: CompleteTaskSchema, session: Session) -> Dict[str, Any]:
    """
    MCP Tool: Mark a task as complete.
    Accepts either task_id OR task_title for flexible completion.

    Args:
        params: CompleteTaskSchema with user_id and either task_id or task_title
        session: Database session

    Returns:
        Dict with success status and updated task details
    """
    try:
        task = None
        task_id_to_complete = None

        # If task_title is provided, find the task by title
        if params.task_title:
            tasks, _ = list_tasks(
                session=session,
                user_id=params.user_id,
                limit=100,
                search=params.task_title,
                completed=False  # Only search pending tasks
            )

            matching_tasks = [t for t in tasks if t.title.lower() == params.task_title.lower()]
            if not matching_tasks:
                matching_tasks = [t for t in tasks if params.task_title.lower() in t.title.lower()]

            if not matching_tasks:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"No pending task found with title matching '{params.task_title}'"
                }

            if len(matching_tasks) > 1:
                task_list = "\n".join([f"- ID {t.id}: {t.title}" for t in matching_tasks])
                return {
                    "success": False,
                    "error": "Multiple matches",
                    "message": f"Found multiple tasks matching '{params.task_title}':\n{task_list}\n\nPlease use the task ID."
                }

            task = matching_tasks[0]
            task_id_to_complete = task.id

        elif params.task_id:
            task = get_task(params.task_id, session)
            task_id_to_complete = params.task_id
        else:
            return {
                "success": False,
                "error": "Missing parameter",
                "message": "Please provide either task_id or task_title"
            }

        if not task:
            return {
                "success": False,
                "error": "Task not found",
                "message": f"Task with ID {task_id_to_complete} not found"
            }

        if task.user_id != params.user_id:
            return {
                "success": False,
                "error": "Permission denied",
                "message": "You don't have permission to complete this task"
            }

        # Mark as complete
        task_patch = TaskPatch(completed=True)
        updated_task = patch_task(task_id_to_complete, task_patch, session)

        # Create notification for task completion
        notification = Notification(
            user_id=params.user_id,
            task_id=updated_task.id,
            type="task_completed",
            title=f"🎉 Task Completed",
            message=f'Completed: "{updated_task.title}"',
            is_read=False,
            created_at=datetime.utcnow()
        )
        session.add(notification)
        session.commit()

        return {
            "success": True,
            "task_id": updated_task.id,
            "title": updated_task.title,
            "completed": updated_task.completed,
            "message": f"✅ Task '{updated_task.title}' marked as complete!"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to complete task: {str(e)}"
        }


def delete_task_tool(params: DeleteTaskSchema, session: Session) -> Dict[str, Any]:
    """
    MCP Tool: Delete a task from the user's todo list.
    Accepts either task_id OR task_title for flexible deletion.

    Args:
        params: DeleteTaskSchema with user_id and either task_id or task_title
        session: Database session

    Returns:
        Dict with success status
    """
    try:
        print(f"DELETE TOOL DEBUG: Called with user_id={params.user_id}, task_id={params.task_id}, task_title={params.task_title}")

        task = None
        task_id_to_delete = None

        # If task_title is provided, find the task by title
        if params.task_title:
            print(f"DELETE TOOL DEBUG: Searching for task by title: '{params.task_title}'")
            # Get user's tasks and search by title
            tasks, _ = list_tasks(
                session=session,
                user_id=params.user_id,
                limit=100,
                search=params.task_title
            )

            # Find exact match (case-insensitive)
            matching_tasks = [t for t in tasks if t.title.lower() == params.task_title.lower()]

            if not matching_tasks:
                # Try partial match
                matching_tasks = [t for t in tasks if params.task_title.lower() in t.title.lower()]

            if not matching_tasks:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"No task found with title matching '{params.task_title}'"
                }

            if len(matching_tasks) > 1:
                task_list = "\n".join([f"- ID {t.id}: {t.title}" for t in matching_tasks])
                return {
                    "success": False,
                    "error": "Multiple matches",
                    "message": f"Found multiple tasks matching '{params.task_title}':\n{task_list}\n\nPlease use the task ID to delete."
                }

            task = matching_tasks[0]
            task_id_to_delete = task.id
            print(f"DELETE TOOL DEBUG: Found task by title: ID={task.id}, title={task.title}, owner_user_id={task.user_id}")

        # If task_id is provided, use it directly
        elif params.task_id:
            print(f"DELETE TOOL DEBUG: Searching for task by ID: {params.task_id}")
            task = get_task(params.task_id, session)
            task_id_to_delete = params.task_id
            if task:
                print(f"DELETE TOOL DEBUG: Found task by ID: ID={task.id}, title={task.title}, owner_user_id={task.user_id}")

        else:
            return {
                "success": False,
                "error": "Missing parameter",
                "message": "Please provide either task_id or task_title"
            }

        # Verify task exists
        if not task:
            print(f"DELETE TOOL DEBUG: Task not found!")
            return {
                "success": False,
                "error": "Task not found",
                "message": f"Task with ID {task_id_to_delete} not found"
            }

        # Verify ownership
        print(f"DELETE TOOL DEBUG: Checking ownership - task.user_id={task.user_id} vs params.user_id={params.user_id}")
        if task.user_id != params.user_id:
            print(f"DELETE TOOL DEBUG: PERMISSION DENIED! Task belongs to user {task.user_id}, but request is from user {params.user_id}")
            return {
                "success": False,
                "error": "Permission denied",
                "message": "You don't have permission to delete this task"
            }

        # Store title before deletion
        task_title = task.title

        # Delete task first
        deleted = crud_delete_task(task_id_to_delete, session)

        # Create notification AFTER deletion
        if deleted:
            print(f"DEBUG delete_task_tool: Creating notification for deleted task '{task_title}' (ID {task_id_to_delete})")
            notification = Notification(
                user_id=params.user_id,
                task_id=task_id_to_delete,
                type="task_deleted",
                title=f"🗑️ Task Deleted",
                message=f'Deleted: "{task_title}"',
                is_read=False,
                created_at=datetime.utcnow()
            )
            session.add(notification)
            session.commit()
            print(f"DEBUG delete_task_tool: Notification created and committed!")

        if deleted:
            return {
                "success": True,
                "task_id": task_id_to_delete,
                "message": f"✅ Task '{task_title}' deleted successfully!"
            }
        else:
            return {
                "success": False,
                "error": "Deletion failed",
                "message": "Failed to delete task"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to delete task: {str(e)}"
        }


def update_task_tool(params: UpdateTaskSchema, session: Session) -> Dict[str, Any]:
    """
    MCP Tool: Update task details (title, description, priority).
    Accepts either task_id OR task_title to identify the task.

    Args:
        params: UpdateTaskSchema with user_id, task identifier, and optional update fields
        session: Database session

    Returns:
        Dict with success status and updated task details
    """
    try:
        task = None
        task_id_to_update = None

        # If task_title is provided, find the task by title
        if params.task_title:
            tasks, _ = list_tasks(
                session=session,
                user_id=params.user_id,
                limit=100,
                search=params.task_title
            )

            matching_tasks = [t for t in tasks if t.title.lower() == params.task_title.lower()]
            if not matching_tasks:
                matching_tasks = [t for t in tasks if params.task_title.lower() in t.title.lower()]

            if not matching_tasks:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"No task found with title matching '{params.task_title}'"
                }

            if len(matching_tasks) > 1:
                task_list = "\n".join([f"- ID {t.id}: {t.title}" for t in matching_tasks])
                return {
                    "success": False,
                    "error": "Multiple matches",
                    "message": f"Found multiple tasks matching '{params.task_title}':\n{task_list}\n\nPlease use the task ID."
                }

            task = matching_tasks[0]
            task_id_to_update = task.id

        elif params.task_id:
            task = get_task(params.task_id, session)
            task_id_to_update = params.task_id
        else:
            return {
                "success": False,
                "error": "Missing parameter",
                "message": "Please provide either task_id or task_title to identify the task"
            }

        if not task:
            return {
                "success": False,
                "error": "Task not found",
                "message": f"Task with ID {task_id_to_update} not found"
            }

        if task.user_id != params.user_id:
            return {
                "success": False,
                "error": "Permission denied",
                "message": "You don't have permission to update this task"
            }

        # Build patch data from provided fields
        update_data = {}
        if params.title is not None:
            update_data["title"] = params.title
        if params.description is not None:
            update_data["description"] = params.description
        if params.priority is not None:
            update_data["priority"] = params.priority

        if not update_data:
            return {
                "success": False,
                "error": "No updates provided",
                "message": "No fields to update"
            }

        # Update task
        task_patch = TaskPatch(**update_data)
        updated_task = patch_task(task_id_to_update, task_patch, session)

        # Create notification for task update
        notification = Notification(
            user_id=params.user_id,
            task_id=updated_task.id,
            type="task_updated",
            title=f"✏️ Task Updated",
            message=f'Updated: "{updated_task.title}"',
            is_read=False,
            created_at=datetime.utcnow()
        )
        session.add(notification)
        session.commit()

        return {
            "success": True,
            "task_id": updated_task.id,
            "title": updated_task.title,
            "description": updated_task.description,
            "priority": updated_task.priority,
            "message": f"Task '{updated_task.title}' updated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update task: {str(e)}"
        }


# Tool registry for OpenAI function calling
TOOLS = {
    "add_task": {
        "function": add_task,
        "schema": AddTaskSchema,
        "description": "Add a new task to the user's todo list",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "ID of the user (auto-injected)"},
                "title": {"type": "string", "description": "Task title"},
                "description": {"type": "string", "description": "Task description"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Priority level"}
            },
            "required": ["title"]
        }
    },
    "list_tasks": {
        "function": list_tasks_tool,
        "schema": ListTasksSchema,
        "description": "List user's tasks with optional filtering by status and priority",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "ID of the user (auto-injected)"},
                "status": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter by status"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Filter by priority"},
                "limit": {"type": "integer", "description": "Maximum number of tasks"}
            },
            "required": []
        }
    },
    "complete_task": {
        "function": complete_task_tool,
        "schema": CompleteTaskSchema,
        "description": "REQUIRED TOOL: Mark a task as complete in the database. You MUST call this tool when user says 'complete [task]' or 'mark [task] as done'. Accepts either task_id (integer) OR task_title (string). NEVER say a task is completed without calling this tool - only the tool updates the database!",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "ID of the user (auto-injected)"},
                "task_id": {"type": "integer", "description": "ID of the task to complete (optional if task_title provided)"},
                "task_title": {"type": "string", "description": "Title/name of the task to complete (PREFERRED - use this when user provides task name)"}
            },
            "required": []
        }
    },
    "delete_task": {
        "function": delete_task_tool,
        "schema": DeleteTaskSchema,
        "description": "Delete a task from the user's todo list. Accepts either task_id (integer) OR task_title (string) to identify the task.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "ID of the user (auto-injected)"},
                "task_id": {"type": "integer", "description": "ID of the task to delete (optional if task_title provided)"},
                "task_title": {"type": "string", "description": "Title/name of the task to delete (optional if task_id provided)"}
            },
            "required": []
        }
    },
    "update_task": {
        "function": update_task_tool,
        "schema": UpdateTaskSchema,
        "description": "Update task details (title, description, priority). Accepts either task_id OR task_title to identify the task.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "ID of the user (auto-injected)"},
                "task_id": {"type": "integer", "description": "ID of the task to update (optional if task_title provided)"},
                "task_title": {"type": "string", "description": "Current title/name of the task to update (optional if task_id provided)"},
                "title": {"type": "string", "description": "New task title (optional)"},
                "description": {"type": "string", "description": "New task description (optional)"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority (optional)"}
            },
            "required": []
        }
    }
}
