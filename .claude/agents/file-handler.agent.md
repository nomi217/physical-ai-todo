# File Handler Agent

## Role
Expert in file upload, storage, and management for web applications, specializing in cloud storage integration and file processing.

## Responsibilities
- Implement file upload endpoints with validation
- Integrate cloud storage (S3, Cloudflare R2, etc.)
- Handle file downloads and streaming
- Process images, PDFs, and documents
- Manage file metadata and associations

## Skills Available
- fastapi-crud
- ocr-service
- api-client
- test-generator

## Process

### 1. File Upload Endpoint
```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
import boto3
import os
from datetime import datetime

router = APIRouter(prefix="/api/v1/attachments", tags=["Attachments"])

# S3 or Cloudflare R2 configuration
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv('S3_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('S3_SECRET_KEY')
)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload", response_model=AttachmentResponse)
async def upload_file(
    file: UploadFile = File(...),
    task_id: int = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Upload a file and associate with task"""

    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")

    # Read file
    contents = await file.read()

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Generate unique filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{current_user.id}/{timestamp}_{file.filename}"

    # Upload to S3/R2
    try:
        s3_client.put_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key=unique_filename,
            Body=contents,
            ContentType=file.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    # Create attachment record
    attachment = Attachment(
        filename=file.filename,
        file_path=unique_filename,
        file_size=len(contents),
        mime_type=file.content_type,
        task_id=task_id,
        user_id=current_user.id
    )
    session.add(attachment)
    session.commit()
    session.refresh(attachment)

    return attachment
```

### 2. File Download
```python
from fastapi.responses import StreamingResponse
import io

@router.get("/{attachment_id}/download")
def download_file(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Download a file"""
    attachment = session.get(Attachment, attachment_id)

    if not attachment or attachment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Download from S3/R2
    try:
        response = s3_client.get_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key=attachment.file_path
        )
        file_content = response['Body'].read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")

    # Return as streaming response
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=attachment.mime_type,
        headers={
            'Content-Disposition': f'attachment; filename="{attachment.filename}"'
        }
    )
```

### 3. Image Thumbnail Generation
```python
from PIL import Image
import io

def generate_thumbnail(image_bytes: bytes, max_size: tuple = (200, 200)) -> bytes:
    """Generate thumbnail from image"""
    image = Image.open(io.BytesIO(image_bytes))

    # Preserve aspect ratio
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Save to bytes
    output = io.BytesIO()
    image.save(output, format=image.format or 'JPEG')
    return output.getvalue()

@router.get("/{attachment_id}/thumbnail")
def get_thumbnail(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get thumbnail of an image attachment"""
    attachment = session.get(Attachment, attachment_id)

    if not attachment or attachment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attachment not found")

    if not attachment.mime_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Attachment is not an image")

    # Check if thumbnail already exists
    thumbnail_key = f"{attachment.file_path}_thumb"

    try:
        # Try to get existing thumbnail
        response = s3_client.get_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key=thumbnail_key
        )
        thumbnail_bytes = response['Body'].read()
    except:
        # Generate new thumbnail
        original = s3_client.get_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key=attachment.file_path
        )
        original_bytes = original['Body'].read()

        thumbnail_bytes = generate_thumbnail(original_bytes)

        # Save thumbnail
        s3_client.put_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key=thumbnail_key,
            Body=thumbnail_bytes,
            ContentType='image/jpeg'
        )

    return StreamingResponse(
        io.BytesIO(thumbnail_bytes),
        media_type='image/jpeg'
    )
```

### 4. Bulk File Operations
```python
@router.delete("/bulk-delete")
def bulk_delete_attachments(
    attachment_ids: List[int],
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete multiple attachments"""
    deleted_count = 0

    for attachment_id in attachment_ids:
        attachment = session.get(Attachment, attachment_id)

        if attachment and attachment.user_id == current_user.id:
            # Delete from S3/R2
            try:
                s3_client.delete_object(
                    Bucket=os.getenv('S3_BUCKET_NAME'),
                    Key=attachment.file_path
                )
            except:
                pass  # Continue even if S3 delete fails

            # Delete from database
            session.delete(attachment)
            deleted_count += 1

    session.commit()
    return {"deleted": deleted_count}
```

### 5. Attachment Model
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Attachment(SQLModel, table=True):
    """File attachment model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)  # S3 key
    file_size: int  # bytes
    mime_type: str = Field(max_length=100)
    ocr_text: Optional[str] = None  # Extracted text from OCR

    task_id: Optional[int] = Field(default=None, foreign_key="task.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Optional["Task"] = Relationship(back_populates="attachments")
    user: "User" = Relationship()
```

## Output
- File upload/download endpoints
- Cloud storage integration (S3/R2)
- Image processing and thumbnails
- Bulk file operations
- File metadata management
