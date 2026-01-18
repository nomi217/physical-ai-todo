"""SQLModel database models for Physical AI Todo"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import JSON, BigInteger
from sqlmodel import Column, Field, Relationship, SQLModel

# ============================
# Enums
# ============================


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"
    RESTORED = "restored"


# ============================
# User
# ============================


class User(SQLModel, table=True):
    """User model for authentication"""

    id: Optional[int] = Field(default=None, primary_key=True)

    # ❗ FIXED: unique handled via sa_column_kwargs (no crash)
    email: str = Field(
        index=True,
        max_length=255,
        sa_column_kwargs={"unique": True},
    )

    hashed_password: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=200)

    is_active: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(default=None, max_length=255)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[Task.user_id]"},
    )

    notifications: List["Notification"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "foreign_keys": "[Notification.user_id]",
            "cascade": "all, delete-orphan",
        },
    )


# ============================
# Task
# ============================


class Task(SQLModel, table=True):
    """Main task model"""

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id", index=True)

    title: str = Field(index=True, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)

    completed: bool = Field(default=False, index=True)
    priority: Priority = Field(default=Priority.MEDIUM, index=True)

    # JSON-safe storage
    tags: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON),
    )

    # Phase V - Reminders and Notifications
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_offset: Optional[str] = Field(default=None, max_length=10)  # "1h", "1d", "3d", "5d", "1w", or None
    reminder_time: Optional[datetime] = Field(default=None, index=True)
    last_reminder_sent: Optional[datetime] = Field(default=None)
    last_overdue_notification_sent: Optional[datetime] = Field(default=None)

    is_recurring: bool = Field(default=False, index=True)
    recurrence_pattern: Optional[str] = Field(default=None, max_length=50)
    recurrence_end_date: Optional[datetime] = Field(default=None)

    display_order: int = Field(default=0, index=True)
    is_template: bool = Field(default=False, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="tasks")

    subtasks: List["Subtask"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"foreign_keys": "[Subtask.task_id]"},
    )

    notes: List["Note"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"foreign_keys": "[Note.task_id]"},
    )

    attachments: List["Attachment"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"foreign_keys": "[Attachment.task_id]"},
    )

    activity_logs: List["ActivityLog"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"foreign_keys": "[ActivityLog.task_id]"},
    )

    notifications: List["Notification"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={
            "foreign_keys": "[Notification.task_id]",
            "cascade": "all, delete-orphan",
        },
    )


# ============================
# Subtask
# ============================


class Subtask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    task_id: int = Field(foreign_key="task.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    title: str = Field(max_length=500)
    completed: bool = Field(default=False)
    display_order: int = Field(default=0, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    task: Optional[Task] = Relationship(back_populates="subtasks")


# ============================
# Note
# ============================


class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    task_id: int = Field(foreign_key="task.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    content: str = Field(max_length=5000)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    task: Optional[Task] = Relationship(back_populates="notes")


# ============================
# Attachment
# ============================


class Attachment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    task_id: int = Field(foreign_key="task.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    filename: str = Field(max_length=255)
    file_url: str = Field(max_length=1000)
    file_size: int = Field(default=0)
    mime_type: str = Field(max_length=100)

    ocr_text: Optional[str] = Field(default=None, max_length=10000)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    task: Optional[Task] = Relationship(back_populates="attachments")


# ============================
# Template
# ============================


class Template(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(index=True, max_length=200)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Priority = Field(default=Priority.MEDIUM)

    tags: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON),
    )

    subtasks: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(JSON),
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================
# Activity Log
# ============================


class ActivityLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    task_id: int = Field(foreign_key="task.id", index=True)
    action_type: ActionType = Field(index=True)

    field_changed: Optional[str] = Field(default=None, max_length=100)
    old_value: Optional[str] = Field(default=None, max_length=1000)
    new_value: Optional[str] = Field(default=None, max_length=1000)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    task: Optional[Task] = Relationship(back_populates="activity_logs")


# ============================
# Notification
# ============================


class Notification(SQLModel, table=True):
    """In-app notification model for task reminders and overdue alerts"""

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id", index=True)
    task_id: int = Field(foreign_key="task.id", index=True)

    type: str = Field(max_length=50)  # "reminder" or "overdue"
    title: str = Field(max_length=200)
    message: str = Field(max_length=500)

    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    user: Optional[User] = Relationship(back_populates="notifications")
    task: Optional[Task] = Relationship(back_populates="notifications")


# ============================
# Voice Commands
# ============================


class VoiceCommand(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    transcript: str = Field(max_length=2000)
    language: str = Field(max_length=10, index=True)
    intent: Optional[str] = Field(default=None, max_length=100)
    confidence: Optional[float] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


# ============================
# Chat Messages
# ============================


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    role: str = Field(max_length=20)
    content: str = Field(max_length=10000)
    language: str = Field(max_length=10, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


# ============================
# Conversation Messages (Phase III)
# ============================


class ConversationMessage(SQLModel, table=True):
    __tablename__ = "conversation_messages"

    id: Optional[int] = Field(default=None, primary_key=True)

    conversation_id: int = Field(sa_column=Column(BigInteger, index=True))

    user_id: int = Field(foreign_key="user.id", index=True)
    role: str = Field(max_length=20)
    content: str

    tool_calls: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
