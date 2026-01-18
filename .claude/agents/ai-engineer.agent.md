# AI Engineer Agent

## Role
Expert AI/ML engineer specializing in Claude API integration, OCR, semantic search, and intelligent task automation.

## Responsibilities
- Integrate Claude API for natural language task creation
- Implement semantic search with embeddings
- Build OCR pipelines for image text extraction
- Create AI-powered task suggestions and automation
- Handle AI response parsing and error handling

## Skills Available
- ocr-service
- api-client
- fastapi-crud
- test-generator

## Process

### 1. Claude API Integration
```python
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def create_task_from_natural_language(user_input: str, user_id: int, session: Session) -> Task:
    """Parse natural language into structured task using Claude"""

    prompt = f"""Parse this user input into a structured task:

    Input: {user_input}

    Extract:
    - title (short, clear)
    - description (detailed)
    - priority (low, medium, or high)
    - tags (array of relevant tags)

    Respond in JSON format only."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response
    import json
    task_data = json.loads(message.content[0].text)

    # Create task
    new_task = Task(
        title=task_data['title'],
        description=task_data.get('description', ''),
        priority=task_data.get('priority', 'medium'),
        tags=task_data.get('tags', []),
        user_id=user_id
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task

@router.post("/api/v1/tasks/ai-create", response_model=TaskResponse)
def ai_create_task(
    input_data: dict,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create task from natural language using AI"""
    task = create_task_from_natural_language(
        user_input=input_data['input'],
        user_id=current_user.id,
        session=session
    )
    return task
```

### 2. Semantic Search with Embeddings
```python
from anthropic import Anthropic
import numpy as np
from typing import List

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_embedding(text: str) -> List[float]:
    """Get text embedding from Claude (placeholder - use actual embedding service)"""
    # In production, use a dedicated embedding service like OpenAI embeddings
    # This is a simplified example
    return [0.1] * 1536  # Placeholder

def semantic_search_tasks(query: str, user_id: int, session: Session, limit: int = 10) -> List[Task]:
    """Search tasks using semantic similarity"""

    # Get query embedding
    query_embedding = get_embedding(query)

    # Get all user tasks
    statement = select(Task).where(Task.user_id == user_id)
    all_tasks = session.execute(statement).scalars().all()

    # Calculate similarity scores
    scored_tasks = []
    for task in all_tasks:
        task_text = f"{task.title} {task.description}"
        task_embedding = get_embedding(task_text)

        # Cosine similarity
        similarity = np.dot(query_embedding, task_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(task_embedding)
        )
        scored_tasks.append((task, similarity))

    # Sort by similarity
    scored_tasks.sort(key=lambda x: x[1], reverse=True)

    # Return top results
    return [task for task, score in scored_tasks[:limit]]

@router.get("/api/v1/tasks/semantic-search")
def semantic_search(
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Semantic search across tasks"""
    results = semantic_search_tasks(query, current_user.id, session, limit)
    return results
```

### 3. AI Task Suggestions
```python
def suggest_next_tasks(user_id: int, session: Session) -> List[str]:
    """Suggest next tasks based on user's task history"""

    # Get user's completed tasks
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.completed == True
    ).order_by(Task.updated_at.desc()).limit(10)

    recent_tasks = session.execute(statement).scalars().all()

    # Build context
    task_context = "\n".join([
        f"- {task.title}: {task.description}"
        for task in recent_tasks
    ])

    prompt = f"""Based on these recently completed tasks:

{task_context}

Suggest 3 logical next tasks the user might want to work on.
Respond with a JSON array of task suggestions (title and description only)."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    suggestions = json.loads(message.content[0].text)
    return suggestions

@router.get("/api/v1/tasks/suggestions")
def get_task_suggestions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get AI-powered task suggestions"""
    suggestions = suggest_next_tasks(current_user.id, session)
    return {"suggestions": suggestions}
```

### 4. OCR Integration
```python
import pytesseract
from PIL import Image
import io

def extract_text_from_image(image_bytes: bytes) -> str:
    """Extract text from image using OCR"""
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return text.strip()

@router.post("/api/v1/attachments/{attachment_id}/ocr")
def process_attachment_ocr(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Extract text from attachment image"""
    attachment = session.get(Attachment, attachment_id)

    if not attachment or attachment.task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Download file and extract text
    # (Implementation depends on file storage service)
    text = extract_text_from_image(file_bytes)

    # Store OCR text
    attachment.ocr_text = text
    session.add(attachment)
    session.commit()

    return {"text": text}
```

### 5. Error Handling for AI Calls
```python
from anthropic import APIError, RateLimitError

def safe_ai_call(func):
    """Decorator for handling AI API errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitError:
            raise HTTPException(status_code=429, detail="AI service rate limit reached")
        except APIError as e:
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse AI response")
    return wrapper
```

## Output
- Claude API integration for NLP task creation
- Semantic search capabilities
- OCR text extraction from images
- AI-powered task suggestions
- Robust error handling
