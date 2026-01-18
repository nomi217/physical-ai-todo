# SQLModel Schema Generator

Generate production-ready SQLModel table definitions with relationships, indexes, constraints, and validation rules.

## Purpose

Eliminate boilerplate when defining database models. Auto-generate SQLModel classes from specifications with:
- Field definitions and types
- Foreign key relationships
- Indexes and constraints
- Validation rules
- Default values
- Timestamps (created_at, updated_at)

## Time Savings

**20 minutes per model** (7 models = 2.5 hours saved)

## Input Parameters

```bash
/skill sqlmodel-schema --entity=<EntityName> --fields=<field1:type,field2:type,...> [--relations=<entity1,entity2>] [--indexes=<field1,field2>]
```

### Required Parameters

- `--entity`: Entity name in PascalCase (e.g., `Note`, `Subtask`, `Attachment`)
- `--fields`: Comma-separated list of fields with types (e.g., `title:str,completed:bool,created_at:datetime`)

### Optional Parameters

- `--relations`: Related entities (generates foreign keys)
- `--indexes`: Fields to index for performance
- `--unique`: Fields that must be unique
- `--timestamps`: Add created_at/updated_at (default: `true`)
- `--soft-delete`: Add deleted_at field (default: `false`)

## Field Types

Supported types:
- `str` - String (VARCHAR)
- `int` - Integer
- `float` - Float
- `bool` - Boolean
- `datetime` - DateTime
- `date` - Date
- `time` - Time
- `text` - Text (unlimited length)
- `json` - JSON field

## Output/Deliverables

### 1. Model Definition

**Location**: `backend/app/models.py` (added to existing file)

**Contents**:
- SQLModel class with table=True
- Field definitions with types and constraints
- Foreign key relationships
- Indexes
- Validation methods

### 2. Type Hints

All fields are properly typed for mypy compliance.

## Usage Examples

### Example 1: Subtask Model

```bash
/skill sqlmodel-schema --entity=Subtask --fields=task_id:int,title:str,completed:bool,display_order:int --relations=Task --indexes=task_id,display_order
```

**Generates**:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class Subtask(SQLModel, table=True):
    """Subtask model - represents a single step in a task."""

    __tablename__ = "subtasks"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys
    task_id: int = Field(foreign_key="tasks.id", index=True, ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id", index=True, ondelete="CASCADE")

    # Fields
    title: str = Field(max_length=200, nullable=False)
    completed: bool = Field(default=False)
    display_order: int = Field(default=0, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: "Task" = Relationship(back_populates="subtasks")
    user: "User" = Relationship(back_populates="subtasks")

    # Indexes
    __table_args__ = (
        Index('idx_subtask_task_order', 'task_id', 'display_order'),
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "title": "Complete implementation",
                "completed": False,
                "display_order": 0
            }
        }

    def __repr__(self):
        return f"<Subtask {self.id}: {self.title}>"
```

### Example 2: Note Model

```bash
/skill sqlmodel-schema --entity=Note --fields=task_id:int,content:text,created_at:datetime --relations=Task
```

**Generates**:

```python
class Note(SQLModel, table=True):
    """Note model - text notes attached to tasks."""

    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True, ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id", index=True, ondelete="CASCADE")

    content: str = Field(sa_column=Column(Text))  # Unlimited text

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: "Task" = Relationship(back_populates="notes")
    user: "User" = Relationship(back_populates="notes")

    def __repr__(self):
        return f"<Note {self.id} for Task {self.task_id}>"
```

### Example 3: Attachment Model

```bash
/skill sqlmodel-schema --entity=Attachment --fields=task_id:int,filename:str,file_path:str,file_size:int,mime_type:str,ocr_text:text --relations=Task --indexes=task_id,mime_type
```

**Generates**:

```python
class Attachment(SQLModel, table=True):
    """Attachment model - files attached to tasks."""

    __tablename__ = "attachments"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True, ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id", index=True, ondelete="CASCADE")

    filename: str = Field(max_length=255, nullable=False)
    file_path: str = Field(max_length=500, nullable=False)
    file_size: int = Field(ge=0)  # Must be >= 0
    mime_type: str = Field(max_length=100, index=True)
    ocr_text: Optional[str] = Field(default=None, sa_column=Column(Text))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: "Task" = Relationship(back_populates="attachments")
    user: "User" = Relationship(back_populates="attachments")

    # Indexes
    __table_args__ = (
        Index('idx_attachment_task_mime', 'task_id', 'mime_type'),
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "filename": "document.pdf",
                "file_path": "/uploads/abc123.pdf",
                "file_size": 1024000,
                "mime_type": "application/pdf"
            }
        }

    def __repr__(self):
        return f"<Attachment {self.id}: {self.filename}>"
```

## Code Templates

### Base Model Template

```python
from sqlmodel import SQLModel, Field, Relationship, Column, Index
from sqlalchemy import Text
from typing import Optional
from datetime import datetime


class {{EntityName}}(SQLModel, table=True):
    """{{EntityName}} model - {{description}}."""

    __tablename__ = "{{table_name}}"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    {{#if hasForeignKeys}}
    # Foreign Keys
    {{#each foreignKeys}}
    {{this.field}}: int = Field(
        foreign_key="{{this.table}}.id",
        index=True,
        ondelete="{{this.ondelete}}"
    )
    {{/each}}
    {{/if}}

    # Fields
    {{#each fields}}
    {{this.name}}: {{this.type}} = Field({{this.constraints}})
    {{/each}}

    {{#if timestamps}}
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    {{/if}}

    {{#if softDelete}}
    deleted_at: Optional[datetime] = Field(default=None)
    {{/if}}

    {{#if hasRelationships}}
    # Relationships
    {{#each relationships}}
    {{this.name}}: "{{this.model}}" = Relationship(back_populates="{{this.back_populates}}")
    {{/each}}
    {{/if}}

    {{#if hasIndexes}}
    # Indexes
    __table_args__ = (
        {{#each indexes}}
        Index('{{this.name}}', {{this.columns}}),
        {{/each}}
    )
    {{/if}}

    class Config:
        json_schema_extra = {
            "example": {{exampleJson}}
        }

    def __repr__(self):
        return f"<{{EntityName}} {self.id}{{#if titleField}}: {self.{{titleField}}}{{/if}}>"
```

### Validation Template

```python
from pydantic import validator


class {{EntityName}}(SQLModel, table=True):
    # ... fields ...

    @validator('email')
    def validate_email(cls, v):
        """Ensure email is valid."""
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower()

    @validator('priority')
    def validate_priority(cls, v):
        """Ensure priority is in allowed values."""
        allowed = ['low', 'medium', 'high']
        if v not in allowed:
            raise ValueError(f'Priority must be one of {allowed}')
        return v
```

## Best Practices

### 1. **Always Add User Foreign Key**

```python
# Every user-owned model should have user_id
user_id: int = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
```

### 2. **Use Cascading Deletes Appropriately**

```python
# CASCADE: Delete children when parent is deleted
task_id: int = Field(foreign_key="tasks.id", ondelete="CASCADE")

# SET NULL: Set to NULL when parent is deleted
template_id: Optional[int] = Field(foreign_key="templates.id", ondelete="SET NULL")

# RESTRICT: Prevent deletion if children exist
category_id: int = Field(foreign_key="categories.id", ondelete="RESTRICT")
```

### 3. **Add Indexes for Foreign Keys and Frequently Queried Fields**

```python
# Index foreign keys (improves JOIN performance)
task_id: int = Field(foreign_key="tasks.id", index=True)

# Index fields used in WHERE clauses
status: str = Field(max_length=20, index=True)
priority: str = Field(max_length=20, index=True)
```

### 4. **Use Composite Indexes for Common Query Patterns**

```python
__table_args__ = (
    # Optimize queries like: WHERE user_id = X AND status = Y
    Index('idx_task_user_status', 'user_id', 'status'),

    # Optimize queries like: WHERE task_id = X ORDER BY display_order
    Index('idx_subtask_task_order', 'task_id', 'display_order'),
)
```

### 5. **Set Appropriate String Lengths**

```python
# Short strings (titles, names, emails)
title: str = Field(max_length=200)
email: str = Field(max_length=255)

# Medium strings (descriptions)
description: Optional[str] = Field(max_length=1000)

# Long strings (unlimited text)
content: str = Field(sa_column=Column(Text))
```

### 6. **Add Validation Constraints**

```python
# Non-negative numbers
file_size: int = Field(ge=0)
display_order: int = Field(ge=0)

# Value ranges
priority_score: int = Field(ge=1, le=10)

# Required vs Optional
title: str = Field(nullable=False)  # Required
description: Optional[str] = Field(default=None)  # Optional
```

### 7. **Use Proper Relationship Definitions**

```python
# One-to-Many (Parent side)
class Task(SQLModel, table=True):
    subtasks: list["Subtask"] = Relationship(back_populates="task")

# Many-to-One (Child side)
class Subtask(SQLModel, table=True):
    task: "Task" = Relationship(back_populates="subtasks")
```

## Advanced Features

### Enum Fields

```python
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    priority: Priority = Field(default=Priority.MEDIUM)
```

### JSON Fields

```python
from sqlalchemy import Column, JSON

class Task(SQLModel, table=True):
    metadata: dict = Field(default={}, sa_column=Column(JSON))
    tags: list[str] = Field(default=[], sa_column=Column(JSON))
```

### Computed Fields

```python
from sqlmodel import Field, computed_field

class Task(SQLModel, table=True):
    subtasks: list["Subtask"] = Relationship(back_populates="task")

    @computed_field
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage from subtasks."""
        if not self.subtasks:
            return 0.0
        completed = sum(1 for s in self.subtasks if s.completed)
        return (completed / len(self.subtasks)) * 100
```

### Soft Delete

```python
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    deleted_at: Optional[datetime] = Field(default=None)

    def soft_delete(self):
        """Mark task as deleted without removing from database."""
        self.deleted_at = datetime.utcnow()

    @property
    def is_deleted(self) -> bool:
        """Check if task is soft-deleted."""
        return self.deleted_at is not None
```

### Unique Constraints

```python
from sqlalchemy import UniqueConstraint

class User(SQLModel, table=True):
    email: str = Field(max_length=255, unique=True)

    __table_args__ = (
        # Composite unique constraint
        UniqueConstraint('user_id', 'email', name='uix_user_email'),
    )
```

## Testing

### Model Test Template

```python
import pytest
from sqlmodel import Session, create_engine, select
from app.models import Task, Subtask


def test_create_subtask(session: Session):
    """Test creating a subtask."""
    task = Task(title="Test task", user_id=1)
    session.add(task)
    session.commit()

    subtask = Subtask(
        task_id=task.id,
        user_id=1,
        title="Test subtask",
        completed=False,
        display_order=0
    )
    session.add(subtask)
    session.commit()

    assert subtask.id is not None
    assert subtask.task_id == task.id
    assert subtask.completed is False


def test_cascade_delete(session: Session):
    """Test that subtasks are deleted when task is deleted."""
    task = Task(title="Test task", user_id=1)
    session.add(task)
    session.commit()

    subtask = Subtask(task_id=task.id, user_id=1, title="Subtask")
    session.add(subtask)
    session.commit()

    session.delete(task)
    session.commit()

    # Subtask should be deleted due to CASCADE
    result = session.exec(select(Subtask).where(Subtask.id == subtask.id)).first()
    assert result is None
```

## Migration Integration

After creating models, generate Alembic migration:

```bash
/skill alembic-migration --changes=add_subtasks_table
```

## Checklist

When generating models, ensure:

- [ ] Primary key is defined (id: Optional[int])
- [ ] Foreign keys use proper ondelete strategy
- [ ] All foreign keys are indexed
- [ ] String fields have max_length constraints
- [ ] Numeric fields have ge/le constraints where appropriate
- [ ] Timestamps (created_at, updated_at) are added
- [ ] Relationships are bidirectional with back_populates
- [ ] Composite indexes are added for common query patterns
- [ ] Example JSON is provided in Config
- [ ] __repr__ method is implemented
- [ ] Validation is added for business rules

## Related Skills

- `alembic-migration` - Generate migrations after creating models
- `fastapi-crud` - Generate CRUD routes for models
- `test-generator` - Generate model tests
