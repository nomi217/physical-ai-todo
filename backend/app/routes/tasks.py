"""
Task management API routes.

Provides RESTful endpoints for CRUD operations on tasks.
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app import crud
from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models import User
from app.schemas import (
    BulkOperationRequest,
    BulkPriorityRequest,
    BulkTagRequest,
    ReorderRequest,
    TaskCreate,
    TaskListResponse,
    TaskPatch,
    TaskRead,
    TaskUpdate,
)
from app.models import Notification
from datetime import datetime

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def _task_to_read(db_task) -> TaskRead:
    """Convert database Task model to TaskRead schema."""
    return TaskRead(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        completed=db_task.completed,
        priority=db_task.priority,
        tags=json.loads(db_task.tags) if db_task.tags else [],
        created_at=db_task.created_at,
        updated_at=db_task.updated_at,
        due_date=db_task.due_date,
        reminder_offset=db_task.reminder_offset,
        reminder_time=db_task.reminder_time,
    )


@router.get("", response_model=TaskListResponse)
def get_tasks(
    limit: int = Query(50, ge=1, le=100, description="Maximum tasks per page"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(
        None, pattern="^(high|medium|low)$", description="Filter by priority"
    ),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    sort: str = Query(
        "created_at",
        pattern="^(created_at|updated_at|priority|title)$",
        description="Sort field",
    ),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    List all tasks with optional filtering, search, sorting, and pagination.

    **Query Parameters:**
    - **limit**: Max tasks per page (1-100, default: 50)
    - **offset**: Number of tasks to skip (default: 0)
    - **search**: Search term for title/description
    - **completed**: Filter by completion (true/false)
    - **priority**: Filter by priority (high/medium/low)
    - **tags**: Comma-separated tags (e.g., "work,urgent")
    - **sort**: Sort by field (created_at/updated_at/priority/title)
    - **order**: Sort order (asc/desc)

    **Returns:**
    - List of tasks matching filters
    - Total count of matching tasks
    - Pagination info (limit, offset)
    """
    tasks, total = crud.list_tasks(
        session=session,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        search=search,
        completed=completed,
        priority=priority,
        tags=tags,
        sort=sort,
        order=order,
    )

    # Convert tasks to TaskRead schema
    tasks_with_parsed_tags = [_task_to_read(task) for task in tasks]

    return TaskListResponse(
        tasks=tasks_with_parsed_tags, total=total, limit=limit, offset=offset
    )


@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new task.

    **Request Body:**
    - **title**: Task title (required, 1-200 chars)
    - **description**: Task description (optional, max 2000 chars)
    - **priority**: Priority level (high/medium/low, default: medium)
    - **tags**: Array of tag strings (default: [])
    - **due_date**: Due date and time (optional, ISO 8601 format)
    - **reminder_offset**: Reminder offset (optional, one of: 1h/1d/3d/5d/1w)

    **Returns:**
    - Created task with ID, timestamps, and calculated reminder_time
    """
    db_task = crud.create_task(task_data, session, user_id=current_user.id)

    # Create notification for task creation
    notification = Notification(
        user_id=current_user.id,
        task_id=db_task.id,
        type="task_created",
        title=f"✅ Task Created",
        message=f'Created task: "{db_task.title}"',
        is_read=False,
        created_at=datetime.utcnow()
    )
    session.add(notification)
    session.commit()

    return _task_to_read(db_task)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get a single task by ID.

    **Path Parameters:**
    - **task_id**: Task ID to retrieve

    **Returns:**
    - Task details

    **Raises:**
    - 404: Task not found
    """
    db_task = crud.get_task(task_id, session)
    if not db_task or db_task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    return _task_to_read(db_task)


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Update a task (full replacement).

    **Path Parameters:**
    - **task_id**: Task ID to update

    **Request Body:**
    - All task fields (title, description, priority, tags, completed, due_date, reminder_offset)

    **Returns:**
    - Updated task with recalculated reminder_time

    **Raises:**
    - 404: Task not found
    """
    # Verify ownership
    existing_task = crud.get_task(task_id, session)
    if not existing_task or existing_task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    db_task = crud.update_task(task_id, task_data, session)
    if not db_task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    return _task_to_read(db_task)


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(
    task_id: int,
    task_data: TaskPatch,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Partially update a task.

    **Path Parameters:**
    - **task_id**: Task ID to update

    **Request Body:**
    - Only the fields you want to update (all optional)

    **Example:**
    ```json
    {"completed": true}
    ```

    **Returns:**
    - Updated task

    **Raises:**
    - 404: Task not found
    """
    # Verify ownership
    existing_task = crud.get_task(task_id, session)
    if not existing_task or existing_task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    db_task = crud.patch_task(task_id, task_data, session)
    if not db_task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    # Create notification for task update
    notification = Notification(
        user_id=current_user.id,
        task_id=db_task.id,
        type="task_updated",
        title=f"✏️ Task Updated",
        message=f'Updated: "{db_task.title}"',
        is_read=False,
        created_at=datetime.utcnow()
    )
    session.add(notification)
    session.commit()

    return _task_to_read(db_task)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a task.

    **Path Parameters:**
    - **task_id**: Task ID to delete

    **Returns:**
    - No content (204)

    **Raises:**
    - 404: Task not found
    """
    # Verify ownership
    existing_task = crud.get_task(task_id, session)
    if not existing_task or existing_task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    # Create notification BEFORE deleting (we need the task title)
    task_title = existing_task.title
    notification = Notification(
        user_id=current_user.id,
        task_id=task_id,
        type="task_deleted",
        title=f"🗑️ Task Deleted",
        message=f'Deleted: "{task_title}"',
        is_read=False,
        created_at=datetime.utcnow()
    )
    session.add(notification)
    session.commit()

    deleted = crud.delete_task(task_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    return None


@router.post("/{task_id}/toggle", response_model=TaskRead)
def toggle_task_completion(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Toggle task completion status (completed <-> not completed).

    **Path Parameters:**
    - **task_id**: Task ID to toggle

    **Returns:**
    - Updated task with toggled completion status

    **Raises:**
    - 404: Task not found
    """
    # Verify ownership
    existing_task = crud.get_task(task_id, session)
    if not existing_task or existing_task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    db_task = crud.toggle_complete(task_id, session)
    if not db_task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    # Create notification for task completion/uncomplete
    if db_task.completed:
        notification = Notification(
            user_id=current_user.id,
            task_id=db_task.id,
            type="task_completed",
            title=f"🎉 Task Completed",
            message=f'Completed: "{db_task.title}"',
            is_read=False,
            created_at=datetime.utcnow()
        )
    else:
        notification = Notification(
            user_id=current_user.id,
            task_id=db_task.id,
            type="task_reopened",
            title=f"🔄 Task Reopened",
            message=f'Reopened: "{db_task.title}"',
            is_read=False,
            created_at=datetime.utcnow()
        )
    session.add(notification)
    session.commit()

    return _task_to_read(db_task)


# ============================================================================
# Bulk Operations and Reorder Endpoints (US5: Interactive Management)
# ============================================================================


@router.post("/reorder")
def reorder_tasks(
    request: ReorderRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Reorder tasks by updating display_order for multiple tasks.

    **Request Body:**
    ```json
    {
      "items": [
        {"id": 1, "display_order": 0},
        {"id": 2, "display_order": 1},
        {"id": 3, "display_order": 2}
      ]
    }
    ```

    **Returns:**
    - Success message with count of updated tasks

    **Raises:**
    - 400: Invalid request (empty items list)
    - 403: User doesn't own one or more tasks
    """
    if not request.items:
        raise HTTPException(status_code=400, detail="Items list cannot be empty")

    # Extract task IDs
    task_ids = [item["id"] for item in request.items]

    # Verify ownership of all tasks
    for task_id in task_ids:
        task = crud.get_task(task_id, session)
        if not task or task.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail=f"Task {task_id} not found or access denied"
            )

    # Update display_order for each task
    updated_count = 0
    for item in request.items:
        task = crud.patch_task(
            item["id"], TaskPatch(display_order=item["display_order"]), session
        )
        if task:
            updated_count += 1

    return {
        "success": True,
        "updated_count": updated_count,
        "message": f"Reordered {updated_count} tasks",
    }


@router.post("/bulk/complete")
def bulk_complete_tasks(
    request: BulkOperationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Mark multiple tasks as completed.

    **Request Body:**
    ```json
    {
      "task_ids": [1, 2, 3, 4, 5]
    }
    ```

    **Returns:**
    - Success message with count of updated tasks

    **Raises:**
    - 400: Invalid request (empty task_ids)
    """
    if not request.task_ids:
        raise HTTPException(status_code=400, detail="task_ids cannot be empty")

    updated_count = 0
    for task_id in request.task_ids:
        # Verify ownership
        task = crud.get_task(task_id, session)
        if task and task.user_id == current_user.id:
            # Mark as completed
            crud.patch_task(task_id, TaskPatch(completed=True), session)
            updated_count += 1

    return {
        "success": True,
        "updated_count": updated_count,
        "message": f"Completed {updated_count} tasks",
    }


@router.post("/bulk/delete")
def bulk_delete_tasks(
    request: BulkOperationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete multiple tasks.

    **Request Body:**
    ```json
    {
      "task_ids": [1, 2, 3]
    }
    ```

    **Returns:**
    - Success message with count of deleted tasks

    **Raises:**
    - 400: Invalid request (empty task_ids)
    """
    if not request.task_ids:
        raise HTTPException(status_code=400, detail="task_ids cannot be empty")

    deleted_count = 0
    for task_id in request.task_ids:
        # Verify ownership
        task = crud.get_task(task_id, session)
        if task and task.user_id == current_user.id:
            crud.delete_task(task_id, session)
            deleted_count += 1

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Deleted {deleted_count} tasks",
    }


@router.post("/bulk/tag")
def bulk_add_tag(
    request: BulkTagRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Add a tag to multiple tasks.

    **Request Body:**
    ```json
    {
      "task_ids": [1, 2, 3],
      "tag": "urgent"
    }
    ```

    **Returns:**
    - Success message with count of updated tasks

    **Raises:**
    - 400: Invalid request (empty task_ids or tag)
    """
    if not request.task_ids:
        raise HTTPException(status_code=400, detail="task_ids cannot be empty")
    if not request.tag:
        raise HTTPException(status_code=400, detail="tag cannot be empty")

    updated_count = 0
    for task_id in request.task_ids:
        # Verify ownership
        task = crud.get_task(task_id, session)
        if task and task.user_id == current_user.id:
            # Get existing tags
            existing_tags = json.loads(task.tags) if task.tags else []
            # Add new tag if not already present
            if request.tag not in existing_tags:
                existing_tags.append(request.tag)
                crud.patch_task(task_id, TaskPatch(tags=existing_tags), session)
                updated_count += 1

    return {
        "success": True,
        "updated_count": updated_count,
        "message": f"Added tag '{request.tag}' to {updated_count} tasks",
    }


@router.post("/bulk/priority")
def bulk_set_priority(
    request: BulkPriorityRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Set priority for multiple tasks.

    **Request Body:**
    ```json
    {
      "task_ids": [1, 2, 3],
      "priority": "high"
    }
    ```

    **Returns:**
    - Success message with count of updated tasks

    **Raises:**
    - 400: Invalid request (empty task_ids)
    """
    if not request.task_ids:
        raise HTTPException(status_code=400, detail="task_ids cannot be empty")

    updated_count = 0
    for task_id in request.task_ids:
        # Verify ownership
        task = crud.get_task(task_id, session)
        if task and task.user_id == current_user.id:
            crud.patch_task(task_id, TaskPatch(priority=request.priority), session)
            updated_count += 1

    return {
        "success": True,
        "updated_count": updated_count,
        "message": f"Set priority to '{request.priority}' for {updated_count} tasks",
    }
