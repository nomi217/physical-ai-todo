# SQLModel Schema Generator Skill

## Purpose
Generate SQLModel table classes and Pydantic schemas with proper relationships, indexes, and validation.

## When to Use
- Creating new database models
- Adding relationships between models
- Need request/response schemas

## Inputs Required
- **Model Name**: Singular PascalCase (e.g., "Subtask")
- **Fields**: List of fields with types
- **Relationships**: Foreign keys and relationships
- **Indexes**: Fields that need indexing

## Process

### 1. Table Model
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class {Model}(SQLModel, table=True):
    """
{Model} model for {purpose}
    """
    __tablename__ = "{model_plural}"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    user_id: int = Field(foreign_key="user.id", index=True)
    parent_id: Optional[int] = Field(foreign_key="{parent}.id", index=True, nullable=True)

    # Fields
    title: str = Field(max_length=500, index=True)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = Field(default=False, index=True)
    display_order: int = Field(default=0, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="{model_plural}")
    parent: Optional["{Parent}"] = Relationship(back_populates="{model_plural}")
    children: List["{Child}"] = Relationship(back_populates="{model}", cascade_delete=True)
```

### 2. Enum Types
```python
class {EnumName}(str, Enum):
    """{EnumName} values"""
    VALUE1 = "value1"
    VALUE2 = "value2"
    VALUE3 = "value3"
```

### 3. Request Schemas (Pydantic)
```python
from pydantic import BaseModel, Field
from typing import Optional

class {Model}Create(BaseModel):
    """Schema for creating {model}"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    parent_id: Optional[int] = None
    display_order: int = Field(default=0, ge=0)

class {Model}Update(BaseModel):
    """Schema for updating {model}"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    completed: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)

class {Model}Response(BaseModel):
    """Schema for {model} responses"""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 4. Common Field Patterns

**User Association:**
```python
user_id: int = Field(foreign_key="user.id", index=True)
user: Optional["User"] = Relationship(back_populates="{model_plural}")
```

**Self-Referencing (Parent/Child):**
```python
parent_id: Optional[int] = Field(foreign_key="{model}.id", index=True, nullable=True)
parent: Optional["{Model}"] = Relationship(back_populates="children", sa_relationship_kwargs={"remote_side": "id"})
children: List["{Model}"] = Relationship(back_populates="parent")
```

**JSON Fields:**
```python
tags: Optional[str] = Field(default="[]", max_length=1000)  # Store as JSON string
metadata: Optional[str] = Field(default="{}", max_length=5000)  # Store as JSON string
```

**Enums:**
```python
status: Status = Field(default=Status.PENDING, index=True)
```

**Soft Delete:**
```python
deleted_at: Optional[datetime] = Field(default=None, index=True)
is_deleted: bool = Field(default=False, index=True)
```

## Best Practices
- Always add indexes on foreign keys
- Index fields used in WHERE/ORDER BY clauses
- Use Optional[] for nullable fields
- Set sensible max_length constraints
- Add default values where appropriate
- Use cascade_delete=True for dependent relationships
- Add docstrings to models
- Use Enums for fixed value sets
- Validate constraints with Field()
- Use from_attributes=True for ORM compatibility

## Output
Complete model and schema definitions ready to import.
