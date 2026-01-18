# Data Model - Phase II

**Feature**: Phase II - Full-Stack Web Application
**Date**: 2025-12-07
**Database**: Neon DB (PostgreSQL via SQLModel)

## Overview

This document defines the database schema for Phase II using SQLModel (Pydantic + SQLAlchemy). All models are designed for async PostgreSQL operations with Neon DB.

---

## Core Entities

### 1. Task (Primary Entity)

**Purpose**: Represents a todo task with all Phase I + Phase II fields

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import json

class Task(SQLModel, table=True):
    """Task model with Phase I + Phase II fields"""

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Phase I Fields
    title: str = Field(
        max_length=200,
        index=True,
        description="Task title (required, 1-200 chars)"
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Task description (optional, max 2000 chars)"
    )
    completed: bool = Field(
        default=False,
        index=True,
        description="Completion status"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp"
    )

    # Phase II New Fields
    priority: str = Field(
        default="medium",
        index=True,
        regex="^(high|medium|low)$",
        description="Priority level: high, medium, or low"
    )
    tags: str = Field(
        default="[]",
        description="JSON array of tags stored as string"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )

    # Helper Methods
    def get_tags(self) -> list[str]:
        """Parse tags from JSON string"""
        try:
            return json.loads(self.tags)
        except:
            return []

    def set_tags(self, tags_list: list[str]):
        """Set tags from list"""
        self.tags = json.dumps(tags_list)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "high",
                "tags": '["shopping", "urgent"]',
                "created_at": "2025-12-07T10:00:00",
                "updated_at": "2025-12-07T10:00:00"
            }
        }
```

**Validation Rules**:
- `title`: Required, 1-200 characters, no empty strings
- `description`: Optional, max 2000 characters
- `completed`: Boolean, defaults to `False`
- `priority`: Enum ("high", "medium", "low"), defaults to "medium"
- `tags`: JSON array stored as string, defaults to `"[]"`
- `created_at`: Auto-generated, immutable
- `updated_at`: Auto-updated on every modification

**Indexes**:
- Primary: `id` (auto-increment)
- Index: `title` (for search)
- Index: `completed` (for filtering)
- Index: `priority` (for filtering/sorting)

**State Transitions**:
```
created → completed (when user marks done)
completed → created (when user marks incomplete)
```

---

### 2. VoiceCommand (Optional - Logging)

**Purpose**: Log voice commands for analytics and debugging

**SQLModel Definition**:
```python
class VoiceCommand(SQLModel, table=True):
    """Voice command log"""

    id: Optional[int] = Field(default=None, primary_key=True)
    transcript: str = Field(description="Transcribed text")
    language: str = Field(
        max_length=5,
        regex="^(en|ur|ar|es|fr|de)$",
        description="Language code"
    )
    intent: str = Field(
        max_length=50,
        description="Parsed intent (e.g., 'create_task', 'complete_task')"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Transcription confidence score (0-1)"
    )
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "transcript": "Add task buy milk",
                "language": "en",
                "intent": "create_task",
                "confidence": 0.95,
                "created_at": "2025-12-07T10:00:00"
            }
        }
```

**Usage**: Optional for Phase II, useful for debugging voice recognition accuracy

---

### 3. ChatMessage (Optional - Chat History)

**Purpose**: Persist AI chat history for context

**SQLModel Definition**:
```python
class ChatMessage(SQLModel, table=True):
    """AI chat message history"""

    id: Optional[int] = Field(default=None, primary_key=True)
    role: str = Field(
        regex="^(user|assistant)$",
        description="Message role"
    )
    content: str = Field(
        max_length=10000,
        description="Message content"
    )
    language: str = Field(
        max_length=5,
        regex="^(en|ur|ar|es|fr|de)$",
        description="Message language"
    )
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "role": "user",
                "content": "What tasks do I have?",
                "language": "en",
                "created_at": "2025-12-07T10:00:00"
            }
        }
```

**Usage**: Optional for Phase II, enables chat context persistence

---

## Pydantic Schemas (API Request/Response)

### TaskCreate (POST /tasks)
```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    """Schema for creating a task"""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    priority: str = Field(default="medium", regex="^(high|medium|low)$")
    tags: list[str] = Field(default=[])

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "high",
                "tags": ["shopping", "urgent"]
            }
        }
```

### TaskUpdate (PUT /tasks/{id})
```python
class TaskUpdate(BaseModel):
    """Schema for full task update"""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=2000)
    priority: str = Field(..., regex="^(high|medium|low)$")
    tags: list[str] = Field(...)
    completed: bool = Field(...)

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

### TaskPatch (PATCH /tasks/{id})
```python
class TaskPatch(BaseModel):
    """Schema for partial task update"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[str] = Field(None, regex="^(high|medium|low)$")
    tags: Optional[list[str]] = None
    completed: Optional[bool] = None

    @validator('title')
    def title_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v
```

### TaskRead (Response)
```python
class TaskRead(BaseModel):
    """Schema for task response"""

    id: int
    title: str
    description: str
    completed: bool
    priority: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Allow ORM models
```

### TaskListResponse (GET /tasks response)
```python
class TaskListResponse(BaseModel):
    """Schema for list tasks response"""

    tasks: list[TaskRead]
    total: int
    limit: int
    offset: int

    class Config:
        schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "priority": "high",
                        "tags": ["shopping", "urgent"],
                        "created_at": "2025-12-07T10:00:00",
                        "updated_at": "2025-12-07T10:00:00"
                    }
                ],
                "total": 1,
                "limit": 50,
                "offset": 0
            }
        }
```

---

## Database Migrations

### Initial Migration (Create Tables)

**Using SQLModel's create_all**:
```python
# backend/app/database.py
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine

async def init_db():
    """Create all tables"""
    async with engine.begin() as conn:
        # Import all models first
        from app.models import Task, VoiceCommand, ChatMessage

        # Create tables
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Alternative: Alembic (for production)**:
```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Create tasks table"

# Apply migration
alembic upgrade head
```

---

## Query Examples

### Create Task
```python
from sqlmodel import select
from app.models import Task
from app.schemas import TaskCreate

async def create_task(task_data: TaskCreate, session: AsyncSession) -> Task:
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        tags=json.dumps(task_data.tags)
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

### List Tasks with Filters
```python
async def list_tasks(
    session: AsyncSession,
    search: str | None = None,
    completed: bool | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    sort: str = "created_at",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0
) -> tuple[list[Task], int]:
    # Build query
    query = select(Task)

    # Apply filters
    if search:
        query = query.where(
            (Task.title.contains(search)) | (Task.description.contains(search))
        )
    if completed is not None:
        query = query.where(Task.completed == completed)
    if priority:
        query = query.where(Task.priority == priority)
    if tags:
        # Search in JSON tags (PostgreSQL-specific)
        for tag in tags:
            query = query.where(Task.tags.contains(f'"{tag}"'))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # Apply sorting
    sort_column = getattr(Task, sort, Task.created_at)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute
    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks, total
```

### Update Task
```python
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: AsyncSession
) -> Task | None:
    task = await session.get(Task, task_id)
    if not task:
        return None

    task.title = task_data.title
    task.description = task_data.description
    task.priority = task_data.priority
    task.tags = json.dumps(task_data.tags)
    task.completed = task_data.completed
    task.updated_at = datetime.now()

    await session.commit()
    await session.refresh(task)
    return task
```

---

## Constraints & Business Rules

1. **Title Validation**:
   - Required field
   - 1-200 characters
   - Cannot be empty or whitespace only
   - Automatically trimmed

2. **Priority Validation**:
   - Must be one of: "high", "medium", "low"
   - Defaults to "medium"
   - Case-sensitive

3. **Tags Management**:
   - Stored as JSON array string
   - No duplicates (enforced in business logic)
   - Tags are case-sensitive
   - Maximum 10 tags per task (enforced in API)

4. **Completion Status**:
   - Boolean field
   - Can be toggled multiple times
   - No cascade effects (future: may trigger notifications)

5. **Timestamps**:
   - `created_at`: Set once, never modified
   - `updated_at`: Auto-updated on every save

---

## Migration from Phase I

**Phase I Data Model** (in-memory dict):
```python
{
    "id": int,
    "title": str,
    "description": str,
    "completed": bool,
    "created_at": str  # ISO 8601
}
```

**Migration Strategy**:
1. **Backward Compatible**: Phase II model includes all Phase I fields
2. **New Fields Have Defaults**: `priority="medium"`, `tags="[]"`, `updated_at=created_at`
3. **No Data Loss**: All Phase I tasks can be migrated as-is
4. **Migration Script**: (Future) `scripts/migrate_phase1_to_phase2.py`

---

## Database Diagram

```
┌─────────────────────────────────────────┐
│              Task                        │
├─────────────────────────────────────────┤
│ id: int (PK, auto-increment)            │
│ title: varchar(200) NOT NULL            │
│ description: text                        │
│ completed: boolean DEFAULT false        │
│ priority: varchar(10) DEFAULT 'medium'  │
│ tags: text DEFAULT '[]'                 │
│ created_at: timestamp                   │
│ updated_at: timestamp                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         VoiceCommand (Optional)          │
├─────────────────────────────────────────┤
│ id: int (PK)                            │
│ transcript: text                         │
│ language: varchar(5)                     │
│ intent: varchar(50)                      │
│ confidence: float                        │
│ created_at: timestamp                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         ChatMessage (Optional)           │
├─────────────────────────────────────────┤
│ id: int (PK)                            │
│ role: varchar(10)                        │
│ content: text                            │
│ language: varchar(5)                     │
│ created_at: timestamp                   │
└─────────────────────────────────────────┘
```

---

## Next Steps

1. Create API contracts in `contracts/openapi.yaml`
2. Implement CRUD operations in `backend/app/crud.py`
3. Create API routes in `backend/app/routes/tasks.py`
4. Write tests in `backend/tests/test_crud.py`

**Data Model Status**: ✅ Complete
**Ready for API Contract Design**: Yes
