# API Examples - Phase II

**Base URL**: `http://localhost:8000` (development) | `https://api.todo.example.com` (production)

---

## Task Management

### 1. Create a Task

**Request**:
```http
POST /api/v1/tasks
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "tags": ["shopping", "urgent"]
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "high",
  "tags": ["shopping", "urgent"],
  "created_at": "2025-12-07T10:00:00Z",
  "updated_at": "2025-12-07T10:00:00Z"
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "high",
    "tags": ["shopping", "urgent"]
  }'
```

---

### 2. List All Tasks

**Request**:
```http
GET /api/v1/tasks
```

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "priority": "high",
      "tags": ["shopping", "urgent"],
      "created_at": "2025-12-07T10:00:00Z",
      "updated_at": "2025-12-07T10:00:00Z"
    },
    {
      "id": 2,
      "title": "Complete project report",
      "description": "",
      "completed": true,
      "priority": "medium",
      "tags": ["work"],
      "created_at": "2025-12-06T14:30:00Z",
      "updated_at": "2025-12-07T09:00:00Z"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

---

### 3. Search Tasks

**Request**:
```http
GET /api/v1/tasks?search=groceries&completed=false&priority=high
```

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "priority": "high",
      "tags": ["shopping", "urgent"],
      "created_at": "2025-12-07T10:00:00Z",
      "updated_at": "2025-12-07T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**cURL**:
```bash
curl "http://localhost:8000/api/v1/tasks?search=groceries&completed=false&priority=high"
```

---

### 4. Get Single Task

**Request**:
```http
GET /api/v1/tasks/1
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "high",
  "tags": ["shopping", "urgent"],
  "created_at": "2025-12-07T10:00:00Z",
  "updated_at": "2025-12-07T10:00:00Z"
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "not_found",
  "message": "Task with ID 999 not found"
}
```

---

### 5. Update Task (Full Replace)

**Request**:
```http
PUT /api/v1/tasks/1
Content-Type: application/json

{
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas",
  "priority": "medium",
  "tags": ["shopping"],
  "completed": false
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas",
  "completed": false,
  "priority": "medium",
  "tags": ["shopping"],
  "created_at": "2025-12-07T10:00:00Z",
  "updated_at": "2025-12-07T10:15:00Z"
}
```

---

### 6. Partial Update Task

**Request**:
```http
PATCH /api/v1/tasks/1
Content-Type: application/json

{
  "completed": true
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas",
  "completed": true,
  "priority": "medium",
  "tags": ["shopping"],
  "created_at": "2025-12-07T10:00:00Z",
  "updated_at": "2025-12-07T10:20:00Z"
}
```

---

### 7. Delete Task

**Request**:
```http
DELETE /api/v1/tasks/1
```

**Response** (200 OK):
```json
{
  "message": "Task deleted successfully"
}
```

---

## Voice Commands

### 8. Transcribe Voice

**Request**:
```http
POST /api/v1/voice/transcribe
Content-Type: application/json

{
  "audio": "base64_encoded_audio_data...",
  "language": "en"
}
```

**Response** (200 OK):
```json
{
  "transcript": "Add task buy milk",
  "language": "en",
  "confidence": 0.95
}
```

---

### 9. Execute Voice Command

**Request**:
```http
POST /api/v1/voice/command
Content-Type: application/json

{
  "transcript": "Add task buy milk",
  "language": "en"
}
```

**Response** (200 OK):
```json
{
  "action": "create_task",
  "result": {
    "id": 3,
    "title": "Buy milk",
    "description": "",
    "completed": false,
    "priority": "medium",
    "tags": [],
    "created_at": "2025-12-07T10:30:00Z",
    "updated_at": "2025-12-07T10:30:00Z"
  }
}
```

---

## AI Chatbot

### 10. Send Chat Message (Streaming)

**Request**:
```http
POST /api/v1/chat/message
Content-Type: application/json

{
  "content": "What tasks do I have?",
  "language": "en"
}
```

**Response** (200 OK - Server-Sent Events):
```
data: You
data:  have
data:  2
data:  tasks
data: :
data:  \n1
data: .
data:  Buy
data:  groceries
data:  (
data: high
data:  priority
data: )\n
data: 2
data: .
data:  Complete
data:  project
data:  report
data:  (
data: completed
data: )
```

**JavaScript Example**:
```javascript
const response = await fetch('http://localhost:8000/api/v1/chat/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: 'What tasks do I have?',
    language: 'en'
  })
})

const reader = response.body.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break

  const chunk = decoder.decode(value)
  const lines = chunk.split('\n')

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const text = line.slice(6)
      console.log(text) // Process streaming text
    }
  }
}
```

---

### 11. Get Chat History

**Request**:
```http
GET /api/v1/chat/history?limit=10
```

**Response** (200 OK):
```json
{
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "What tasks do I have?",
      "language": "en",
      "created_at": "2025-12-07T10:30:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "You have 2 tasks:\n1. Buy groceries (high priority)\n2. Complete project report (completed)",
      "language": "en",
      "created_at": "2025-12-07T10:30:01Z"
    }
  ]
}
```

---

### 12. Clear Chat History

**Request**:
```http
DELETE /api/v1/chat/history
```

**Response** (200 OK):
```json
{
  "message": "Chat history cleared"
}
```

---

## Filter, Sort & Pagination Examples

### Filter by Multiple Tags
```http
GET /api/v1/tasks?tags=work,urgent
```

### Sort by Priority (High → Low)
```http
GET /api/v1/tasks?sort=priority&order=desc
```

### Pagination
```http
GET /api/v1/tasks?limit=10&offset=20
```

### Combined Filters
```http
GET /api/v1/tasks?search=meeting&completed=false&priority=high&sort=created_at&order=desc&limit=20
```

---

## Error Responses

### Validation Error (422)
```json
{
  "error": "validation_error",
  "message": "Title cannot be empty",
  "details": {
    "field": "title",
    "constraint": "minLength"
  }
}
```

### Not Found (404)
```json
{
  "error": "not_found",
  "message": "Task with ID 999 not found"
}
```

### Internal Error (500)
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

---

## Multi-language Examples

### Create Task in Urdu
```http
POST /api/v1/tasks
Content-Type: application/json

{
  "title": "خریداری کریں",
  "description": "دودھ، انڈے، روٹی",
  "priority": "high",
  "tags": ["خریداری"]
}
```

### Chat in Arabic
```http
POST /api/v1/chat/message
Content-Type: application/json

{
  "content": "ما هي المهام العاجلة؟",
  "language": "ar"
}
```

### Voice Command in Spanish
```http
POST /api/v1/voice/command
Content-Type: application/json

{
  "transcript": "Agregar tarea comprar leche",
  "language": "es"
}
```

---

## Rate Limiting

**Headers** (for chat endpoints):
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701950400
```

**Rate Limit Exceeded (429)**:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Try again in 60 seconds."
}
```

---

## Testing with Postman

1. **Import OpenAPI Spec**: Import `openapi.yaml` into Postman
2. **Set Base URL**: Configure environment variable `{{baseUrl}}` = `http://localhost:8000`
3. **Test Collection**: Run all endpoints in sequence
4. **Environment**: Create separate environments for dev/staging/prod

## Testing with HTTPie

```bash
# Create task
http POST :8000/api/v1/tasks title="Buy milk" priority=high

# List tasks
http :8000/api/v1/tasks search==milk

# Update task
http PATCH :8000/api/v1/tasks/1 completed:=true

# Delete task
http DELETE :8000/api/v1/tasks/1
```
