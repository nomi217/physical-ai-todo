# Phase III AI Chatbot: Quickstart Implementation Guide

**Feature**: Phase III - AI-Powered Conversational Task Management
**Date**: 2025-12-13
**Status**: Phase 1 - Design Complete

## Overview

This guide provides step-by-step instructions for implementing the AI chatbot feature from scratch. Follow these steps in order for successful implementation.

**Total Estimated Time**: 3-4 weeks (40-60 tasks)

---

## Prerequisites Check

### Required Software

**Backend**:
- ✅ Python 3.13+ installed (`python --version`)
- ✅ pip package manager (`pip --version`)
- ✅ PostgreSQL client (psql) for migrations

**Frontend**:
- ✅ Node.js 18+ installed (`node --version`)
- ✅ npm package manager (`npm --version`)

**Services**:
- ✅ Neon PostgreSQL database (from Phase II)
- ✅ OpenAI API account with GPT-4 Turbo access

### Phase II Dependencies (Must Be Complete)

- ✅ **Authentication system**: JWT tokens, user sessions
- ✅ **Task CRUD operations**: `backend/app/crud.py`, `backend/app/routes/tasks.py`
- ✅ **User model**: `backend/app/models.py`
- ✅ **Database connection**: `backend/app/database.py` (Neon connection working)
- ✅ **Frontend i18n**: `frontend/contexts/I18nContext.tsx` (for multi-language support)

### API Keys Required

**OpenAI API Key**:
1. Sign up at https://platform.openai.com/
2. Navigate to API Keys section
3. Create new key with GPT-4 Turbo access
4. **Minimum spend**: $5 for Tier 1 (60k TPM, 500 RPM)

**Verify OpenAI Access**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY"
# Should return list of models including "gpt-4-turbo-preview"
```

---

## Step 1: Installation

### Backend Dependencies

**Install MCP SDK and OpenAI SDK**:
```bash
cd backend
pip install mcp openai>=1.0.0
pip freeze > requirements.txt  # Update requirements
```

**Verify Installation**:
```python
# Test in Python REPL
python
>>> import mcp
>>> import openai
>>> print(openai.__version__)
# Should print >= 1.0.0
```

### Environment Variables

**Update `.env` file**:
```bash
# Add to backend/.env
OPENAI_API_KEY=sk-...your-key-here...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Rate limiting (optional)
CHAT_RATE_LIMIT_PER_MINUTE=100
```

**Load in application** (backend/app/main.py):
```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")
```

---

## Step 2: Database Migration

### Create Migration File

**Option A: Auto-generate** (recommended):
```bash
cd backend
alembic revision --autogenerate -m "Add conversation_messages table for AI chatbot"
```

**Option B: Manual migration** (if autogenerate fails):
```bash
alembic revision -m "Add conversation_messages table"
# Then copy schema from data-model.md into generated migration file
```

### Review Migration

**Edit** `backend/alembic/versions/XXX_add_conversation_messages.py`:
- Verify table schema matches `data-model.md`
- Verify indexes are created correctly
- Verify foreign key constraint with CASCADE delete

### Apply Migration

```bash
alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade XXX -> YYY, Add conversation_messages table
```

### Verify Schema

```bash
# Connect to Neon database
psql $DATABASE_URL

# Check table structure
\d conversation_messages

# Expected columns: id, conversation_id, user_id, role, content, tool_calls, created_at, updated_at

# Check indexes
\di conversation_messages*

# Expected 3 indexes:
# - idx_conversation_messages_conversation_id_created_at
# - idx_conversation_messages_user_id_conversation_id
# - idx_conversation_messages_user_id_created_at
```

---

## Step 3: MCP Server Setup

### Create MCP Module

**Directory structure**:
```bash
mkdir -p backend/app/mcp
touch backend/app/mcp/__init__.py
touch backend/app/mcp/tools.py
touch backend/app/mcp/schemas.py
touch backend/app/mcp/server.py
```

### Implement MCP Tools

**File**: `backend/app/mcp/tools.py`

**Step 3.1: Import dependencies**:
```python
from mcp import Tool
from pydantic import BaseModel, Field
from backend.app.crud import (
    create_task, get_tasks, update_task_status,
    delete_task, update_task
)
```

**Step 3.2: Define tool schemas** (see `contracts/mcp-tools.yaml`):
```python
class AddTaskParams(BaseModel):
    user_id: int = Field(..., description="User ID")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")
    tags: list[str] = Field(default_factory=list)
```

**Step 3.3: Implement tools** (10 tools from contract):
```python
@Tool(
    name="add_task",
    description="Create a new task for the user. Use this when the user wants to add, create, or remember something.",
)
def add_task(params: AddTaskParams) -> dict:
    """Add a new task to the user's todo list."""
    task = create_task(
        user_id=params.user_id,
        title=params.title,
        description=params.description,
        priority=params.priority,
        tags=params.tags
    )
    return {
        "status": "success",
        "task_id": task.id,
        "message": f"Created task '{task.title}' with ID {task.id}"
    }

# Implement remaining 9 tools: list_tasks, complete_task, delete_task, update_task,
# set_priority, manage_tags, manage_subtasks, search_tasks, filter_tasks
```

**Step 3.4: Register tools**:
```python
# At end of tools.py
MCP_TOOLS = [
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    set_priority,
    manage_tags,
    manage_subtasks,
    search_tasks,
    filter_tasks
]
```

### Test MCP Tools

**Unit tests** (`backend/tests/test_mcp_tools.py`):
```python
import pytest
from backend.app.mcp.tools import add_task, AddTaskParams

def test_add_task(test_db, test_user):
    """Test add_task MCP tool."""
    params = AddTaskParams(
        user_id=test_user.id,
        title="Buy groceries",
        description="Get milk and eggs",
        priority="medium",
        tags=["shopping"]
    )

    result = add_task(params)

    assert result["status"] == "success"
    assert result["task_id"] is not None
    assert "Buy groceries" in result["message"]

# Write tests for all 10 tools
```

**Run tests**:
```bash
pytest backend/tests/test_mcp_tools.py -v
```

---

## Step 4: OpenAI Agent Integration

### Create Chat Module

**Directory structure**:
```bash
mkdir -p backend/app/chat
touch backend/app/chat/__init__.py
touch backend/app/chat/agent.py
touch backend/app/chat/prompts.py
touch backend/app/chat/conversation.py
```

### System Prompt

**File**: `backend/app/chat/prompts.py`
```python
SYSTEM_PROMPT = """
You are a helpful task management assistant. Your goal is to help users manage their todo lists through natural conversation.

**Your capabilities**:
- Add, update, delete, and complete tasks
- Search and filter tasks by priority, tags, or status
- Manage subtasks for complex projects
- Set priorities and organize with tags

**Guidelines**:
- Be friendly and conversational
- Confirm actions: "I've added 'Buy groceries' to your list!"
- If you need more information, ask clarifying questions
- If multiple tasks match a description, ask which one the user means
- Detect the user's language and respond in the same language (English, Urdu, Arabic, Spanish, French, German)

**Tools available**: You have access to 10 MCP tools for task operations. Use them to help users efficiently.
""".strip()
```

### OpenAI Agent

**File**: `backend/app/chat/agent.py`
```python
import os
import json
from openai import OpenAI
from backend.app.mcp.tools import MCP_TOOLS

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def convert_mcp_tools_to_openai(mcp_tools):
    """Convert MCP tools to OpenAI function calling format."""
    openai_tools = []
    for tool in mcp_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.params.model_json_schema()
            }
        })
    return openai_tools

def execute_chat(user_id, messages, max_iterations=5):
    """
    Execute AI chat with MCP tool calling support.

    Args:
        user_id: Authenticated user ID (injected into all tool calls)
        messages: Conversation history (list of dicts)
        max_iterations: Max tool calling iterations

    Returns:
        Tuple (assistant_response: str, tool_calls: list)
    """
    openai_tools = convert_mcp_tools_to_openai(MCP_TOOLS)

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
            temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.7))
        )

        assistant_message = response.choices[0].message

        # No tool calls - final response
        if assistant_message.finish_reason == "stop":
            return assistant_message.content, []

        # Execute tool calls
        if assistant_message.tool_calls:
            tool_results = []

            # Append assistant message to history
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [tc.model_dump() for tc in assistant_message.tool_calls]
            })

            # Execute each tool
            for tool_call in assistant_message.tool_calls:
                tool = next(t for t in MCP_TOOLS if t.name == tool_call.function.name)

                # Parse arguments and inject user_id
                args = json.loads(tool_call.function.arguments)
                args["user_id"] = user_id  # Security: authenticated user only

                # Execute tool
                params_class = tool.__annotations__["params"]
                result = tool(params=params_class(**args))
                tool_results.append({
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                        "result": json.dumps(result)
                    }
                })

                # Append tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            # Continue iteration
            continue

        break

    # If max iterations reached
    return "I apologize, but I encountered an issue processing your request.", []
```

### Conversation Management

**File**: `backend/app/chat/conversation.py`
```python
from sqlmodel import Session, select, func
from backend.app.database import engine
from backend.app.models import ConversationMessage
import json

def create_new_conversation(user_id: int) -> int:
    """Generate new conversation ID."""
    with Session(engine) as session:
        max_id = session.exec(
            select(func.max(ConversationMessage.conversation_id))
        ).scalar()
        return (max_id or 0) + 1

def save_message(conversation_id, user_id, role, content, tool_calls=None):
    """Save message to database."""
    with Session(engine) as session:
        message = ConversationMessage(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

def load_conversation_history(conversation_id, user_id, max_messages=20):
    """Load recent conversation messages."""
    with Session(engine) as session:
        messages = session.exec(
            select(ConversationMessage)
            .where(
                ConversationMessage.conversation_id == conversation_id,
                ConversationMessage.user_id == user_id
            )
            .order_by(ConversationMessage.created_at.desc())
            .limit(max_messages)
        ).all()

        # Reverse to chronological order
        messages = list(reversed(messages))

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "tool_calls": msg.tool_calls
            }
            for msg in messages
        ]
```

---

## Step 5: Chat API Endpoint

### Create Chat Router

**File**: `backend/app/routes/chat.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.app.auth.dependencies import get_current_user
from backend.app.models import User
from backend.app.chat.agent import execute_chat
from backend.app.chat.prompts import SYSTEM_PROMPT
from backend.app.chat.conversation import (
    create_new_conversation,
    save_message,
    load_conversation_history
)

router = APIRouter(prefix="/api/v1", tags=["chat"])

class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Stateless chat endpoint with conversation persistence.

    See contracts/chat-api.yaml for full API documentation.
    """
    # Validate message
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Load or create conversation
    if request.conversation_id:
        messages = load_conversation_history(
            request.conversation_id,
            current_user.id,
            max_messages=20
        )
        conversation_id = request.conversation_id
    else:
        messages = []
        conversation_id = create_new_conversation(current_user.id)

    # Add system prompt if first message
    if len(messages) == 0:
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    # Add user message
    messages.append({"role": "user", "content": request.message})
    save_message(conversation_id, current_user.id, "user", request.message)

    # Execute AI chat
    try:
        assistant_response, tool_calls = execute_chat(current_user.id, messages)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="AI service temporarily unavailable. Please try again."
        )

    # Save assistant response
    save_message(
        conversation_id,
        current_user.id,
        "assistant",
        assistant_response,
        tool_calls=tool_calls if tool_calls else None
    )

    return ChatResponse(
        conversation_id=conversation_id,
        response=assistant_response,
        tool_calls=tool_calls
    )
```

### Register Router

**File**: `backend/app/main.py`
```python
from backend.app.routes import chat

app.include_router(chat.router)
```

### Test Chat Endpoint

**Manual test with curl**:
```bash
# Login to get JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.access_token')

# Send chat message
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add buy groceries to my list"}' \
  | jq .

# Expected output:
# {
#   "conversation_id": 1,
#   "response": "I've added 'Buy groceries' to your task list!",
#   "tool_calls": [{"id": "call_...", "function": {"name": "add_task", ...}}]
# }
```

---

## Step 6: Frontend Integration

### Create Chat Components

**Directory structure**:
```bash
mkdir -p frontend/components/chat
touch frontend/components/chat/ChatInterface.tsx
touch frontend/components/chat/MessageList.tsx
touch frontend/components/chat/MessageItem.tsx
touch frontend/components/chat/ChatInput.tsx
touch frontend/components/chat/ConversationSidebar.tsx
touch frontend/components/chat/TypingIndicator.tsx
touch frontend/components/chat/ToolCallDisplay.tsx
```

### Chat Context

**File**: `frontend/contexts/ChatContext.tsx`
```typescript
"use client";
import React, { createContext, useContext, useState } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  tool_calls?: any[];
}

interface ChatContextType {
  conversationId: number | null;
  messages: Message[];
  isLoading: boolean;
  sendMessage: (message: string) => Promise<void>;
  startNewConversation: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (message: string) => {
    setIsLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: message }]);

    try {
      const response = await fetch("/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // Send cookies
        body: JSON.stringify({
          conversation_id: conversationId,
          message,
        }),
      });

      const data = await response.json();
      setConversationId(data.conversation_id);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          tool_calls: data.tool_calls,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewConversation = () => {
    setConversationId(null);
    setMessages([]);
  };

  return (
    <ChatContext.Provider
      value={{ conversationId, messages, isLoading, sendMessage, startNewConversation }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error("useChat must be used within ChatProvider");
  return context;
};
```

### Chat Interface

**File**: `frontend/components/chat/ChatInterface.tsx` (simplified):
```typescript
"use client";
import React from "react";
import { useChat } from "@/contexts/ChatContext";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";

export function ChatInterface() {
  const { messages, sendMessage, isLoading } = useChat();

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-purple-900 to-blue-900 p-6">
      <div className="flex-1 backdrop-blur-xl bg-white/10 rounded-3xl p-6 flex flex-col">
        <h1 className="text-2xl font-bold text-white mb-4">AI Assistant</h1>
        <MessageList messages={messages} />
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
```

### Add to Dashboard

**File**: `frontend/app/dashboard/page.tsx` (add chat tab):
```typescript
import { ChatInterface } from "@/components/chat/ChatInterface";
import { ChatProvider } from "@/contexts/ChatContext";

export default function Dashboard() {
  return (
    <ChatProvider>
      <div className="flex">
        {/* Existing task UI */}
        <div className="flex-1">{/* Task list */}</div>

        {/* New chat sidebar */}
        <div className="w-96 border-l border-white/20">
          <ChatInterface />
        </div>
      </div>
    </ChatProvider>
  );
}
```

---

## Step 7: Testing

### Backend Tests

```bash
# Unit tests (MCP tools, models)
pytest backend/tests/test_mcp_tools.py -v
pytest backend/tests/test_models.py -v

# Integration tests (chat endpoint)
pytest backend/tests/test_chat_api.py -v

# Coverage report
pytest --cov=backend/app --cov-report=html
```

### Frontend Tests

```bash
# Component tests
npm test -- chat

# E2E tests (manual for Phase III)
# 1. Start frontend: npm run dev
# 2. Login as test user
# 3. Navigate to dashboard
# 4. Open chat sidebar
# 5. Test conversation: "Add buy groceries"
# 6. Verify task appears in task list
```

---

## Step 8: Deployment Checklist

- [ ] Environment variables set (OPENAI_API_KEY)
- [ ] Database migrations applied (conversation_messages table exists)
- [ ] OpenAI API key validated (test with curl)
- [ ] Backend tests passing (80%+ coverage)
- [ ] Frontend tests passing
- [ ] Rate limiting configured (optional)
- [ ] Monitoring/logging enabled (optional)
- [ ] PHR created for Phase III implementation

---

## Troubleshooting

**Issue**: "OpenAI API rate limit exceeded"
**Solution**: Check OpenAI dashboard usage, upgrade to Tier 2 if needed

**Issue**: "Database connection pool exhausted"
**Solution**: Verify NullPool configuration, check Neon connection limits

**Issue**: "Chat endpoint returns 401 Unauthorized"
**Solution**: Verify JWT token is being sent, check Phase II auth system

**Issue**: "Tool execution errors"
**Solution**: Check CRUD functions exist, verify user_id injection

---

**Version**: 1.0.0
**Created**: 2025-12-13
**Status**: Phase 1 Design Complete

**Next**: Run `/sp.tasks` to generate granular implementation tasks
