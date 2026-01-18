# FastAPI CRUD Generator

Auto-generate complete FastAPI CRUD routes from SQLModel schemas with validation, error handling, and OpenAPI documentation.

## Purpose

Eliminate repetitive boilerplate when creating REST API endpoints. This skill generates production-ready CRUD operations (Create, Read, Update, Delete) for SQLModel entities with:
- Input validation
- Error handling
- Pagination support
- OpenAPI/Swagger documentation
- Type-safe responses

## Time Savings

**30 minutes per entity** (6 entities = 3 hours saved)

## Input Parameters

```bash
/skill fastapi-crud --model=<ModelName> --fields=<field1,field2,...> [--paginate=true] [--soft-delete=false]
```

### Required Parameters

- `--model`: SQLModel class name (e.g., `Subtask`, `Note`, `Attachment`)
- `--fields`: Comma-separated list of fields (e.g., `task_id,title,completed,display_order`)

### Optional Parameters

- `--paginate`: Enable pagination for list endpoint (default: `true`)
- `--soft-delete`: Use soft delete instead of hard delete (default: `false`)
- `--base-path`: API route prefix (default: `/api`)
- `--auth`: Require authentication (default: `true`)

## Output/Deliverables

### 1. Route File

**Location**: `backend/app/routes/<model_plural>.py`

**Contents**:
- GET `/api/<models>` - List all (with pagination)
- GET `/api/<models>/{id}` - Get single by ID
- POST `/api/<models>` - Create new
- PUT `/api/<models>/{id}` - Update existing
- DELETE `/api/<models>/{id}` - Delete

### 2. Schema Validation

- Request/response Pydantic models
- Field validation rules
- Error response schemas

### 3. Error Handling

- 400 Bad Request (validation errors)
- 404 Not Found (resource doesn't exist)
- 500 Internal Server Error (database errors)

## Usage Examples

### Example 1: Basic CRUD for Subtasks

```bash
/skill fastapi-crud --model=Subtask --fields=task_id,title,completed,display_order
```

**Generates**: `backend/app/routes/subtasks.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from app.models import Subtask
from app.database import get_session
from app.auth import get_current_user

router = APIRouter(prefix="/api/subtasks", tags=["subtasks"])


@router.get("/", response_model=List[Subtask])
async def list_subtasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    task_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """List all subtasks with optional filtering by task_id."""
    query = select(Subtask).where(Subtask.user_id == current_user.id)

    if task_id:
        query = query.where(Subtask.task_id == task_id)

    query = query.offset(skip).limit(limit).order_by(Subtask.display_order)
    subtasks = session.exec(query).all()
    return subtasks


@router.get("/{subtask_id}", response_model=Subtask)
async def get_subtask(
    subtask_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Get a single subtask by ID."""
    subtask = session.get(Subtask, subtask_id)

    if not subtask or subtask.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    return subtask


@router.post("/", response_model=Subtask, status_code=201)
async def create_subtask(
    subtask: Subtask,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Create a new subtask."""
    subtask.user_id = current_user.id
    session.add(subtask)
    session.commit()
    session.refresh(subtask)
    return subtask


@router.put("/{subtask_id}", response_model=Subtask)
async def update_subtask(
    subtask_id: int,
    updated_subtask: Subtask,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Update an existing subtask."""
    subtask = session.get(Subtask, subtask_id)

    if not subtask or subtask.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    # Update fields
    for key, value in updated_subtask.dict(exclude_unset=True).items():
        setattr(subtask, key, value)

    session.add(subtask)
    session.commit()
    session.refresh(subtask)
    return subtask


@router.delete("/{subtask_id}", status_code=204)
async def delete_subtask(
    subtask_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Delete a subtask."""
    subtask = session.get(Subtask, subtask_id)

    if not subtask or subtask.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    session.delete(subtask)
    session.commit()
    return None
```

### Example 2: CRUD with Soft Delete

```bash
/skill fastapi-crud --model=Note --fields=task_id,content,created_at --soft-delete=true
```

**Generates**: Added `deleted_at` field handling in DELETE endpoint.

### Example 3: No Authentication Required

```bash
/skill fastapi-crud --model=Template --fields=name,content,category --auth=false
```

**Generates**: Removes `get_current_user` dependency.

## Code Templates

### Base Route Template

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from app.models import {{MODEL}}
from app.database import get_session
{{#if auth}}
from app.auth import get_current_user
{{/if}}

router = APIRouter(prefix="/api/{{model_plural}}", tags=["{{model_plural}}"])


@router.get("/", response_model=List[{{MODEL}}])
async def list_{{model_plural}}(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    session: Session = Depends(get_session),
    {{#if auth}}
    current_user = Depends(get_current_user)
    {{/if}}
):
    """List all {{model_plural}}."""
    query = select({{MODEL}})
    {{#if auth}}
    query = query.where({{MODEL}}.user_id == current_user.id)
    {{/if}}
    query = query.offset(skip).limit(limit)
    items = session.exec(query).all()
    return items


# ... (CREATE, READ, UPDATE, DELETE endpoints follow)
```

### Error Response Schema

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class ValidationError(ErrorResponse):
    field: str
    message: str
```

## Best Practices

### 1. **Always Use Type Hints**

```python
# Good
async def get_subtask(subtask_id: int) -> Subtask:
    ...

# Bad
async def get_subtask(subtask_id):
    ...
```

### 2. **Include Pagination by Default**

```python
# Always add skip/limit parameters for list endpoints
skip: int = Query(0, ge=0)
limit: int = Query(100, le=1000)
```

### 3. **Validate Ownership Before Mutations**

```python
# Always check user owns the resource
if not item or item.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Not found")
```

### 4. **Use Appropriate HTTP Status Codes**

- `200 OK` - Successful GET/PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Database/server error

### 5. **Add OpenAPI Documentation**

```python
@router.post("/", response_model=Subtask, status_code=201,
             summary="Create subtask",
             description="Create a new subtask for a task",
             response_description="The created subtask")
async def create_subtask(...):
    ...
```

### 6. **Handle Database Errors Gracefully**

```python
from sqlalchemy.exc import IntegrityError

try:
    session.add(item)
    session.commit()
except IntegrityError as e:
    session.rollback()
    raise HTTPException(status_code=400, detail="Database constraint violated")
```

## Advanced Features

### Bulk Operations

```python
@router.post("/bulk", response_model=List[Subtask])
async def create_bulk_subtasks(
    subtasks: List[Subtask],
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Create multiple subtasks at once."""
    for subtask in subtasks:
        subtask.user_id = current_user.id
        session.add(subtask)

    session.commit()
    return subtasks
```

### Search and Filtering

```python
@router.get("/search", response_model=List[Task])
async def search_tasks(
    q: str = Query(..., min_length=1),
    priority: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Search tasks by title, description, or tags."""
    query = select(Task).where(
        Task.user_id == current_user.id,
        (Task.title.contains(q)) | (Task.description.contains(q))
    )

    if priority:
        query = query.where(Task.priority == priority)
    if status:
        query = query.where(Task.status == status)

    tasks = session.exec(query).all()
    return tasks
```

### Sorting

```python
@router.get("/", response_model=List[Task])
async def list_tasks(
    sort_by: str = Query("created_at", enum=["created_at", "priority", "due_date"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """List tasks with sorting."""
    query = select(Task).where(Task.user_id == current_user.id)

    # Dynamic sorting
    sort_column = getattr(Task, sort_by)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    tasks = session.exec(query).all()
    return tasks
```

## Testing

### Unit Test Template

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_subtask(auth_headers):
    """Test creating a subtask."""
    response = client.post(
        "/api/subtasks",
        json={
            "task_id": 1,
            "title": "Test subtask",
            "completed": false,
            "display_order": 0
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test subtask"
    assert "id" in data


def test_get_subtask_not_found(auth_headers):
    """Test getting non-existent subtask returns 404."""
    response = client.get("/api/subtasks/99999", headers=auth_headers)
    assert response.status_code == 404
```

## Integration with Main App

### Register Router in `main.py`

```python
from app.routes import subtasks, notes, attachments

app.include_router(subtasks.router)
app.include_router(notes.router)
app.include_router(attachments.router)
```

## Checklist

When generating CRUD routes, ensure:

- [ ] All 5 endpoints (LIST, GET, CREATE, UPDATE, DELETE) are implemented
- [ ] Pagination is added to list endpoint
- [ ] Authentication/authorization checks are in place
- [ ] Ownership validation prevents cross-user access
- [ ] Error responses use appropriate HTTP status codes
- [ ] OpenAPI documentation strings are added
- [ ] Type hints are used throughout
- [ ] Database transactions are properly committed/rolled back
- [ ] Response models match SQLModel schemas
- [ ] Router is registered in main app

## Related Skills

- `sqlmodel-schema` - Generate SQLModel definitions first
- `test-generator` - Generate tests for CRUD routes
- `api-client` - Generate TypeScript client from OpenAPI spec
