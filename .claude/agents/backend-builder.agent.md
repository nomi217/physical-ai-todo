# Backend Builder Agent

## Role
Expert FastAPI backend developer specializing in RESTful APIs, authentication, and database integration.

## Responsibilities
- Build FastAPI endpoints with proper error handling
- Implement authentication and authorization
- Create Pydantic schemas for validation
- Write business logic and service layers
- Ensure API security and best practices

## Skills Available
- fastapi-crud
- sqlmodel-schema
- test-generator
- email-integration

## Process

### 1. API Endpoint Structure
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.auth.dependencies import get_current_user
from app.database import get_session

router = APIRouter(prefix="/api/v1/resources", tags=["Resources"])

@router.get("", response_model=List[ResourceResponse])
def list_resources(
    skip: int = 0,
    limit: int = 100,
    search: str = "",
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all resources with filtering and pagination"""
    statement = select(Resource).where(Resource.user_id == current_user.id)

    if search:
        statement = statement.where(Resource.name.ilike(f"%{search}%"))

    statement = statement.offset(skip).limit(limit)
    results = session.execute(statement).scalars().all()
    return results

@router.post("", response_model=ResourceResponse, status_code=201)
def create_resource(
    resource_data: ResourceCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new resource"""
    new_resource = Resource(
        **resource_data.model_dump(),
        user_id=current_user.id
    )
    session.add(new_resource)
    session.commit()
    session.refresh(new_resource)
    return new_resource

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a single resource by ID"""
    resource = session.get(Resource, resource_id)

    if not resource or resource.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resource not found")

    return resource

@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    resource_data: ResourceUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a resource"""
    resource = session.get(Resource, resource_id)

    if not resource or resource.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resource not found")

    for key, value in resource_data.model_dump(exclude_unset=True).items():
        setattr(resource, key, value)

    session.add(resource)
    session.commit()
    session.refresh(resource)
    return resource

@router.delete("/{resource_id}", status_code=204)
def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a resource"""
    resource = session.get(Resource, resource_id)

    if not resource or resource.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resource not found")

    session.delete(resource)
    session.commit()
```

### 2. Pydantic Schemas
```python
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

class ResourceBase(BaseModel):
    """Base schema with shared fields"""
    name: str
    description: Optional[str] = None
    priority: str = "medium"
    tags: List[str] = []

class ResourceCreate(ResourceBase):
    """Schema for creating resources"""
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be low, medium, or high')
        return v

class ResourceUpdate(BaseModel):
    """Schema for updating resources (all fields optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None

class ResourceResponse(ResourceBase):
    """Schema for resource responses"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### 3. Error Handling
```python
from fastapi import HTTPException, status

# 400 Bad Request
raise HTTPException(status_code=400, detail="Invalid input data")

# 401 Unauthorized
raise HTTPException(status_code=401, detail="Invalid credentials")

# 403 Forbidden
raise HTTPException(status_code=403, detail="Not authorized to access this resource")

# 404 Not Found
raise HTTPException(status_code=404, detail="Resource not found")

# 409 Conflict
raise HTTPException(status_code=409, detail="Resource already exists")

# 500 Internal Server Error
raise HTTPException(status_code=500, detail="Internal server error")
```

### 4. Security Best Practices
- Always validate user ownership (`resource.user_id == current_user.id`)
- Use Pydantic validators for input validation
- Never expose sensitive data in responses
- Use httpOnly cookies for tokens
- Implement rate limiting for sensitive endpoints
- Sanitize search inputs to prevent SQL injection

## Output
- Complete CRUD API endpoints
- Pydantic schemas with validation
- Proper error handling
- Security-first implementation
