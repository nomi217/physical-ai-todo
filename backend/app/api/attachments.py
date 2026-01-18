"""Attachment CRUD API endpoints with file upload"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List
from datetime import datetime
import os
import shutil
from pathlib import Path

from app.database import get_session
from app.models import Attachment, Task
from app.auth.dependencies import get_current_user, User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/tasks/{task_id}/attachments", tags=["Attachments"])

# File upload configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx'}


# Schemas
class AttachmentResponse(BaseModel):
    """Schema for attachment responses"""
    id: int
    task_id: int
    user_id: int
    filename: str
    file_url: str
    file_size: int
    mime_type: str
    ocr_text: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Endpoints
@router.get("", response_model=List[AttachmentResponse])
def list_attachments(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all attachments for a task"""
    # Verify task ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get attachments
    statement = select(Attachment).where(
        Attachment.task_id == task_id
    ).order_by(Attachment.created_at.desc())

    attachments = session.execute(statement).scalars().all()
    return attachments


@router.post("", response_model=AttachmentResponse, status_code=201)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Upload a file attachment"""
    # Verify task ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file and check size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB")

    # Generate unique filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{current_user.id}_{task_id}_{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    try:
        with open(file_path, 'wb') as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    # Create attachment record
    new_attachment = Attachment(
        task_id=task_id,
        user_id=current_user.id,
        filename=file.filename,
        file_url=f"/uploads/{unique_filename}",
        file_size=len(contents),
        mime_type=file.content_type or 'application/octet-stream',
        created_at=datetime.utcnow()
    )
    session.add(new_attachment)

    # Update task's updated_at
    task.updated_at = datetime.utcnow()
    session.add(task)

    session.commit()
    session.refresh(new_attachment)
    return new_attachment


@router.get("/{attachment_id}", response_model=AttachmentResponse)
def get_attachment(
    task_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a single attachment"""
    attachment = session.get(Attachment, attachment_id)

    if not attachment or attachment.task_id != task_id or attachment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attachment not found")

    return attachment


@router.delete("/{attachment_id}", status_code=204)
def delete_attachment(
    task_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete an attachment"""
    attachment = session.get(Attachment, attachment_id)

    if not attachment or attachment.task_id != task_id or attachment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Delete file from filesystem
    file_path = UPLOAD_DIR / os.path.basename(attachment.file_url)
    if file_path.exists():
        try:
            os.remove(file_path)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Failed to delete file {file_path}: {e}")

    # Delete from database
    session.delete(attachment)

    # Update parent task's updated_at
    task = session.get(Task, task_id)
    if task:
        task.updated_at = datetime.utcnow()
        session.add(task)

    session.commit()
