# Data Model: Task Reminders and In-App Notifications

**Feature**: 006-task-reminders
**Date**: 2025-12-30
**Phase**: 1 - Data Model Design

## Overview

This document defines the database schema changes and entity relationships for the task reminders and notifications feature. All entities use SQLModel (Pydantic + SQLAlchemy) for FastAPI integration.

---

## Entity 1: Task (EXTENDED)

**Status**: Existing entity - adding new fields

### New Fields

| Field Name | Type | Constraints | Purpose |
|------------|------|-------------|---------|
| `due_date` | `datetime \| None` | Nullable, indexed | When the task is due (user-selected via calendar picker) |
| `reminder_offset` | `str \| None` | Max 10 chars, nullable | User's selected offset: "1h", "1d", "3d", "5d", "1w", or NULL for "Never" |
| `reminder_time` | `datetime \| None` | Nullable, indexed | Calculated from due_date minus offset, used by scheduler |
| `last_reminder_sent` | `datetime \| None` | Nullable | Timestamp when reminder notification was sent (prevents duplicates) |
| `last_overdue_notification_sent` | `datetime \| None` | Nullable | Timestamp when overdue notification was sent (prevents duplicates) |

### Existing Fields (No Changes)
```python
id: int
user_id: int
title: str (max 500, indexed)
description: str | None (max 5000)
completed: bool (indexed)
priority: str (enum: "low", "medium", "high")
tags: str (JSON array stored as string)
display_order: int (indexed)
is_template: bool
created_at: datetime (indexed)
updated_at: datetime
# ... subtasks, notes, attachments relationships
```

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    # ... existing fields ...

    # NEW: Due date and reminder fields
    due_date: datetime | None = Field(default=None, index=True, sa_column_kwargs={"nullable": True})
    reminder_offset: str | None = Field(default=None, max_length=10, sa_column_kwargs={"nullable": True})
    reminder_time: datetime | None = Field(default=None, index=True, sa_column_kwargs={"nullable": True})
    last_reminder_sent: datetime | None = Field(default=None, sa_column_kwargs={"nullable": True})
    last_overdue_notification_sent: datetime | None = Field(default=None, sa_column_kwargs={"nullable": True})

    # Relationships
    notifications: list["Notification"] = Relationship(back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
```

### Validation Rules

1. **due_date**: Must be in the future (if provided)
2. **reminder_offset**: Must be one of: "1h", "1d", "3d", "5d", "1w", NULL
3. **reminder_time**: Automatically calculated by backend, must be in the future if set
4. **reminder_time Calculation**: `reminder_time = due_date - OFFSET_MAPPING[reminder_offset]`
5. **Validation**: If reminder_time calculation results in past time, raise error

### State Transitions

```
State: Task with no due date
  → User sets due_date → State: Task with due date, no reminder
  → User selects offset → State: Task with due date and reminder

State: Task with due date and reminder
  → reminder_time <= now → Scheduler creates reminder notification, sets last_reminder_sent
  → due_date <= now AND not completed → Scheduler creates overdue notification, sets last_overdue_notification_sent

State: Task with overdue notification
  → User completes task → Overdue indicator cleared
  → User updates due_date to future → Overdue status cleared, recalculate reminder_time
```

---

## Entity 2: Notification (NEW)

**Status**: New table

### Purpose
Stores all in-app notifications triggered by task reminders or overdue status. Provides audit trail and enables notification history features.

### Fields

| Field Name | Type | Constraints | Purpose |
|------------|------|-------------|---------|
| `id` | `int` | Primary key, auto-increment | Unique identifier |
| `user_id` | `int` | Foreign key → user.id, indexed | Owner of the notification |
| `task_id` | `int` | Foreign key → task.id, indexed | Related task |
| `type` | `str` | Max 50 chars, required | Notification type: "reminder" or "overdue" |
| `title` | `str` | Max 200 chars, required | Notification title (e.g., task.title) |
| `message` | `str` | Max 500 chars, required | Notification message (e.g., "Due in 1 hour") |
| `is_read` | `bool` | Default False, indexed | Read status for filtering |
| `created_at` | `datetime` | Auto-generated, indexed | When notification was created |

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    task_id: int = Field(foreign_key="task.id", index=True)
    type: str = Field(max_length=50)  # "reminder" or "overdue"
    title: str = Field(max_length=200)
    message: str = Field(max_length=500)
    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.now, index=True)

    # Relationships
    user: "User" = Relationship(back_populates="notifications")
    task: "Task" = Relationship(back_populates="notifications")
```

### Indexes

**Required Indexes** (for query performance):

1. **Composite Index**: `(user_id, is_read)` - For "get unread notifications for user" query
2. **Single Index**: `task_id` - For cascade delete when task is removed
3. **Single Index**: `created_at` - For date-range queries and cleanup jobs
4. **Single Index**: `is_read` - For filtering by read status

```sql
CREATE INDEX idx_notifications_user_read ON notification (user_id, is_read);
CREATE INDEX idx_notifications_task ON notification (task_id);
CREATE INDEX idx_notifications_created ON notification (created_at);
CREATE INDEX idx_notifications_read ON notification (is_read);
```

### Cascade Behavior

**When Task is Deleted**: All related notifications are deleted (`cascade="all, delete-orphan"`)
**When User is Deleted**: All user's notifications are deleted (via user relationship cascade)

---

## Entity 3: User (EXTENDED)

**Status**: Existing entity - adding relationship

### New Relationship

```python
class User(SQLModel, table=True):
    # ... existing fields ...

    # NEW: Relationship to notifications
    notifications: list["Notification"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
```

**No new fields added to User table** - only relationship for SQLModel ORM queries.

---

## Database Migration Script

### Alembic Migration

**File**: `backend/alembic/versions/2025_12_30_xxxx_add_reminders_notifications.py`

```python
"""Add reminders and notifications

Revision ID: xxxxxxxxxxxx
Revises: <previous_revision_id>
Create Date: 2025-12-30

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'xxxxxxxxxxxx'
down_revision = '<previous_revision_id>'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Extend tasks table
    op.add_column('task', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('reminder_offset', sa.String(length=10), nullable=True))
    op.add_column('task', sa.Column('reminder_time', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('last_reminder_sent', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('last_overdue_notification_sent', sa.DateTime(), nullable=True))

    # Create indexes on tasks table
    op.create_index('idx_task_due_date', 'task', ['due_date'])
    op.create_index('idx_task_reminder_time', 'task', ['reminder_time'])

    # Create notifications table
    op.create_table(
        'notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.String(length=500), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes on notifications table
    op.create_index('idx_notifications_user_read', 'notification', ['user_id', 'is_read'])
    op.create_index('idx_notifications_task', 'notification', ['task_id'])
    op.create_index('idx_notifications_created', 'notification', ['created_at'])
    op.create_index('idx_notifications_read', 'notification', ['is_read'])

def downgrade() -> None:
    # Drop notifications table and indexes
    op.drop_index('idx_notifications_read', table_name='notification')
    op.drop_index('idx_notifications_created', table_name='notification')
    op.drop_index('idx_notifications_task', table_name='notification')
    op.drop_index('idx_notifications_user_read', table_name='notification')
    op.drop_table('notification')

    # Drop task indexes
    op.drop_index('idx_task_reminder_time', table_name='task')
    op.drop_index('idx_task_due_date', table_name='task')

    # Remove task columns
    op.drop_column('task', 'last_overdue_notification_sent')
    op.drop_column('task', 'last_reminder_sent')
    op.drop_column('task', 'reminder_time')
    op.drop_column('task', 'reminder_offset')
    op.drop_column('task', 'due_date')
```

---

## Data Integrity Rules

### Foreign Key Constraints

1. **notification.user_id** → user.id (ON DELETE CASCADE)
2. **notification.task_id** → task.id (ON DELETE CASCADE)

### Check Constraints (Application-Level)

```python
# In Pydantic schemas (schemas.py)
from pydantic import field_validator, model_validator
from datetime import datetime

class TaskCreate(BaseModel):
    # ... existing fields ...
    due_date: datetime | None = None
    reminder_offset: str | None = None

    @field_validator('due_date')
    @classmethod
    def due_date_must_be_future(cls, v):
        if v and v <= datetime.now():
            raise ValueError('Due date must be in the future')
        return v

    @field_validator('reminder_offset')
    @classmethod
    def validate_reminder_offset(cls, v):
        if v and v not in ["1h", "1d", "3d", "5d", "1w", None]:
            raise ValueError('Invalid reminder offset')
        return v

    @model_validator(mode='after')
    def validate_reminder_time_feasible(self):
        if self.due_date and self.reminder_offset and self.reminder_offset != "never":
            calculated_time = calculate_reminder_time(self.due_date, self.reminder_offset)
            if calculated_time <= datetime.now():
                raise ValueError('Reminder time would be in the past with this offset')
        return self
```

---

## Query Patterns

### Common Queries (with indexes)

#### 1. Get Unread Notifications for User
```sql
SELECT * FROM notification
WHERE user_id = ? AND is_read = false
ORDER BY created_at DESC;
-- Uses idx_notifications_user_read (composite index)
```

#### 2. Get Tasks Due for Reminder (Scheduler)
```sql
SELECT * FROM task
WHERE reminder_time <= NOW()
  AND last_reminder_sent IS NULL
  AND completed = false;
-- Uses idx_task_reminder_time
```

#### 3. Get Overdue Tasks (Scheduler)
```sql
SELECT * FROM task
WHERE due_date <= NOW()
  AND completed = false
  AND last_overdue_notification_sent IS NULL;
-- Uses idx_task_due_date
```

#### 4. Get Upcoming Reminders (Dashboard Widget)
```sql
SELECT * FROM task
WHERE user_id = ?
  AND reminder_time > NOW()
  AND reminder_time <= NOW() + INTERVAL '24 hours'
ORDER BY reminder_time ASC
LIMIT 5;
-- Uses idx_task_reminder_time + user_id index
```

---

## Data Lifecycle

### Notification Cleanup Strategy

**Problem**: Notification table will grow indefinitely
**Solution**: Periodic cleanup job (runs daily)

```python
# Run daily at 2 AM
@scheduler.scheduled_job('cron', hour=2, minute=0)
async def cleanup_old_notifications():
    # Delete read notifications older than 30 days
    threshold = datetime.now() - timedelta(days=30)
    await db.execute(
        delete(Notification).where(
            and_(
                Notification.is_read == True,
                Notification.created_at < threshold
            )
        )
    )
```

---

## Relationships Diagram

```
User (1) ───────< (N) Task
  │                    │
  │                    │ due_date: datetime?
  │                    │ reminder_offset: str?
  │                    │ reminder_time: datetime? (calculated)
  │                    │
  └──< (N) Notification (N) >──┘
         │
         ├─ user_id (FK)
         ├─ task_id (FK)
         ├─ type: "reminder" | "overdue"
         ├─ is_read: bool
         └─ created_at: datetime
```

---

## TypeScript Types (Frontend)

```typescript
// frontend/lib/types.ts

export interface Task {
  // ... existing fields ...

  // NEW: Reminder fields
  due_date?: string;  // ISO 8601 datetime string
  reminder_offset?: "1h" | "1d" | "3d" | "5d" | "1w" | null;
  reminder_time?: string;  // ISO 8601 datetime string (calculated)
}

export interface Notification {
  id: number;
  user_id: number;
  task_id: number;
  type: "reminder" | "overdue";
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;  // ISO 8601 datetime string
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: "low" | "medium" | "high";
  tags?: string[];
  due_date?: Date;  // Frontend uses Date object, converted to ISO string for API
  reminder_offset?: "1h" | "1d" | "3d" | "5d" | "1w" | "never";
}
```

---

## Summary

- **Task table extended**: 5 new nullable datetime/string fields, 2 new indexes
- **Notification table created**: 8 fields, 4 indexes, 2 foreign keys with CASCADE delete
- **User table**: No schema changes, only SQLModel relationship added
- **Migration script**: Alembic script for upgrade/downgrade paths
- **All queries indexed**: Efficient access patterns for scheduler and user queries
- **Cleanup strategy**: Daily job to remove old read notifications (30 days retention)

**Ready to proceed to Phase 1: API Contracts**
