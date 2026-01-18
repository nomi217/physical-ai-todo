"""Note CRUD API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.database import get_session
from app.models import Note, Task
from app.auth.dependencies import get_current_user, User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/tasks/{task_id}/notes", tags=["Notes"])


# Schemas
class NoteCreate(BaseModel):
    """Schema for creating a note"""
    content: str


class NoteUpdate(BaseModel):
    """Schema for updating a note"""
    content: str


class NoteResponse(BaseModel):
    """Schema for note responses"""
    id: int
    task_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Endpoints
@router.get("", response_model=List[NoteResponse])
def list_notes(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all notes for a task"""
    # Verify task ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get notes ordered by created_at (newest first)
    statement = select(Note).where(
        Note.task_id == task_id
    ).order_by(Note.created_at.desc())

    notes = session.execute(statement).scalars().all()
    return notes


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(
    task_id: int,
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new note"""
    # Verify task ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Create note
    new_note = Note(
        task_id=task_id,
        user_id=current_user.id,
        content=note_data.content,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(new_note)

    # Update task's updated_at
    task.updated_at = datetime.utcnow()
    session.add(task)

    session.commit()
    session.refresh(new_note)
    return new_note


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    task_id: int,
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a single note"""
    note = session.get(Note, note_id)

    if not note or note.task_id != task_id or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    task_id: int,
    note_id: int,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a note"""
    note = session.get(Note, note_id)

    if not note or note.task_id != task_id or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update content
    note.content = note_data.content
    note.updated_at = datetime.utcnow()
    session.add(note)

    # Update parent task's updated_at
    task = session.get(Task, task_id)
    if task:
        task.updated_at = datetime.utcnow()
        session.add(task)

    session.commit()
    session.refresh(note)
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(
    task_id: int,
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a note"""
    note = session.get(Note, note_id)

    if not note or note.task_id != task_id or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")

    session.delete(note)

    # Update parent task's updated_at
    task = session.get(Task, task_id)
    if task:
        task.updated_at = datetime.utcnow()
        session.add(task)

    session.commit()
