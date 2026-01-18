"""In-memory storage and CRUD operations for tasks.

This module provides all CRUD operations (Create, Read, Update, Delete)
for tasks using an in-memory list data structure.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from . import models

# In-memory storage
_tasks: List[Dict[str, Any]] = []
_next_id: int = 1


def add_task(title: str, description: str = "") -> Dict[str, Any]:
    """
    Create a new task.

    Args:
        title: Task title (required, 1-200 chars)
        description: Task description (optional, max 2000 chars)

    Returns:
        Created task dictionary

    Raises:
        ValueError: If validation fails
    """
    global _next_id

    # Validate input
    errors = models.validate_task_data(title, description)
    if errors:
        raise ValueError("; ".join(errors))

    # Create task
    task = {
        "id": _next_id,
        "title": title.strip(),
        "description": description.strip() if description else "",
        "completed": False,
        "created_at": datetime.now().isoformat()
    }

    # Store task
    _tasks.append(task)
    _next_id += 1

    return task


def list_tasks() -> List[Dict[str, Any]]:
    """
    Get all tasks.

    Returns:
        List of task dictionaries (may be empty)
    """
    return _tasks.copy()  # Return copy to prevent external modification


def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Find task by ID.

    Args:
        task_id: Task ID to find

    Returns:
        Task dictionary if found, None otherwise
    """
    for task in _tasks:
        if task["id"] == task_id:
            return task.copy()  # Return copy
    return None


def update_task(task_id: int, title: Optional[str] = None,
                description: Optional[str] = None) -> Dict[str, Any]:
    """
    Update task fields.

    Args:
        task_id: Task ID to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Updated task dictionary

    Raises:
        ValueError: If task not found or validation fails
    """
    # Find task
    task = None
    for t in _tasks:
        if t["id"] == task_id:
            task = t
            break

    if task is None:
        raise ValueError(f"Task with ID {task_id} not found")

    # Validate new values
    if title is not None:
        error = models.validate_title(title)
        if error:
            raise ValueError(error)
        task["title"] = title.strip()

    if description is not None:
        error = models.validate_description(description)
        if error:
            raise ValueError(error)
        task["description"] = description.strip() if description else ""

    return task.copy()


def delete_task(task_id: int) -> Dict[str, Any]:
    """
    Delete task by ID.

    Args:
        task_id: Task ID to delete

    Returns:
        Deleted task dictionary

    Raises:
        ValueError: If task not found
    """
    global _tasks

    for i, task in enumerate(_tasks):
        if task["id"] == task_id:
            deleted_task = _tasks.pop(i)
            return deleted_task

    raise ValueError(f"Task with ID {task_id} not found")


def mark_complete(task_id: int, completed: bool = True) -> Dict[str, Any]:
    """
    Mark task as complete or incomplete.

    Args:
        task_id: Task ID to update
        completed: True to mark complete, False for incomplete

    Returns:
        Updated task dictionary

    Raises:
        ValueError: If task not found
    """
    for task in _tasks:
        if task["id"] == task_id:
            task["completed"] = completed
            return task.copy()

    raise ValueError(f"Task with ID {task_id} not found")


def reset_storage():
    """Reset storage to empty state. For testing only."""
    global _tasks, _next_id
    _tasks = []
    _next_id = 1
