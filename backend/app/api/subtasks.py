"""Subtask CRUD API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.database import get_session
from app.models import Subtask, Task
from app.auth.dependencies import get_current_user, User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/tasks/{task_id}/subtasks", tags=["Subtasks"])


# Schemas
class SubtaskCreate(BaseModel):
    """Schema for creating a subtask"""
    title: str


class SubtaskUpdate(BaseModel):
    """Schema for updating a subtask"""
    title: str | None = None
    completed: bool | None = None
    display_order: int | None = None


class SubtaskResponse(BaseModel):
    """Schema for subtask responses"""
    id: int
    task_id: int
    user_id: int
    title: str
    completed: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Endpoints
@router.get("", response_model=List[SubtaskResponse])
def list_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all subtasks for a task"""
    # Verify task ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get subtasks ordered by display_order
    statement = select(Subtask).where(
        Subtask.task_id == task_id
    ).order_by(Subtask.display_order, Subtask.created_at)

    subtasks = session.execute(statement).scalars().all()
    return subtasks


@router.post("", response_model=SubtaskResponse, status_code=201)
def create_subtask(
    task_id: int,
    subtask_data: SubtaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new subtask"""
    # Verify task ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get max display_order
    max_order = session.execute(
        select(Subtask.display_order).where(Subtask.task_id == task_id).order_by(Subtask.display_order.desc()).limit(1)
    ).scalar_one_or_none() or 0

    # Create subtask
    new_subtask = Subtask(
        task_id=task_id,
        user_id=current_user.id,
        title=subtask_data.title,
        display_order=max_order + 1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(new_subtask)

    # Update task's updated_at
    task.updated_at = datetime.utcnow()
    session.add(task)

    session.commit()
    session.refresh(new_subtask)
    return new_subtask


@router.get("/{subtask_id}", response_model=SubtaskResponse)
def get_subtask(
    task_id: int,
    subtask_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a single subtask"""
    subtask = session.get(Subtask, subtask_id)

    if not subtask or subtask.task_id != task_id or subtask.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    return subtask


@router.put("/{subtask_id}", response_model=SubtaskResponse)
def update_subtask(
    task_id: int,
    subtask_id: int,
    subtask_data: SubtaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a subtask"""
    subtask = session.get(Subtask, subtask_id)

    if not subtask or subtask.task_id != task_id or subtask.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    # Update fields
    update_data = subtask_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(subtask, key, value)

    subtask.updated_at = datetime.utcnow()
    session.add(subtask)

    # Update parent task's updated_at
    task = session.get(Task, task_id)
    if task:
        task.updated_at = datetime.utcnow()
        session.add(task)

    session.commit()
    session.refresh(subtask)
    return subtask


@router.delete("/{subtask_id}", status_code=204)
def delete_subtask(
    task_id: int,
    subtask_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a subtask"""
    subtask = session.get(Subtask, subtask_id)

    if not subtask or subtask.task_id != task_id or subtask.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    session.delete(subtask)

    # Update parent task's updated_at
    task = session.get(Task, task_id)
    if task:
        task.updated_at = datetime.utcnow()
        session.add(task)

    session.commit()
