# Phase III AI Chatbot: Data Model

**Feature**: Phase III - AI-Powered Conversational Task Management
**Date**: 2025-12-13
**Status**: Phase 1 - Design Complete

## Overview

This document defines the PostgreSQL database schema for conversation persistence in the AI chatbot feature. The design follows **stateless architecture** principles: zero server-side memory, all conversation state in the database.

---

## Database Schema

### ConversationMessage Table

**Purpose**: Store all user and AI messages with tool execution history

```sql
CREATE TABLE conversation_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tool_calls JSONB DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

#### Column Definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| **id** | SERIAL | PRIMARY KEY | Auto-incrementing message ID |
| **conversation_id** | INTEGER | NOT NULL | Logical grouping of related messages (user-generated, not FK) |
| **user_id** | INTEGER | NOT NULL, FK→users(id), ON DELETE CASCADE | Message owner (authenticated user) |
| **role** | VARCHAR(20) | NOT NULL, CHECK constraint | Message sender: "user", "assistant", or "system" |
| **content** | TEXT | NOT NULL | Message text content (user input or AI response) |
| **tool_calls** | JSONB | NULLABLE | JSON array of tool executions (only for assistant messages with tools) |
| **created_at** | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Message creation timestamp (immutable) |
| **updated_at** | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Message update timestamp (for future edits) |

#### Constraints

1. **Primary Key**: `id` (auto-incrementing)
2. **Foreign Key**: `user_id` references `users(id)` with CASCADE delete
3. **Check Constraint**: `role` ∈ {"user", "assistant", "system"}
4. **NOT NULL**: All columns except `tool_calls` (assistant messages without tools have NULL)

#### Indexes

**Performance Optimization**: Indexes designed for conversation history queries (most frequent operation)

```sql
-- Index 1: Conversation history retrieval (PRIMARY USE CASE)
-- Query: SELECT * FROM conversation_messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 20
CREATE INDEX idx_conversation_messages_conversation_id_created_at
ON conversation_messages(conversation_id, created_at DESC);

-- Index 2: User ownership queries (security check)
-- Query: SELECT * FROM conversation_messages WHERE user_id = ? AND conversation_id = ?
CREATE INDEX idx_conversation_messages_user_id_conversation_id
ON conversation_messages(user_id, conversation_id);

-- Index 3: User's conversation list (conversation sidebar)
-- Query: SELECT DISTINCT conversation_id FROM conversation_messages WHERE user_id = ? ORDER BY created_at DESC
CREATE INDEX idx_conversation_messages_user_id_created_at
ON conversation_messages(user_id, created_at DESC);
```

**Index Justification**:
- **Index 1**: Composite index on `(conversation_id, created_at)` optimizes sliding window query (recent 20 messages)
- **Index 2**: Composite index on `(user_id, conversation_id)` optimizes ownership verification
- **Index 3**: Composite index on `(user_id, created_at)` optimizes conversation list for sidebar

**Query Performance** (estimated with 10k messages):
- Load 20 recent messages: <10ms (Index 1)
- Verify user owns conversation: <5ms (Index 2)
- List user's 10 recent conversations: <15ms (Index 3)

---

## Relationships

### Relationship 1: ConversationMessage → User (Many-to-One)

```
┌─────────────────────────┐       ┌──────────────┐
│ conversation_messages   │ ────> │ users        │
│                         │       │              │
│ user_id (FK)            │       │ id (PK)      │
│                         │       │ email        │
└─────────────────────────┘       └──────────────┘
```

**Cardinality**: Many ConversationMessages belong to one User

**Cascade Behavior**: ON DELETE CASCADE
- When user is deleted, all their conversation messages are deleted
- Rationale: Conversation messages are meaningless without the owning user

**Validation**: FastAPI endpoint verifies `current_user.id == conversation_message.user_id` before allowing access

### Relationship 2: Conversation (Logical Grouping)

**Note**: `conversation_id` is NOT a foreign key. It's a logical grouping field.

```
┌─────────────────────────┐
│ conversation_messages   │
│                         │
│ conversation_id = 42    │  ← Message 1 (user)
│ conversation_id = 42    │  ← Message 2 (assistant)
│ conversation_id = 42    │  ← Message 3 (user)
│ conversation_id = 42    │  ← Message 4 (assistant)
│                         │
│ conversation_id = 43    │  ← Different conversation
└─────────────────────────┘
```

**Why not a separate `conversations` table?**
- **Simplicity**: No need to manage conversation lifecycle (create, delete)
- **Stateless**: Conversations are implicitly created when first message is sent
- **Query efficiency**: No JOIN required for message retrieval

**Conversation ID Generation**:
```python
def create_new_conversation(user_id):
    """
    Generate new conversation ID (auto-increment from max existing ID).

    Returns:
        int: New conversation ID
    """
    with Session(engine) as session:
        max_id = session.query(func.max(ConversationMessage.conversation_id)).scalar()
        return (max_id or 0) + 1
```

---

## JSON Schema for tool_calls Column

**Purpose**: Store array of tool executions for assistant messages that called tools

**Schema**:
```json
[
  {
    "id": "call_abc123",
    "type": "function",
    "function": {
      "name": "add_task",
      "arguments": "{\"user_id\": 42, \"title\": \"Buy groceries\", \"description\": \"\"}",
      "result": "{\"status\": \"success\", \"task_id\": 15, \"message\": \"Created task 'Buy groceries' with ID 15\"}"
    }
  },
  {
    "id": "call_def456",
    "type": "function",
    "function": {
      "name": "complete_task",
      "arguments": "{\"user_id\": 42, \"task_id\": 3}",
      "result": "{\"status\": \"success\", \"message\": \"Marked task 3 as complete\"}"
    }
  }
]
```

**Field Descriptions**:
- **id**: OpenAI tool call ID (for tracking)
- **type**: Always "function" for Phase III
- **function.name**: MCP tool name (e.g., "add_task")
- **function.arguments**: JSON string of tool parameters
- **function.result**: JSON string of tool execution result (for debugging/audit)

**NULL vs Empty Array**:
- **NULL**: Assistant message with NO tool calls (pure text response)
- **[]**: Reserved for future use (empty array not used in Phase III)

---

## SQLModel Schema Definition (Python)

```python
# backend/app/models.py
from sqlmodel import Field, SQLModel, JSON, Column
from datetime import datetime
from typing import Optional

class ConversationMessage(SQLModel, table=True):
    """
    Conversation message model for AI chatbot.

    Stores user and assistant messages with tool execution history.
    Supports stateless chat architecture (all state in database).
    """
    __tablename__ = "conversation_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(index=True, nullable=False)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    role: str = Field(max_length=20, nullable=False)
    content: str = Field(nullable=False)
    tool_calls: Optional[list] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 42,
                "user_id": 5,
                "role": "user",
                "content": "Add buy groceries to my list",
                "tool_calls": None,
                "created_at": "2025-12-13T10:30:00Z",
                "updated_at": "2025-12-13T10:30:00Z"
            }
        }
```

---

## Migration Strategy

### Migration File (Alembic)

**File**: `backend/alembic/versions/004_add_conversation_messages.py`

```python
"""Add conversation_messages table for AI chatbot

Revision ID: 004_add_conversation_messages
Revises: 003_add_phase_ii_features
Create Date: 2025-12-13 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers
revision = '004_add_conversation_messages'
down_revision = '003_add_phase_ii_features'  # Replace with actual Phase II revision
branch_labels = None
depends_on = None


def upgrade():
    """Create conversation_messages table and indexes."""
    # Create table
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_role_valid')
    )

    # Create indexes (order matters for composite indexes)
    op.create_index(
        'idx_conversation_messages_conversation_id_created_at',
        'conversation_messages',
        ['conversation_id', sa.text('created_at DESC')],
        unique=False
    )
    op.create_index(
        'idx_conversation_messages_user_id_conversation_id',
        'conversation_messages',
        ['user_id', 'conversation_id'],
        unique=False
    )
    op.create_index(
        'idx_conversation_messages_user_id_created_at',
        'conversation_messages',
        ['user_id', sa.text('created_at DESC')],
        unique=False
    )


def downgrade():
    """Drop conversation_messages table and indexes."""
    op.drop_index('idx_conversation_messages_user_id_created_at', table_name='conversation_messages')
    op.drop_index('idx_conversation_messages_user_id_conversation_id', table_name='conversation_messages')
    op.drop_index('idx_conversation_messages_conversation_id_created_at', table_name='conversation_messages')
    op.drop_table('conversation_messages')
```

### Migration Execution

**Step 1: Generate Migration** (if using autogenerate)
```bash
cd backend
alembic revision --autogenerate -m "Add conversation_messages table for AI chatbot"
```

**Step 2: Review Migration File**
- Verify table schema matches data-model.md
- Verify indexes are created correctly
- Verify foreign key constraint and CASCADE delete

**Step 3: Apply Migration**
```bash
alembic upgrade head
```

**Step 4: Verify Schema**
```bash
psql $DATABASE_URL -c "\d conversation_messages"
```

**Expected Output**:
```
                                Table "public.conversation_messages"
     Column       |           Type           | Nullable |         Default
------------------+--------------------------+----------+---------------------------
 id               | integer                  | not null | generated by default as identity
 conversation_id  | integer                  | not null |
 user_id          | integer                  | not null |
 role             | character varying(20)    | not null |
 content          | text                     | not null |
 tool_calls       | jsonb                    |          |
 created_at       | timestamp with time zone | not null | now()
 updated_at       | timestamp with time zone | not null | now()
Indexes:
    "conversation_messages_pkey" PRIMARY KEY, btree (id)
    "idx_conversation_messages_conversation_id_created_at" btree (conversation_id, created_at DESC)
    "idx_conversation_messages_user_id_conversation_id" btree (user_id, conversation_id)
    "idx_conversation_messages_user_id_created_at" btree (user_id, created_at DESC)
Foreign-key constraints:
    "conversation_messages_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
Check constraints:
    "check_role_valid" CHECK (role::text = ANY (ARRAY['user'::text, 'assistant'::text, 'system'::text]))
```

### Rollback Strategy

**If migration fails or Phase III is cancelled**:

```bash
# Rollback to previous migration
alembic downgrade -1

# Verify table is dropped
psql $DATABASE_URL -c "\dt conversation_messages"
# Expected: "Did not find any relation named 'conversation_messages'"
```

**Data Loss**: Rolling back deletes all conversation history. **Not recommended in production.**

**Production Rollback**: Use blue/green deployment to rollback application code without dropping table.

---

## Backward Compatibility

### Phase II Schema (No Changes Required)

The `conversation_messages` table is **independent** from Phase II schema:
- No foreign keys TO Phase II tables (except `users`)
- No changes to existing Phase II tables (`tasks`, `users`, etc.)
- Phase II features continue working without modification

### Phase II → Phase III Upgrade Path

**Zero downtime migration**:
1. Apply migration (adds new table)
2. Deploy Phase III backend (new `/api/v1/chat` endpoint)
3. Deploy Phase III frontend (adds chat UI)
4. Phase II features continue working (tasks, auth, etc.)

**Rollback path**:
1. Rollback frontend (remove chat UI)
2. Rollback backend (remove chat endpoint)
3. Optionally rollback migration (drops table, loses conversation data)

---

## Data Retention and Cleanup

### Data Growth Estimation

**Per user**:
- Average 30 conversations/month
- Average 10 messages/conversation
- Average 200 characters/message
- **Total**: 30 × 10 × 200 = 60,000 characters = **60 KB/user/month**

**1,000 users**:
- 60 KB × 1,000 = **60 MB/month**
- 12 months = **720 MB/year**

**Conclusion**: Negligible storage impact (Neon free tier: 3 GB limit)

### Cleanup Strategy (Future Optimization)

**Phase III: No cleanup** (unlimited retention)

**Future Phase**: Implement conversation archival
- Archive conversations older than 90 days to cold storage (S3)
- Keep recent 90 days in PostgreSQL for fast access
- Restore from archive on user request

```sql
-- Future cleanup query (NOT implemented in Phase III)
DELETE FROM conversation_messages
WHERE created_at < NOW() - INTERVAL '90 days';
```

---

## Testing Strategy

### Unit Tests

```python
# backend/tests/test_models.py
import pytest
from backend.app.models import ConversationMessage
from datetime import datetime

def test_conversation_message_creation():
    """Test ConversationMessage model instantiation."""
    msg = ConversationMessage(
        conversation_id=42,
        user_id=5,
        role="user",
        content="Add buy groceries"
    )
    assert msg.conversation_id == 42
    assert msg.user_id == 5
    assert msg.role == "user"
    assert msg.content == "Add buy groceries"
    assert msg.tool_calls is None

def test_conversation_message_with_tool_calls():
    """Test ConversationMessage with tool execution history."""
    tool_calls = [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "add_task",
                "arguments": '{"user_id": 42, "title": "Buy groceries"}',
                "result": '{"status": "success", "task_id": 15}'
            }
        }
    ]
    msg = ConversationMessage(
        conversation_id=42,
        user_id=5,
        role="assistant",
        content="I've added 'Buy groceries' to your list!",
        tool_calls=tool_calls
    )
    assert msg.tool_calls is not None
    assert len(msg.tool_calls) == 1
    assert msg.tool_calls[0]["function"]["name"] == "add_task"
```

### Integration Tests

```python
# backend/tests/test_conversation_crud.py
import pytest
from backend.app.crud import create_conversation_message, load_conversation_history

def test_save_and_load_conversation(test_db, test_user):
    """Test full conversation persistence flow."""
    # Create conversation messages
    msg1 = create_conversation_message(
        conversation_id=1,
        user_id=test_user.id,
        role="user",
        content="Add buy groceries"
    )
    msg2 = create_conversation_message(
        conversation_id=1,
        user_id=test_user.id,
        role="assistant",
        content="I've added the task!",
        tool_calls=[{"id": "call_123", "type": "function", "function": {"name": "add_task"}}]
    )

    # Load conversation history
    messages = load_conversation_history(conversation_id=1, user_id=test_user.id)

    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["tool_calls"] is not None

def test_conversation_ownership_check(test_db, test_user, other_user):
    """Test that users can only access their own conversations."""
    # User 1 creates conversation
    create_conversation_message(
        conversation_id=1,
        user_id=test_user.id,
        role="user",
        content="My secret message"
    )

    # User 2 tries to access User 1's conversation
    messages = load_conversation_history(conversation_id=1, user_id=other_user.id)

    # Should return empty (ownership check failed)
    assert len(messages) == 0
```

---

## Summary

### Database Objects Created
- ✅ `conversation_messages` table (8 columns)
- ✅ 3 indexes for query optimization
- ✅ 1 foreign key constraint (users)
- ✅ 1 check constraint (role validation)
- ✅ SQLModel Python class

### Key Design Decisions
- **Stateless architecture**: All conversation state in database, zero server memory
- **Sliding window optimization**: Indexes support recent 20 messages query (<10ms)
- **Logical conversations**: No separate `conversations` table (simplified schema)
- **JSONB for tool_calls**: Flexible structure for tool execution history
- **Cascade delete**: Conversation messages deleted when user is deleted

### Ready For
- ✅ Alembic migration creation
- ✅ Backend CRUD implementation
- ✅ Chat endpoint integration
- ✅ Frontend conversation history UI

---

**Version**: 1.0.0
**Created**: 2025-12-13
**Status**: Phase 1 Design Complete

**Next**: Generate `contracts/chat-api.yaml` and `contracts/mcp-tools.yaml`
