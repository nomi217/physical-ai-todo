# FastAPI CRUD Generator Skill

## Purpose
Generate complete CRUD endpoints for FastAPI with proper error handling, validation, and database operations.

## When to Use
- Creating new resource endpoints (tasks, subtasks, notes, attachments, etc.)
- Need standard REST operations (GET, POST, PUT, PATCH, DELETE)
- Want consistent error handling and response formats

## Inputs Required
- **Resource Name**: Name of the resource (e.g., "Subtask", "Note")
- **Schema**: Pydantic schemas (Create, Update, Response)
- **Model**: SQLModel table class
- **Route Prefix**: API route prefix (e.g., "/api/v1/subtasks")

## Process

### 1. Create Route File
```python
# backend/app/routes/{resource_plural}.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional

from app.database import get_session
from app.models import {Resource}
from app.schemas import {Resource}Create, {Resource}Update, {Resource}Response
from app.auth.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1/{resource_plural}", tags=["{resource_plural}"])
```

### 2. List Endpoint (GET /)
```python
@router.get("", response_model=List[{Resource}Response])
def list_{resource_plural}(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all {resource_plural} for current user"""
    query = select({Resource}).where({Resource}.user_id == current_user.id)
    query = query.limit(limit).offset(offset)
    result = session.execute(query)
    items = result.scalars().all()
    return items
```

### 3. Create Endpoint (POST /)
```python
@router.post("", response_model={Resource}Response, status_code=201)
def create_{resource}(
    data: {Resource}Create,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create new {resource}"""
    new_item = {Resource}(
        **data.model_dump(),
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item
```

### 4. Get Single (GET /{id})
```python
@router.get("/{{{resource}_id}}", response_model={Resource}Response)
def get_{resource}(
    {resource}_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get single {resource} by ID"""
    result = session.execute(
        select({Resource}).where(
            {Resource}.id == {resource}_id,
            {Resource}.user_id == current_user.id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    return item
```

### 5. Update (PATCH /{id})
```python
@router.patch("/{{{resource}_id}}", response_model={Resource}Response)
def update_{resource}(
    {resource}_id: int,
    data: {Resource}Update,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update {resource}"""
    item = session.get({Resource}, {resource}_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="{Resource} not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
```

### 6. Delete (DELETE /{id})
```python
@router.delete("/{{{resource}_id}}", status_code=204)
def delete_{resource}(
    {resource}_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete {resource}"""
    item = session.get({Resource}, {resource}_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="{Resource} not found")

    session.delete(item)
    session.commit()
    return None
```

### 7. Register Router
```python
# In backend/app/main.py
from app.routes import {resource_plural}

app.include_router({resource_plural}.router)
```

## Best Practices
- Always filter by `user_id` for multi-user apps
- Use `exclude_unset=True` for PATCH to only update provided fields
- Return 404 for not found, 201 for created, 204 for deleted
- Add query parameters for filtering/sorting on list endpoints
- Use proper HTTP status codes
- Include docstrings for auto-generated API docs
- Validate ownership before allowing updates/deletes

## Example Usage
To create CRUD for "Subtask":
1. Resource: "Subtask"
2. Schemas: SubtaskCreate, SubtaskUpdate, SubtaskResponse
3. Model: Subtask (from models.py)
4. Prefix: "/api/v1/subtasks"
5. Apply template, replace placeholders
6. Test endpoints with curl or Postman

## Output
Complete route file with 6 endpoints ready to use.
