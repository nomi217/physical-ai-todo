# OCR Service Skill

## Purpose
Extract text from images and PDFs using Tesseract OCR.

## Process

### Backend OCR Service
```python
import pytesseract
from PIL import Image
import io

def extract_text_from_image(image_bytes: bytes) -> str:
    """Extract text from image using OCR"""
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return text.strip()

# In routes
@router.post("/api/v1/attachments/{id}/ocr")
async def process_ocr(
    id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    attachment = session.get(Attachment, id)
    if not attachment or attachment.task.user_id != current_user.id:
        raise HTTPException(status_code=404)

    # Download file, extract text
    text = extract_text_from_image(file_bytes)
    attachment.ocr_text = text
    session.commit()

    return {"text": text}
```

## Output
OCR service for image text extraction.
