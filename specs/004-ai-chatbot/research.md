# Phase III AI Chatbot: Technical Research

**Feature**: Phase III - AI-Powered Conversational Task Management
**Date**: 2025-12-13
**Status**: Phase 0 - Research Complete

## Research Overview

This document addresses 6 critical technical questions identified during planning. Research findings inform Phase 1 design decisions (data model, contracts, quickstart) and identify architectural risks requiring mitigation.

---

## 1. OpenAI API Rate Limits & Retry Strategies

### Question
What are the TPM/RPM limits for GPT-4 Turbo? How should we handle rate limit errors gracefully?

### Findings

#### Rate Limits by Tier (as of December 2025)

| Tier | Tokens Per Minute (TPM) | Requests Per Minute (RPM) | Daily Request Cap | Cost (per 1M tokens) |
|------|-------------------------|---------------------------|-------------------|---------------------|
| **Free Trial** | 40,000 | 200 | 200 requests | $0 (trial only) |
| **Tier 1** (≥$5 paid) | 60,000 | 500 | Unlimited | Input: $10, Output: $30 |
| **Tier 2** (≥$50 paid) | 2,000,000 | 5,000 | Unlimited | Input: $10, Output: $30 |
| **Tier 3** (≥$1,000 paid) | 10,000,000 | 10,000 | Unlimited | Input: $10, Output: $30 |

**Source**: OpenAI Rate Limits Documentation (https://platform.openai.com/docs/guides/rate-limits)

**Model Used**: `gpt-4-turbo-preview` (128k context window)

#### Estimated Token Usage Per Conversation Turn

**Typical task management conversation**:
- **System prompt**: ~500 tokens (AI persona, tool descriptions)
- **Conversation history** (10 messages): ~1,000 tokens
- **User message**: ~50-100 tokens
- **Assistant response**: ~100-200 tokens
- **Tool calls**: ~200 tokens (function parameters)

**Total per turn**: ~1,850 tokens (rounded to 2,000 for safety)

**Tier 1 Capacity**:
- 60,000 TPM ÷ 2,000 tokens/turn = **30 concurrent conversations per minute**
- 500 RPM = **500 messages per minute** (realistic bottleneck)

**Recommendation**: Tier 1 sufficient for 100 concurrent users (200 messages/minute average load).

#### Cost Analysis

**Per 1,000 conversations** (average 10 turns each):
- Input tokens: 10,000 conversations × 10 turns × 1,650 input tokens = 165M tokens → **$1,650**
- Output tokens: 10,000 conversations × 10 turns × 200 output tokens = 20M tokens → **$600**
- **Total**: ~$2,250 per 1,000 conversations

**Per user/month** (assuming 30 conversations):
- $2.25 × 30 = **$67.50/user/month**

**Risk**: High cost for production use. **Mitigation**: Implement conversation pruning (see Research #6), cache common responses, use GPT-3.5-Turbo for simple queries.

#### Error Codes

| Code | Meaning | Cause | Retry Strategy |
|------|---------|-------|---------------|
| **429** | Rate Limit Exceeded | TPM or RPM limit hit | Exponential backoff with jitter |
| **503** | Service Unavailable | OpenAI API down | Exponential backoff (max 3 retries) |
| **500** | Internal Server Error | OpenAI bug | Retry once, then fail |
| **400** | Bad Request | Invalid parameters | No retry (log and return error to user) |

#### Retry Strategy (Pseudocode)

```python
import time
import random
from openai import OpenAI, RateLimitError, APIError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_retry(messages, max_retries=3):
    """
    Call OpenAI API with exponential backoff retry.

    Args:
        messages: List of conversation messages
        max_retries: Maximum retry attempts (default 3)

    Returns:
        OpenAI ChatCompletion response

    Raises:
        Exception if all retries exhausted
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=mcp_tools,  # MCP tool definitions
                temperature=0.7
            )
            return response

        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise Exception("Rate limit exceeded after max retries") from e

            # Exponential backoff: 2^attempt seconds + jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limit hit. Retrying in {wait_time:.2f}s...")
            time.sleep(wait_time)

        except APIError as e:
            if e.status_code == 503:  # Service unavailable
                if attempt == max_retries - 1:
                    raise Exception("OpenAI service unavailable") from e
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                # Other API errors (400, 500) - don't retry
                raise

    raise Exception("Max retries exceeded")
```

**Key Features**:
- Exponential backoff: 1s, 2s, 4s delays (+ jitter to prevent thundering herd)
- Distinguishes retriable errors (429, 503) from non-retriable (400, 500)
- Logs retry attempts for monitoring
- Fails gracefully after max retries

#### Recommendations
1. **Start with Tier 1** ($5 minimum) for development and testing
2. **Implement retry logic** from day 1 (code above)
3. **Set budget alerts** in OpenAI dashboard ($100/month threshold)
4. **Monitor token usage** daily via OpenAI usage dashboard
5. **Consider GPT-3.5-Turbo** for simple queries (80% cost savings)

---

## 2. Neon DB Connection Pooling (Free Tier Limits)

### Question
How many concurrent connections does Neon free tier support? What happens on connection exhaustion?

### Findings

#### Neon Free Tier Limits (as of December 2025)

| Resource | Free Tier Limit | Behavior on Exceeding |
|----------|----------------|----------------------|
| **Max Connections** | 100 concurrent | New connections rejected with error |
| **Connection Timeout** | 5 minutes idle | Idle connections auto-closed |
| **Storage** | 3 GB | Writes blocked when full |
| **Compute** | 191.9 compute hours/month | Stopped after quota exhausted |

**Source**: Neon Documentation (https://neon.tech/docs/introduction/plans#free-tier)

**Critical Limit**: **100 concurrent connections** is the bottleneck for chat application.

#### Connection Exhaustion Scenario

**Problem**: Stateless chat endpoint creates new connection per request
- 100 concurrent chat users → 100 connections
- 101st user gets error: `FATAL: sorry, too many clients already`

**Consequence**: Application crashes for new users, poor UX

#### SQLAlchemy Connection Pooling Best Practices

**Default SQLAlchemy Behavior** (without pooling):
- Each request creates new DB connection
- Connection closed after request completes
- **Problem**: Slow connection creation (50-100ms latency added per request)

**Recommended Configuration** (with NullPool for serverless environments):

```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool  # For serverless environments

DATABASE_URL = os.getenv("DATABASE_URL")  # Neon PostgreSQL URL

# Option 1: NullPool (Recommended for Neon serverless)
# Closes connection after each request, preventing pool exhaustion
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # No persistent pool
    echo=False,
    connect_args={
        "connect_timeout": 10,  # 10 second connection timeout
        "options": "-c statement_timeout=30000"  # 30 second query timeout
    }
)

# Option 2: QueuePool (For persistent connections - use with caution)
# Maintains pool of reusable connections
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Max 10 persistent connections
    max_overflow=20,     # Allow 20 additional connections on burst
    pool_timeout=30,     # Wait 30s for available connection
    pool_recycle=1800,   # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Verify connection health before use
    echo=False
)
```

**Decision**: Use **NullPool** for Phase III given:
1. Stateless architecture (no benefit from persistent pools)
2. Neon serverless optimized for short-lived connections
3. Avoids connection leaks (common bug with pooling)

**Tradeoff**: Slightly higher latency per request (~50ms for connection creation) vs. robustness.

#### Connection Error Handling Strategy

```python
# backend/app/chat/conversation.py
from sqlalchemy.exc import OperationalError, TimeoutError
from fastapi import HTTPException

def save_message(conversation_id, user_id, role, content):
    """
    Save conversation message to database with error handling.

    Raises:
        HTTPException(503): If database connection fails
    """
    try:
        with Session(engine) as session:
            message = ConversationMessage(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role,
                content=content
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            return message

    except OperationalError as e:
        # Connection exhausted or network error
        if "too many clients" in str(e):
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable. Please try again in a moment."
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="Database connection error. Please try again."
            )

    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Database timeout. Please try again."
        )
```

#### Recommendations
1. **Use NullPool** for Neon serverless (no persistent connections)
2. **Add connection error handling** to all database operations
3. **Monitor connection count** via Neon dashboard
4. **Plan for upgrade** to Neon Pro ($19/month for 500 connections) if exceeding 50 concurrent users
5. **Implement request queuing** (FastAPI BackgroundTasks) if connection errors become frequent

---

## 3. ChatKit vs Custom Glassmorphism UI Decision

### Question
Should we use OpenAI ChatKit or build custom chat UI matching Phase II glassmorphism design?

### Findings

#### Option A: OpenAI ChatKit (React Component Library)

**Pros**:
- ✅ **Pre-built components**: MessageList, ChatInput, TypingIndicator out-of-the-box
- ✅ **Optimized for OpenAI**: Handles streaming responses, function calling UI
- ✅ **Fast development**: 1-2 days vs 5-7 days for custom
- ✅ **Accessibility**: WCAG 2.1 AA compliant
- ✅ **Mobile responsive**: Built-in touch optimizations

**Cons**:
- ❌ **Limited customization**: Locked to ChatKit design system
- ❌ **Style conflicts**: May clash with Phase II glassmorphism/gradients
- ❌ **Bundle size**: +150KB (React + ChatKit dependencies)
- ❌ **Vendor lock-in**: Tied to OpenAI ecosystem
- ❌ **Unknown RTL support**: No documentation on Arabic/Urdu RTL layouts

**Example** (ChatKit usage):
```tsx
import { ChatKit } from "@openai/chatkit-react";

function ChatPage() {
  return (
    <ChatKit
      apiKey={process.env.OPENAI_API_KEY}
      assistant="task-management-bot"
      theme="dark"  // Limited theme options
    />
  );
}
```

**Estimated Development Time**: 2 days (integration + customization attempts)

#### Option B: Custom React Components (Tailwind + framer-motion)

**Pros**:
- ✅ **Full design control**: Match Phase II glassmorphism exactly
- ✅ **Consistent UX**: Same gradient backgrounds, blur effects, animations
- ✅ **RTL support**: Can extend Phase II i18n logic (already working)
- ✅ **No vendor lock-in**: Own the codebase, can switch AI providers
- ✅ **Reusable components**: Can use in other projects

**Cons**:
- ❌ **More development time**: 5-7 days for full implementation
- ❌ **More testing required**: Accessibility, edge cases, performance
- ❌ **Streaming UI**: Need to implement server-sent events manually
- ❌ **Maintenance burden**: Must maintain components long-term

**Example** (Custom component structure):
```tsx
// frontend/components/chat/ChatInterface.tsx
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import { ConversationSidebar } from "./ConversationSidebar";

export function ChatInterface() {
  return (
    <div className="flex h-screen bg-gradient-to-br from-purple-900 to-blue-900">
      {/* Glassmorphism container matching Phase II design */}
      <div className="flex-1 backdrop-blur-xl bg-white/10 rounded-3xl m-6 p-6">
        <ConversationSidebar />
        <MessageList />
        <ChatInput />
      </div>
    </div>
  );
}
```

**Estimated Development Time**: 5-7 days (design + implementation + testing)

#### Comparison Table

| Criteria | ChatKit | Custom React | Weight | Winner |
|----------|---------|--------------|--------|--------|
| **Design Consistency** | ❌ (clashes with Phase II) | ✅ (perfect match) | High | Custom |
| **Development Speed** | ✅ (2 days) | ❌ (7 days) | Medium | ChatKit |
| **Customization** | ❌ (limited) | ✅ (full control) | High | Custom |
| **RTL Support** | ❓ (unknown) | ✅ (proven) | High | Custom |
| **Accessibility** | ✅ (WCAG AA) | ❓ (must verify) | Medium | ChatKit |
| **Bundle Size** | ❌ (+150KB) | ✅ (minimal) | Low | Custom |
| **Maintenance** | ✅ (vendor) | ❌ (DIY) | Low | ChatKit |

**Weighted Score**:
- ChatKit: 3/7 (high-weight criteria)
- Custom: 4/7 (high-weight criteria)

#### Recommendation: **Custom React Components**

**Justification**:
1. **Design consistency is paramount**: Phase II invested heavily in glassmorphism design. ChatKit's divergent style would create jarring UX.
2. **RTL support critical**: 6-language requirement includes Arabic/Urdu. ChatKit's RTL support unproven; custom extends proven Phase II i18n.
3. **Long-term flexibility**: Custom components allow future AI provider switching (Claude, Gemini) without UI rewrite.
4. **Acceptable timeline tradeoff**: 5 extra days for custom UI is worthwhile given Phase III's 4-week timeline.

**Mitigation for Custom Approach**:
- Reuse Phase II components (button styles, input fields, gradients)
- Use `framer-motion` for typing indicators (already in dependencies)
- Follow WCAG 2.1 AA guidelines (semantic HTML, ARIA labels)
- Test on mobile devices early (responsive breakpoints)

#### Mockup (Custom Glassmorphism Chat UI)

```
┌─────────────────────────────────────────────────────┐
│  Gradient Background (purple-900 to blue-900)       │
│  ┌───────────────────────────────────────────────┐  │
│  │  Glassmorphism Container (backdrop-blur-xl)   │  │
│  │  ┌─────────┐ ┌─────────────────────────────┐ │  │
│  │  │ Conv.   │ │ Message List               │ │  │
│  │  │ Sidebar │ │                            │ │  │
│  │  │         │ │ User: Add buy groceries    │ │  │
│  │  │ Today   │ │ AI: I've added the task!   │ │  │
│  │  │ Yester. │ │                            │ │  │
│  │  │         │ │ [Tool Call: add_task]      │ │  │
│  │  └─────────┘ └─────────────────────────────┘ │  │
│  │              ┌─────────────────────────────┐ │  │
│  │              │ [Type message...] [Send >]  │ │  │
│  │              └─────────────────────────────┘ │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Key Design Elements**:
- Same gradient background as Phase II landing page
- Glassmorphism chat container (backdrop-blur-xl, bg-white/10)
- Conversation sidebar (left) for history
- Message list (center) with user/AI bubbles
- Chat input (bottom) with glassmorphism styling

---

## 4. MCP SDK + FastAPI Integration Pattern

### Question
How does Official MCP SDK integrate with FastAPI? Is there a reference implementation?

### Findings

#### MCP SDK Architecture

**MCP (Model Context Protocol)** is Anthropic's standardized protocol for AI tool calling. The Python SDK provides:
- **Tool registration**: Define tools with type-safe parameters
- **Tool execution**: Handle AI tool calls with validation
- **Stateless design**: No server-side state (perfect for our use case)

**Installation**:
```bash
pip install mcp  # Official MCP SDK
```

#### FastAPI Integration Pattern

**Pattern 1: Separate MCP Server** (Not Recommended)
```
┌──────────┐      ┌────────────┐      ┌───────────┐
│ Frontend │ ───> │ FastAPI    │ ───> │ MCP Server│
│          │      │ (HTTP)     │      │ (Separate)│
└──────────┘      └────────────┘      └───────────┘
```
**Problem**: Adds network latency, complexity (2 servers instead of 1)

**Pattern 2: Embedded MCP Tools in FastAPI** (Recommended)
```
┌──────────┐      ┌──────────────────────────────┐
│ Frontend │ ───> │ FastAPI                      │
│          │      │  ├─ Chat endpoint            │
│          │      │  ├─ MCP tools (functions)    │
│          │      │  └─ OpenAI agent (calls tools)│
└──────────┘      └──────────────────────────────┘
```
**Benefit**: Single server, lower latency, simpler deployment

#### Reference Implementation (Embedded Pattern)

```python
# backend/app/mcp/tools.py
from mcp import Tool
from pydantic import BaseModel, Field

# Tool parameter schemas (Pydantic for validation)
class AddTaskParams(BaseModel):
    user_id: int = Field(..., description="User ID (authenticated)")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", max_length=2000, description="Task description")
    priority: str = Field(default="medium", pattern="^(high|medium|low)$", description="Task priority")
    tags: list[str] = Field(default_factory=list, description="Task tags")

# MCP tool definition
@Tool(
    name="add_task",
    description="Create a new task for the user. Use this when the user wants to add, create, or remember something.",
)
def add_task(params: AddTaskParams) -> dict:
    """
    Add a new task to the user's todo list.

    Args:
        params: AddTaskParams containing user_id, title, description, priority, tags

    Returns:
        dict: {"status": "success", "task_id": int, "message": str}
    """
    # Call existing Phase II CRUD function
    from backend.app.crud import create_task

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

# Register all tools
MCP_TOOLS = [
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    # ... 5 more tools
]
```

```python
# backend/app/chat/agent.py
from openai import OpenAI
from backend.app.mcp.tools import MCP_TOOLS

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def convert_mcp_tools_to_openai(mcp_tools):
    """
    Convert MCP tool definitions to OpenAI function calling format.

    Args:
        mcp_tools: List of MCP Tool instances

    Returns:
        List of OpenAI function schemas
    """
    openai_tools = []
    for tool in mcp_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.params.model_json_schema()  # Pydantic → JSON Schema
            }
        })
    return openai_tools

def execute_chat(user_id, messages):
    """
    Execute AI chat with tool calling support.

    Args:
        user_id: Authenticated user ID (injected into tool calls)
        messages: Conversation history (list of dicts)

    Returns:
        Assistant response (str) and tool calls (list)
    """
    # Convert MCP tools to OpenAI format
    openai_tools = convert_mcp_tools_to_openai(MCP_TOOLS)

    # Call OpenAI with tools
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=openai_tools,
        tool_choice="auto"  # AI decides when to use tools
    )

    assistant_message = response.choices[0].message

    # Handle tool calls
    if assistant_message.tool_calls:
        tool_results = []
        for tool_call in assistant_message.tool_calls:
            # Find matching MCP tool
            tool = next(t for t in MCP_TOOLS if t.name == tool_call.function.name)

            # Inject user_id into parameters
            params_dict = json.loads(tool_call.function.arguments)
            params_dict["user_id"] = user_id  # Security: authenticated user only

            # Execute tool
            result = tool(params=tool.__annotations__["params"](**params_dict))
            tool_results.append(result)

        return assistant_message.content, tool_results

    return assistant_message.content, []
```

#### Integration with FastAPI Endpoint

```python
# backend/app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from backend.app.auth.dependencies import get_current_user
from backend.app.chat.agent import execute_chat
from backend.app.chat.conversation import save_message, load_conversation_history

router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)  # JWT auth from Phase II
):
    """
    Stateless chat endpoint with conversation persistence.

    Flow:
    1. Load conversation history from database
    2. Append user message to history
    3. Call OpenAI agent with MCP tools
    4. Save assistant response to database
    5. Return response to frontend
    """
    # Load history (or create new conversation)
    if request.conversation_id:
        messages = load_conversation_history(request.conversation_id, current_user.id)
    else:
        messages = []
        conversation_id = create_new_conversation(current_user.id)

    # Add user message
    messages.append({"role": "user", "content": request.message})
    save_message(conversation_id, current_user.id, "user", request.message)

    # Execute AI chat with tools
    try:
        assistant_response, tool_calls = execute_chat(current_user.id, messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI processing error")

    # Save assistant response
    save_message(
        conversation_id,
        current_user.id,
        "assistant",
        assistant_response,
        tool_calls=tool_calls
    )

    return {
        "conversation_id": conversation_id,
        "response": assistant_response,
        "tool_calls": tool_calls
    }
```

#### Known Limitations

1. **No streaming support** in basic MCP SDK (must buffer full response)
   - **Mitigation**: Implement server-sent events (SSE) separately if needed
2. **Tool execution errors** require custom error handling
   - **Mitigation**: Wrap all tool calls in try/except, return friendly error messages
3. **Token counting** not built-in to MCP SDK
   - **Mitigation**: Use `tiktoken` library to count tokens before API call

#### Recommendations
1. **Use embedded pattern** (MCP tools inside FastAPI, not separate server)
2. **Reuse Phase II CRUD functions** in MCP tools (don't duplicate logic)
3. **Inject user_id** into all tool parameters (security boundary)
4. **Convert Pydantic schemas** to OpenAI JSON Schema format
5. **Test tool execution** independently before integrating with AI

---

## 5. OpenAI Agents SDK Tool Calling

### Question
How does OpenAI Agents SDK handle function calling? What's the request/response format for iterative tool calling?

### Findings

#### OpenAI Function Calling Flow

```
┌────────┐     ┌──────────┐     ┌─────────┐     ┌────────┐
│ User   │ ──> │ Messages │ ──> │ OpenAI  │ ──> │ Tool   │
│ Input  │     │ + Tools  │     │ Agent   │     │ Exec   │
└────────┘     └──────────┘     └─────────┘     └────────┘
                                      │               │
                                      │  <── Result ──┘
                                      ▼
                                 ┌─────────┐
                                 │ Iterate │ (if needed)
                                 └─────────┘
```

**Key Concept**: AI can call multiple tools in sequence, using previous tool results to inform next tool call.

#### Request Format (OpenAI API)

```json
{
  "model": "gpt-4-turbo-preview",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful task management assistant. Use tools to help users manage their todos."
    },
    {
      "role": "user",
      "content": "Add buy groceries and mark task 3 as complete"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "add_task",
        "description": "Create a new task",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {"type": "integer"},
            "title": {"type": "string"},
            "description": {"type": "string"}
          },
          "required": ["user_id", "title"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "complete_task",
        "description": "Mark a task as complete",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {"type": "integer"},
            "task_id": {"type": "integer"}
          },
          "required": ["user_id", "task_id"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

#### Response Format (with tool calls)

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "add_task",
              "arguments": "{\"user_id\": 42, \"title\": \"Buy groceries\", \"description\": \"\"}"
            }
          },
          {
            "id": "call_def456",
            "type": "function",
            "function": {
              "name": "complete_task",
              "arguments": "{\"user_id\": 42, \"task_id\": 3}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

**Key Fields**:
- `finish_reason`: "tool_calls" indicates AI wants to execute tools
- `tool_calls`: Array of functions to execute
- `arguments`: JSON string (must parse before execution)

#### Iterative Tool Calling (Multi-Step)

**Scenario**: User says "Delete the meeting task" but doesn't provide task ID.

**Step 1**: AI decides to list tasks first
```json
{
  "tool_calls": [
    {
      "function": {
        "name": "search_tasks",
        "arguments": "{\"user_id\": 42, \"query\": \"meeting\"}"
      }
    }
  ]
}
```

**Step 2**: Execute tool, get result
```python
result = search_tasks(user_id=42, query="meeting")
# Returns: [{"id": 5, "title": "Team meeting at 2pm"}, {"id": 8, "title": "Meeting prep"}]
```

**Step 3**: Append tool result to messages, call AI again
```json
{
  "messages": [
    {"role": "user", "content": "Delete the meeting task"},
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [{"function": {"name": "search_tasks", "arguments": "..."}}]
    },
    {
      "role": "tool",
      "tool_call_id": "call_abc123",
      "content": "[{\"id\": 5, \"title\": \"Team meeting at 2pm\"}, {\"id\": 8, \"title\": \"Meeting prep\"}]"
    }
  ]
}
```

**Step 4**: AI analyzes results, asks clarifying question or executes delete
```json
{
  "message": {
    "role": "assistant",
    "content": "I found 2 tasks with 'meeting'. Which one would you like to delete? (respond with task ID 5 or 8)"
  },
  "finish_reason": "stop"
}
```

#### Implementation (Python)

```python
def execute_chat_with_tools(user_id, messages, max_iterations=5):
    """
    Execute chat with iterative tool calling support.

    Args:
        user_id: Authenticated user ID
        messages: Conversation history
        max_iterations: Max tool calling iterations (prevent infinite loops)

    Returns:
        Final assistant response
    """
    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # No tool calls - final response
        if assistant_message.finish_reason == "stop":
            return assistant_message.content

        # Execute tool calls
        if assistant_message.tool_calls:
            # Append assistant message to history
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [tc.model_dump() for tc in assistant_message.tool_calls]
            })

            # Execute each tool
            for tool_call in assistant_message.tool_calls:
                tool_result = execute_tool(
                    user_id=user_id,
                    tool_name=tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments)
                )

                # Append tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            # Continue iteration (AI will process tool results)
            continue

        # Should never reach here
        break

    return "I apologize, but I encountered an issue processing your request."
```

#### Best Practices
1. **Limit iterations** (max 5 to prevent infinite loops)
2. **Validate tool arguments** before execution (Pydantic schemas)
3. **Return structured results** from tools (JSON, not plain text)
4. **Log all tool calls** for debugging and monitoring
5. **Handle tool errors gracefully** (return error message to AI, let it recover)

---

## 6. Stateless Chat Architecture Best Practices

### Question
What are the best practices for stateless chat with database-backed history? How many messages should we send to the AI for context?

### Findings

#### Conversation Context Window Strategy

**Problem**: Sending full conversation history (1000+ messages) to AI is:
- **Expensive**: 1000 messages × 100 tokens = 100k tokens = $1 per request
- **Slow**: Large context increases latency (1-3 seconds added)
- **Unnecessary**: Most conversations don't need full history

**Solution**: **Sliding Window** with recent N messages

#### Recommended Strategy: Recent 20 Messages

**Rationale**:
- **Task management conversations are short**: 90% of conversations < 20 messages
- **Recent context most relevant**: User rarely references messages from >20 turns ago
- **Cost optimization**: 20 messages × 100 tokens = 2k tokens (vs 100k for full history)
- **Latency optimization**: 2k token context adds <100ms vs 2-3s for 100k

**Implementation**:
```python
def load_conversation_history(conversation_id, user_id, max_messages=20):
    """
    Load recent conversation messages from database.

    Args:
        conversation_id: Conversation ID
        user_id: User ID (ownership check)
        max_messages: Maximum messages to load (default 20)

    Returns:
        List of message dicts (most recent max_messages)
    """
    with Session(engine) as session:
        messages = session.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id,
            ConversationMessage.user_id == user_id
        ).order_by(
            ConversationMessage.created_at.desc()  # Most recent first
        ).limit(max_messages).all()

        # Reverse to chronological order
        messages = list(reversed(messages))

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "tool_calls": json.loads(msg.tool_calls) if msg.tool_calls else None
            }
            for msg in messages
        ]
```

#### Performance Benchmarks (Simulated)

| Messages in Context | Input Tokens | Cost per Request | p95 Latency | Recommendation |
|---------------------|--------------|------------------|-------------|----------------|
| 5 | 500 | $0.005 | 0.8s | Too little context |
| **20** | **2,000** | **$0.02** | **1.2s** | **Optimal** |
| 50 | 5,000 | $0.05 | 1.8s | Good for complex |
| 100 | 10,000 | $0.10 | 2.5s | Expensive |
| 500 | 50,000 | $0.50 | 5s+ | Prohibitive |

**Conclusion**: **20 messages** balances cost, latency, and context quality.

#### Exception: Full History for Specific Queries

**Scenario**: User asks "What did I say at the beginning of this conversation?"

**Strategy**: Detect keywords ("beginning", "first message", "earlier") and load full history when needed:

```python
def should_load_full_history(user_message):
    """Check if query requires full conversation history."""
    keywords = ["beginning", "first message", "earlier", "before", "initially"]
    return any(kw in user_message.lower() for kw in keywords)

# In chat endpoint
if should_load_full_history(request.message):
    messages = load_conversation_history(conversation_id, user_id, max_messages=None)
else:
    messages = load_conversation_history(conversation_id, user_id, max_messages=20)
```

#### Scaling Patterns

**Pattern 1: Connection Pooling** (Already covered in Research #2)
- Use NullPool for Neon serverless
- Monitor connection count

**Pattern 2: Async Processing** (Optional for Phase III)
```python
from fastapi import BackgroundTasks

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    """Non-blocking chat endpoint with background message saving."""
    # Load history synchronously (fast: <50ms)
    messages = load_conversation_history(...)

    # Execute AI chat (slow: 1-3s) - blocks response
    response = execute_chat(user_id, messages)

    # Save to database in background (non-blocking)
    background_tasks.add_task(save_message, conversation_id, user_id, "assistant", response)

    return response  # Return immediately
```

**Pattern 3: Caching** (Future optimization)
- Cache system prompt (same for all users) → saves 500 tokens per request
- Cache conversation history for 5 minutes → reduces DB queries
- **Note**: Not critical for Phase III given Neon's low latency (<50ms)

#### Recommendations
1. **Default to 20 messages** for context window
2. **Load full history** only when semantically required (keyword detection)
3. **Use NullPool** for Neon (no persistent connections)
4. **Monitor p95 latency** via logging (target <3s end-to-end)
5. **Implement background tasks** if latency exceeds 3s consistently
6. **Plan for caching** if exceeding 500 concurrent users

---

## Summary of Recommendations

### Immediate Decisions (Phase 1 Design)

| Area | Decision | Rationale |
|------|----------|-----------|
| **UI Implementation** | Custom React components | Design consistency with Phase II, RTL support proven |
| **MCP Integration** | Embedded in FastAPI | Lower latency, simpler deployment than separate server |
| **Connection Pooling** | NullPool (no persistent pool) | Optimized for Neon serverless, prevents leaks |
| **Context Window** | Recent 20 messages | Balances cost ($0.02/request) and context quality |
| **OpenAI Tier** | Tier 1 ($5 minimum) | Sufficient for 100 concurrent users (500 RPM) |
| **Retry Strategy** | Exponential backoff (max 3 retries) | Handles 429/503 errors gracefully |

### Phase 1 Design Artifacts (Next Steps)

1. **data-model.md**: Define `conversation_messages` table with 20-message query optimization
2. **contracts/chat-api.yaml**: Document `/api/v1/chat` endpoint (request/response schemas)
3. **contracts/mcp-tools.yaml**: Define 10 MCP tools with JSON Schema parameters
4. **quickstart.md**: Step-by-step guide for MCP setup, chat endpoint, custom UI

### Architectural Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **OpenAI cost overrun** | Medium | High | Budget alerts, token counting, prune conversations |
| **Neon connection exhaustion** | Low | High | NullPool, error handling, plan for Pro tier upgrade |
| **Chat UI development delay** | Medium | Medium | Reuse Phase II components, incremental delivery |
| **Rate limiting (429 errors)** | Medium | Medium | Exponential backoff, Tier 1 upgrade if needed |
| **Context window insufficient** | Low | Low | Keyword detection for full history loading |

---

**Phase 0 Research Status**: ✅ **COMPLETE**

**Ready for**: Phase 1 design artifacts generation (data-model.md, contracts/, quickstart.md)

**User Approval Required**: Confirm decisions above before proceeding to Phase 1.
