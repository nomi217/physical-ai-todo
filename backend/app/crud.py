"""
CRUD operations for Task management.

Provides async database operations for creating, reading, updating, and deleting tasks.
"""

import json
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select, func, or_
from sqlmodel import Session, col

from app.models import Task, ConversationMessage, Notification
from app.schemas import TaskCreate, TaskUpdate, TaskPatch
from app.utils.reminder_calculator import calculate_reminder_time


def create_task(task_data: TaskCreate, session: Session, user_id: int) -> Task:
    """
    Create a new task in the database.

    Args:
        task_data: Task creation data (title, description, priority, tags, due_date, reminder_offset)
        session: Async database session
        user_id: ID of the user creating the task

    Returns:
        Created Task object with generated ID and timestamps
    """
    # Calculate reminder_time if due_date and reminder_offset provided
    reminder_time = None
    if task_data.due_date and task_data.reminder_offset:
        reminder_time = calculate_reminder_time(task_data.due_date, task_data.reminder_offset)

    # Create new task instance
    db_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        tags=task_data.tags,  # SQLModel with Column(JSON) handles serialization automatically
        completed=False,
        due_date=task_data.due_date,
        reminder_offset=task_data.reminder_offset,
        reminder_time=reminder_time,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


def list_tasks(
    session: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    tags: Optional[str] = None,
    sort: str = "created_at",
    order: str = "desc",
) -> Tuple[List[Task], int]:
    """
    List tasks with optional filtering, sorting, and pagination.

    Args:
        session: Async database session
        limit: Maximum number of tasks to return (default: 50)
        offset: Number of tasks to skip (default: 0)
        search: Search term for title/description (optional)
        completed: Filter by completion status (optional)
        priority: Filter by priority level (optional)
        tags: Comma-separated tags to filter by (optional)
        sort: Field to sort by (created_at, updated_at, priority, title)
        order: Sort order (asc or desc)

    Returns:
        Tuple of (list of tasks, total count)
    """
    # Build base query with user_id filter
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                col(Task.title).ilike(search_pattern),
                col(Task.description).ilike(search_pattern),
            )
        )

    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority:
        query = query.where(Task.priority == priority)

    if tags:
        # Filter by tags (simple contains check)
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            query = query.where(col(Task.tags).contains(f'"{tag}"'))

    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    result = session.execute(count_query)
    total = result.scalar_one()

    # Apply sorting
    sort_column = getattr(Task, sort, Task.created_at)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    result = session.execute(query)
    tasks = result.scalars().all()

    return list(tasks), total


def get_task(task_id: int, session: Session) -> Optional[Task]:
    """
    Get a single task by ID.

    Args:
        task_id: Task ID to retrieve
        session: Async database session

    Returns:
        Task object if found, None otherwise
    """
    result = session.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


def update_task(task_id: int, task_data: TaskUpdate, session: Session) -> Optional[Task]:
    """
    Update a task with full replacement (PUT).

    Args:
        task_id: Task ID to update
        task_data: Complete task data for replacement
        session: Async database session

    Returns:
        Updated Task object if found, None otherwise
    """
    db_task = get_task(task_id, session)
    if not db_task:
        return None

    # Save old values before updating
    old_reminder_time = db_task.reminder_time
    old_due_date = db_task.due_date

    # Calculate reminder_time if due_date and reminder_offset provided
    reminder_time = None
    if task_data.due_date and task_data.reminder_offset:
        reminder_time = calculate_reminder_time(task_data.due_date, task_data.reminder_offset)

    # Update all fields
    db_task.title = task_data.title
    db_task.description = task_data.description
    db_task.priority = task_data.priority
    db_task.tags = json.dumps(task_data.tags)
    db_task.completed = task_data.completed
    db_task.due_date = task_data.due_date
    db_task.reminder_offset = task_data.reminder_offset
    db_task.reminder_time = reminder_time

    # Reset reminder/overdue tracking when reminder_time or due_date changes
    if old_reminder_time != reminder_time:
        db_task.last_reminder_sent = None
    if old_due_date != task_data.due_date:
        db_task.last_overdue_notification_sent = None

    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


def patch_task(task_id: int, task_data: TaskPatch, session: Session) -> Optional[Task]:
    """
    Partially update a task (PATCH).

    Args:
        task_id: Task ID to update
        task_data: Partial task data (only provided fields will be updated)
        session: Async database session

    Returns:
        Updated Task object if found, None otherwise
    """
    db_task = get_task(task_id, session)
    if not db_task:
        return None

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "tags" and value is not None:
            setattr(db_task, field, json.dumps(value))
        elif value is not None:
            setattr(db_task, field, value)

    # Recalculate reminder_time if due_date or reminder_offset changed
    if 'due_date' in update_data or 'reminder_offset' in update_data:
        old_reminder_time = db_task.reminder_time
        old_due_date = db_task.due_date

        # Use updated values if provided, otherwise keep existing
        due_date = update_data.get('due_date', db_task.due_date)
        reminder_offset = update_data.get('reminder_offset', db_task.reminder_offset)

        # Calculate new reminder_time
        if due_date and reminder_offset:
            db_task.reminder_time = calculate_reminder_time(due_date, reminder_offset)
        else:
            db_task.reminder_time = None

        # Reset reminder/overdue tracking when values change
        if db_task.reminder_time != old_reminder_time:
            db_task.last_reminder_sent = None
        if 'due_date' in update_data and db_task.due_date != old_due_date:
            db_task.last_overdue_notification_sent = None

    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


def delete_task(task_id: int, session: Session) -> bool:
    """
    Delete a task by ID.

    Args:
        task_id: Task ID to delete
        session: Async database session

    Returns:
        True if task was deleted, False if not found
    """
    db_task = get_task(task_id, session)
    if not db_task:
        return False

    session.delete(db_task)
    session.commit()

    return True


def toggle_complete(task_id: int, session: Session) -> Optional[Task]:
    """
    Toggle task completion status.

    Args:
        task_id: Task ID to toggle
        session: Async database session

    Returns:
        Updated Task object if found, None otherwise
    """
    db_task = get_task(task_id, session)
    if not db_task:
        return None

    db_task.completed = not db_task.completed
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


# ============================================================================
# Conversation CRUD Operations (Phase III AI Chatbot)
# ============================================================================


def create_conversation_message(
    db: Session,
    conversation_id: int,
    user_id: int,
    role: str,
    content: str,
    tool_calls: Optional[dict] = None
) -> ConversationMessage:
    """
    Create a new conversation message.

    Args:
        db: Database session
        conversation_id: Conversation ID
        user_id: User ID
        role: Message role (user, assistant, system)
        content: Message content
        tool_calls: Optional tool calls data (for assistant messages)

    Returns:
        Created ConversationMessage object
    """
    message = ConversationMessage(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        created_at=datetime.utcnow()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_conversation_history(
    db: Session,
    conversation_id: int,
    limit: int = 20
) -> List[ConversationMessage]:
    """
    Get conversation history with sliding window (last N messages).

    Args:
        db: Database session
        conversation_id: Conversation ID
        limit: Maximum number of messages to return (default: 20)

    Returns:
        List of ConversationMessage objects in chronological order
    """
    query = select(ConversationMessage).where(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(
        ConversationMessage.created_at.desc()
    ).limit(limit)

    result = db.execute(query)
    messages = result.scalars().all()

    # Reverse to get chronological order (oldest first)
    return list(reversed(messages))


def get_user_conversations(
    db: Session,
    user_id: int,
    limit: int = 50
) -> List[dict]:
    """
    Get list of user's conversations with metadata.

    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of conversations to return

    Returns:
        List of conversation metadata dictionaries
    """
    query = select(
        ConversationMessage.conversation_id,
        func.count(ConversationMessage.id).label('message_count'),
        func.max(ConversationMessage.created_at).label('last_message_at'),
        func.min(ConversationMessage.created_at).label('created_at')
    ).where(
        ConversationMessage.user_id == user_id
    ).group_by(
        ConversationMessage.conversation_id
    ).order_by(
        func.max(ConversationMessage.created_at).desc()
    ).limit(limit)

    result = db.execute(query)
    conversations = []

    for row in result:
        conversations.append({
            'conversation_id': row.conversation_id,
            'message_count': row.message_count,
            'last_message_at': row.last_message_at,
            'created_at': row.created_at
        })

    return conversations


# ============================================================================
# Notification CRUD Operations (Phase VI: Task Reminders & Notifications)
# ============================================================================


def get_notifications(
    session: Session,
    user_id: int,
    is_read: Optional[bool] = None,
    type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Notification]:
    """
    Get user's notifications with optional filtering.

    Args:
        session: Database session
        user_id: User ID
        is_read: Filter by read status (optional)
        type: Filter by notification type (optional)
        limit: Maximum notifications to return
        offset: Number to skip

    Returns:
        List of Notification objects sorted by created_at descending
    """
    query = select(Notification).where(Notification.user_id == user_id)

    if is_read is not None:
        query = query.where(Notification.is_read == is_read)

    if type:
        query = query.where(Notification.type == type)

    query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)

    result = session.execute(query)
    return list(result.scalars().all())


def get_unread_count(session: Session, user_id: int) -> int:
    """
    Get count of unread notifications for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Count of unread notifications
    """
    query = select(func.count()).select_from(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    )

    result = session.execute(query)
    return result.scalar_one()


def mark_notification_as_read(
    session: Session,
    notification_id: int,
    user_id: int
) -> Optional[Notification]:
    """
    Mark a notification as read.

    Args:
        session: Database session
        notification_id: Notification ID
        user_id: User ID (for authorization)

    Returns:
        Updated Notification object if found and authorized, None otherwise
    """
    notification = session.exec(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
    ).first()

    if not notification:
        return None

    notification.is_read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)

    return notification


def mark_all_notifications_as_read(session: Session, user_id: int) -> int:
    """
    Mark all user's notifications as read.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Count of notifications updated
    """
    notifications = session.exec(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    ).all()

    count = 0
    for notification in notifications:
        notification.is_read = True
        session.add(notification)
        count += 1

    session.commit()
    return count


def delete_notification(
    session: Session,
    notification_id: int,
    user_id: int
) -> bool:
    """
    Delete a notification.

    Args:
        session: Database session
        notification_id: Notification ID
        user_id: User ID (for authorization)

    Returns:
        True if deleted, False if not found or unauthorized
    """
    notification = session.exec(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
    ).first()

    if not notification:
        return False

    session.delete(notification)
    session.commit()
    return True


def delete_read_notifications(session: Session, user_id: int) -> int:
    """
    Delete all read notifications for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Count of notifications deleted
    """
    notifications = session.exec(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == True
        )
    ).all()

    count = 0
    for notification in notifications:
        session.delete(notification)
        count += 1

    session.commit()
    return count
