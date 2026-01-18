# Implementation Plan: Phase III - AI-Powered Conversational Task Management

**Branch**: `004-ai-chatbot` | **Date**: 2025-12-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/004-ai-chatbot/spec.md`

## Summary

Phase III adds an AI-powered conversational interface to the Physical AI Todo application, enabling users to manage tasks through natural language. The implementation uses:
- **MCP (Model Context Protocol) SDK** to expose task operations as standardized tools
- **OpenAI Agents SDK** (GPT-4 Turbo) for natural language understanding and tool calling
- **Stateless chat architecture** storing all conversation state in PostgreSQL for horizontal scalability
- **Integration with Phase II features** (priorities, tags, subtasks, voice input)

The chatbot complements (not replaces) the existing web UI, providing a conversational alternative for users who prefer natural language interaction.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript (frontend Next.js 14)
**Primary Dependencies**: Official MCP SDK (Python), OpenAI SDK, FastAPI, SQLModel, React Query
**Storage**: Neon Serverless PostgreSQL (conversation_messages table, extends existing schema)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (desktop, tablet, mobile responsive)
**Project Type**: Web (backend + frontend)
**Performance Goals**:
- p95 chat response latency < 3 seconds (including AI processing)
- 100 concurrent chat sessions without degradation
- Conversation history load < 500ms for 100 messages
**Constraints**:
- OpenAI API rate limits (TPM/RPM - see research.md)
- Neon free tier connection pooling limits
- Stateless architecture (zero server-side memory)
**Scale/Scope**:
- Support 1000+ users with persistent conversation history
- Handle conversations with 100+ messages efficiently
- 6-language support (en, ur, ar, es, fr, de)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitution Validation Results

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Spec-Driven Development** | ✅ PASS | Spec created via `/sp.specify`, plan via `/sp.plan`, tasks will follow via `/sp.tasks` |
| **II. Phase-Correct Evolution** | ⚠️ REVIEW | Phase III starting while Phase II is 85% complete (5 features remaining) |
| **III. Authentication and Security First** | ✅ PASS | Inherits Phase II JWT authentication, all endpoints protected |
| **IV. Test-Driven Quality** | ✅ PASS | 80%+ coverage target maintained, tests defined in spec |
| **V. Modern UX and Design Standards** | ✅ PASS | Glassmorphism chat UI, responsive design, accessibility maintained |
| **VI. API-First Architecture** | ✅ PASS | Chat API contract defined, OpenAPI documentation via FastAPI |
| **VII. Database Design Excellence** | ✅ PASS | conversation_messages schema with proper indexes, migrations planned |
| **VIII. Multi-Language and Accessibility** | ✅ PASS | 6-language support via GPT-4 Turbo, RTL support inherited from Phase II |

### Complexity Tracking

**Violation**: Phase III starting before Phase II 100% complete

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Starting Phase III at 85% Phase II completion | Core Phase II functionality complete (auth, tasks, multi-language, advanced features). Remaining 5 features (keyboard shortcuts, undo/redo, export, templates, analytics) are independent enhancements that don't block AI chatbot development. | Waiting for 100% Phase II completion would delay critical AI chatbot feature by 2-3 weeks. Remaining Phase II features don't share dependencies with chatbot (no data model overlap, no API conflicts). Can complete Phase II features in parallel with Phase III Phase 0 research. |

**Decision**: Proceed with Phase III given:
1. All Phase II dependencies for chatbot are complete (auth, tasks CRUD, advanced features)
2. No data model conflicts (conversation_messages is independent table)
3. No API endpoint conflicts (chat uses new `/api/v1/chat` route)
4. Remaining Phase II features are UI enhancements, not architectural foundations

**Project Count Justification**:
- **Project 1**: Phase I console app (Python, in-memory)
- **Project 2**: Phase II web application (FastAPI backend + Next.js frontend)
- **Project 3**: Phase III AI chatbot (extends Project 2 with MCP + OpenAI integration)

Constitution allows ≤3 projects. Phase III is technically an extension of Phase II (same codebase, same tech stack), adding AI layer. Not a separate project but an architectural evolution.

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (COMPLETED via /sp.specify)
├── research.md          # Phase 0 output (/sp.plan command - THIS FILE WILL BE GENERATED)
├── data-model.md        # Phase 1 output (/sp.plan command - THIS FILE WILL BE GENERATED)
├── quickstart.md        # Phase 1 output (/sp.plan command - THIS FILE WILL BE GENERATED)
├── contracts/           # Phase 1 output (/sp.plan command - THIS DIRECTORY WILL BE GENERATED)
│   ├── chat-api.yaml    # OpenAPI 3.0 spec for chat endpoint
│   └── mcp-tools.yaml   # MCP tool schemas (add_task, list_tasks, etc.)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                  # FastAPI app (extend with chat router)
│   ├── models.py                # SQLModel schemas (add ConversationMessage model)
│   ├── crud.py                  # Database operations (add conversation CRUD)
│   ├── database.py              # Neon connection (no changes)
│   ├── auth/                    # Auth module (reuse existing)
│   ├── routes/
│   │   ├── tasks.py             # Existing task routes
│   │   └── chat.py              # NEW: Chat endpoint (/api/v1/chat)
│   ├── mcp/                     # NEW: MCP server implementation
│   │   ├── __init__.py
│   │   ├── server.py            # MCP server setup with Official SDK
│   │   ├── tools.py             # MCP tool definitions (add_task, list_tasks, etc.)
│   │   └── schemas.py           # MCP tool parameter schemas
│   └── chat/                    # NEW: AI chatbot logic
│       ├── __init__.py
│       ├── agent.py             # OpenAI Agents SDK integration
│       ├── prompts.py           # System prompts and persona
│       └── conversation.py      # Conversation history management
└── tests/
    ├── test_mcp_tools.py        # NEW: MCP tool tests
    ├── test_chat_api.py         # NEW: Chat endpoint tests
    └── test_conversation.py     # NEW: Conversation logic tests

frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx             # Main dashboard (add chat tab/sidebar)
│   └── chat/                    # NEW: Chat-specific routes (optional standalone page)
│       └── page.tsx             # Dedicated chat page
├── components/
│   ├── chat/                    # NEW: Chat UI components
│   │   ├── ChatInterface.tsx    # Main chat container
│   │   ├── MessageList.tsx      # Conversation messages display
│   │   ├── MessageItem.tsx      # Individual message (user/assistant)
│   │   ├── ChatInput.tsx        # Message input with send button
│   │   ├── ConversationSidebar.tsx # Conversation history list
│   │   ├── TypingIndicator.tsx  # "AI is typing..." animation
│   │   └── ToolCallDisplay.tsx  # Visual feedback for tool executions
│   └── [existing components]
├── contexts/
│   └── ChatContext.tsx          # NEW: Chat state management (active conversation, messages)
├── lib/
│   ├── api.ts                   # Extend with chatAPI functions
│   └── types.ts                 # Add chat types (Message, Conversation, ToolCall)
└── public/
    └── locales/                 # Extend with chat-specific translations
        ├── en/chat.json         # NEW: English chat strings
        ├── ur/chat.json         # NEW: Urdu chat strings
        ├── ar/chat.json         # NEW: Arabic chat strings
        ├── es/chat.json         # NEW: Spanish chat strings
        ├── fr/chat.json         # NEW: French chat strings
        └── de/chat.json         # NEW: German chat strings
```

**Structure Decision**: Extending Phase II web application structure with new backend modules (`mcp/`, `chat/`) and frontend chat components. Maintains separation of concerns:
- **MCP layer** (`backend/app/mcp/`): Stateless tools exposing task operations
- **Chat layer** (`backend/app/chat/`): AI agent orchestration and conversation management
- **API layer** (`backend/app/routes/chat.py`): HTTP endpoint for frontend
- **Frontend chat** (`frontend/components/chat/`): Reusable chat UI components

This structure allows chatbot to be:
1. **Integrated** into existing dashboard (tab/sidebar)
2. **Standalone** (dedicated `/chat` route)
3. **Decoupled** from existing task UI (can develop independently)

## Phase 0: Research & Technical Validation

### Research Objectives (See research.md for detailed findings)

Phase 0 addresses all **NEEDS CLARIFICATION** items from Technical Context and identifies architectural risks before implementation.

#### 1. OpenAI API Rate Limits & Retry Strategies
**Question**: What are the TPM/RPM limits for GPT-4 Turbo? How should we handle rate limit errors?

**Research Tasks**:
- Document OpenAI rate limits for GPT-4 Turbo (Tier 1, Tier 2, Tier 3)
- Design exponential backoff retry strategy
- Identify error codes (429, 503) and handling
- Estimate cost per conversation (tokens per message)

**Deliverable**: Section in `research.md` with:
- Rate limit table (TPM, RPM, daily caps)
- Retry pseudocode
- Cost analysis ($/1000 conversations estimate)

#### 2. Neon DB Connection Pooling (Free Tier Limits)
**Question**: How many concurrent connections does Neon free tier support? What happens on connection exhaustion?

**Research Tasks**:
- Document Neon free tier limits (max connections, connection timeout)
- Research SQLModel/SQLAlchemy connection pooling best practices
- Identify connection pool configuration (`pool_size`, `max_overflow`, `pool_timeout`)
- Design connection error handling strategy

**Deliverable**: Section in `research.md` with:
- Neon free tier connection limits
- Recommended pool configuration
- Connection error recovery strategy

#### 3. ChatKit vs Custom Glassmorphism UI Decision
**Question**: Should we use OpenAI ChatKit or build custom chat UI matching Phase II glassmorphism design?

**Research Tasks**:
- Evaluate OpenAI ChatKit features (out-of-the-box functionality, customization limits)
- Compare with custom React components (framer-motion, Tailwind CSS)
- Assess design consistency with existing Phase II UI
- Estimate implementation time for both approaches

**Deliverable**: Section in `research.md` with:
- ChatKit pros/cons table
- Custom UI pros/cons table
- **Recommendation** with justification
- Mockup/wireframe (optional)

#### 4. MCP SDK + FastAPI Integration Pattern
**Question**: How does Official MCP SDK integrate with FastAPI? Is there a reference implementation?

**Research Tasks**:
- Review Official MCP SDK documentation (Python)
- Identify integration pattern (FastAPI dependency injection, middleware, or separate server)
- Find reference implementations or examples
- Test basic MCP server setup with FastAPI

**Deliverable**: Section in `research.md` with:
- MCP SDK architecture diagram
- FastAPI integration pattern (code snippet)
- Tool registration example
- Known limitations or gotchas

#### 5. OpenAI Agents SDK Tool Calling
**Question**: How does OpenAI Agents SDK handle function calling? What's the request/response format?

**Research Tasks**:
- Review OpenAI function calling documentation
- Understand tool schema format (JSON Schema)
- Identify how to map MCP tools to OpenAI function calling
- Test iterative tool calling (tool result → new message → new tool call)

**Deliverable**: Section in `research.md` with:
- OpenAI function calling flow diagram
- Tool schema example
- Request/response JSON examples
- Multi-step tool chaining example

#### 6. Stateless Chat Architecture Best Practices
**Question**: What are the best practices for stateless chat with database-backed history?

**Research Tasks**:
- Research conversation context window management (how many messages to send to AI)
- Identify message array construction strategy (recent N messages vs full history)
- Design conversation pruning strategy (performance vs context tradeoff)
- Study scaling patterns (connection pooling, caching, async processing)

**Deliverable**: Section in `research.md` with:
- Conversation context strategy (recommended message count)
- Performance benchmarks (100 messages vs 1000 messages latency)
- Scaling recommendations
- Caching strategy (if applicable)

### Phase 0 Acceptance Criteria
- ✅ All 6 research questions answered in `research.md`
- ✅ Technical risks identified with mitigation strategies
- ✅ Architecture decisions documented (ChatKit vs custom, MCP integration pattern)
- ✅ No unresolved NEEDS CLARIFICATION items remaining
- ✅ Research findings inform Phase 1 design (data model, contracts, quickstart)

### Phase 0 Timeline
**Estimated Duration**: 2-3 days (research-heavy, no coding)

## Phase 1: Design & Planning Artifacts

### Phase 1 Objectives

Create comprehensive design documents that serve as implementation blueprints. All artifacts must be **spec-compliant** and **constitution-aligned**.

#### 1. Data Model Definition (`data-model.md`)

**Purpose**: Define PostgreSQL schema for conversation persistence

**Content Requirements**:
- **ConversationMessage Table Schema**:
  - Primary key, foreign keys, indexes
  - Column definitions with types, constraints, defaults
  - JSON fields (tool_calls) with example structure
- **Relationships**:
  - Link to existing User table
  - Logical grouping by conversation_id
- **Indexes**:
  - Performance optimization for conversation history queries
  - User-specific queries
  - Timestamp-based sorting
- **Migration Strategy**:
  - Alembic migration outline
  - Backward compatibility with Phase II schema
  - Rollback strategy

**Deliverable**: `specs/004-ai-chatbot/data-model.md` (≈100-150 lines)

#### 2. API Contracts (`contracts/`)

**Purpose**: Define HTTP and MCP interfaces for all chatbot interactions

**Content Requirements**:

**File 1: `contracts/chat-api.yaml` (OpenAPI 3.0)**
- **POST /api/v1/chat** endpoint
  - Request schema: `conversation_id` (optional int), `message` (required string)
  - Response schema: `conversation_id` (int), `response` (string), `tool_calls` (array)
  - Authentication: JWT from Phase II (`Authorization: Bearer <token>` or cookie)
  - Error responses: 400 (bad request), 401 (unauthorized), 429 (rate limit), 500 (server error)
  - Example request/response JSON

**File 2: `contracts/mcp-tools.yaml` (MCP Tool Schemas)**
- Tool definitions for each task operation:
  - **add_task**: parameters (user_id, title, description, priority, tags), return type, docstring
  - **list_tasks**: parameters (user_id, status, priority, tags), return type, docstring
  - **complete_task**: parameters (user_id, task_id), return type, docstring
  - **delete_task**: parameters (user_id, task_id), return type, docstring
  - **update_task**: parameters (user_id, task_id, title, description, priority, tags), return type, docstring
  - **set_priority**: parameters (user_id, task_id, priority), return type, docstring
  - **manage_tags**: parameters (user_id, task_id, tags_to_add, tags_to_remove), return type, docstring
  - **manage_subtasks**: parameters (user_id, parent_task_id, subtasks), return type, docstring
  - **search_tasks**: parameters (user_id, query), return type, docstring
  - **filter_tasks**: parameters (user_id, filters), return type, docstring
- JSON Schema format for each tool
- Error handling specifications

**Deliverable**:
- `specs/004-ai-chatbot/contracts/chat-api.yaml` (≈150-200 lines)
- `specs/004-ai-chatbot/contracts/mcp-tools.yaml` (≈300-400 lines)

#### 3. Quickstart Guide (`quickstart.md`)

**Purpose**: Step-by-step implementation and testing guide for developers

**Content Requirements**:
- **Prerequisites Check**:
  - Python 3.13+, Node.js 18+, PostgreSQL (Neon)
  - OpenAI API key with GPT-4 Turbo access
  - Phase II completed (auth, tasks, database)
- **Installation**:
  - Install MCP SDK: `pip install mcp-sdk`
  - Install OpenAI SDK: `pip install openai`
  - Environment variables (.env updates)
- **Database Migration**:
  - Create conversation_messages table
  - Run Alembic migration
  - Verify schema with psql
- **MCP Server Setup**:
  - Implement tools in `backend/app/mcp/tools.py`
  - Register tools with MCP server
  - Test tool execution (unit tests)
- **Chat Endpoint Implementation**:
  - Create `/api/v1/chat` route
  - Integrate MCP tools with OpenAI agent
  - Store conversation history
  - Test endpoint with curl/Postman
- **Frontend Integration**:
  - Create chat UI components
  - Integrate with backend API
  - Add to dashboard (tab or sidebar)
  - Test conversation flow
- **Testing Commands**:
  - Backend tests: `pytest backend/tests/test_chat_api.py -v`
  - Frontend tests: `npm test -- chat`
  - E2E test: Manual conversation flow
- **Deployment Checklist**:
  - Environment variables set
  - Database migrations applied
  - OpenAI API key validated
  - Rate limiting configured
  - Monitoring enabled

**Deliverable**: `specs/004-ai-chatbot/quickstart.md` (≈200-250 lines)

#### 4. Agent Context Update

**Purpose**: Register Phase III artifacts in Claude Code's context for optimal code generation

**Action**: Run `.specify/scripts/bash/update-agent-context.sh claude`

**Effect**: Updates `.claude/` configuration with:
- New file paths (`backend/app/mcp/`, `frontend/components/chat/`)
- API contracts for tool calling
- Data model schema
- Testing requirements

**Deliverable**: Updated `.claude/context.json` or equivalent

### Phase 1 Acceptance Criteria
- ✅ `data-model.md` defines complete schema with migrations
- ✅ `contracts/chat-api.yaml` is valid OpenAPI 3.0 spec
- ✅ `contracts/mcp-tools.yaml` defines all 10 MCP tools
- ✅ `quickstart.md` provides clear step-by-step implementation guide
- ✅ Agent context updated with new paths and schemas
- ✅ All artifacts reviewed and approved by user
- ✅ No contradictions with Phase II design
- ✅ All spec requirements (75 FRs) traceable to design artifacts

### Phase 1 Timeline
**Estimated Duration**: 3-4 days (design and documentation)

## Phase 2: Task Breakdown

**Note**: Phase 2 (task generation) is handled by `/sp.tasks` command, NOT by `/sp.plan`.

After Phase 1 completion, run:
```bash
/sp.tasks
```

This will generate `specs/004-ai-chatbot/tasks.md` with:
- ≤30 minute granular tasks
- Test cases for each task
- Dependencies between tasks
- Acceptance criteria per task
- Estimated effort

**Expected Task Categories**:
1. Database setup (migrations, models)
2. MCP tool implementation (10 tools)
3. OpenAI agent integration
4. Chat endpoint (stateless architecture)
5. Conversation history management
6. Frontend chat UI (6-8 components)
7. Multi-language integration
8. Testing (unit, integration, E2E)
9. Documentation and deployment

**Estimated Total Tasks**: 40-60 tasks (3-4 weeks implementation)

## Implementation Strategy

### Development Approach

**Incremental Delivery**:
1. **Milestone 1 (Week 1)**: MCP server + basic tools (add_task, list_tasks, complete_task)
2. **Milestone 2 (Week 2)**: OpenAI agent + chat endpoint + stateless architecture
3. **Milestone 3 (Week 3)**: Frontend chat UI + conversation history
4. **Milestone 4 (Week 4)**: Advanced tools (priorities, tags, subtasks) + multi-language + polish

**Testing Strategy**:
- TDD for MCP tools (write tests first, then implement)
- Integration tests for chat endpoint (mock OpenAI API)
- E2E tests for full conversation flows
- Performance tests for conversation history loading

**Risk Mitigation**:
- **OpenAI API costs**: Set daily budget alerts, implement token counting
- **Rate limiting**: Implement retry logic early, test with burst traffic
- **Connection pooling**: Monitor Neon connections, add graceful degradation
- **Context window limits**: Design conversation pruning strategy (recent N messages)

### Architecture Principles

1. **Stateless Everywhere**: No server-side memory, all state in PostgreSQL
2. **Fail-Safe Degradation**: If AI fails, return helpful error message
3. **User Ownership**: All tools validate user_id before operations
4. **Idempotency**: Same message to same conversation produces same result (deterministic where possible)
5. **Observability**: Log all AI requests, tool executions, errors

## Architectural Decisions Requiring ADR

After `/sp.plan` completion, the following architectural decisions may warrant ADRs (pending user consent):

### Potential ADR 1: AI Framework Selection
**Decision**: OpenAI Agents SDK vs LangChain vs Custom Implementation

**Significance Test**:
- ✅ **Impact**: Long-term AI integration strategy affects extensibility
- ✅ **Alternatives**: 3 viable options with different tradeoffs
- ✅ **Scope**: Cross-cutting, influences future AI features

**Suggested Command**: `/sp.adr ai-framework-selection`

**Key Tradeoffs**:
- OpenAI Agents SDK: Simpler, vendor lock-in, best OpenAI integration
- LangChain: Framework-agnostic, complex, more abstractions
- Custom: Maximum control, more maintenance, reinventing wheel

### Potential ADR 2: Chat UI Implementation (ChatKit vs Custom)
**Decision**: OpenAI ChatKit vs Custom React Components

**Significance Test**:
- ✅ **Impact**: Affects UI consistency with Phase II, customization ability
- ✅ **Alternatives**: 2 viable options
- ✅ **Scope**: Influences frontend architecture

**Suggested Command**: `/sp.adr chat-ui-implementation`

**Key Tradeoffs**:
- ChatKit: Faster, less control over design, potential style conflicts
- Custom: Full design control, more effort, better Phase II integration

### Potential ADR 3: Conversation Context Management
**Decision**: Full history vs Sliding window vs Token-based pruning

**Significance Test**:
- ✅ **Impact**: Affects performance, AI context quality, scalability
- ✅ **Alternatives**: 3+ strategies with different performance characteristics
- ✅ **Scope**: Cross-cutting, affects database queries and AI requests

**Suggested Command**: `/sp.adr conversation-context-strategy`

**Key Tradeoffs**:
- Full history: Best context, expensive, slow for long conversations
- Sliding window (recent N): Balanced, loses old context
- Token-based: Optimal cost, complex implementation

**User Decision Required**: After research.md completion, review findings and approve ADR creation for above decisions.

## Dependencies

### External Dependencies (New in Phase III)
- **Official MCP SDK** (Python) - Latest stable version
- **OpenAI SDK** (Python) - `openai>=1.0.0`
- **GPT-4 Turbo Model** - OpenAI API access with sufficient quota

### Internal Dependencies (From Phase II)
- ✅ Authentication system (JWT, user sessions)
- ✅ Task CRUD operations (backend/app/routes/tasks.py, backend/app/crud.py)
- ✅ User model (backend/app/models.py)
- ✅ Database connection (backend/app/database.py, Neon PostgreSQL)
- ✅ Frontend i18n system (frontend/contexts/I18nContext.tsx)
- ⏳ Voice input (Phase II bonus, if completed - for voice chatbot integration)

### Phase II Completion Status
**Current**: 85% complete (30/35 features done)

**Remaining Phase II Features** (can proceed in parallel):
- Keyboard shortcuts
- Undo/Redo system
- Export/Import (CSV/JSON)
- Task templates
- Analytics dashboard

**Impact on Phase III**: None. All chatbot dependencies are complete.

## Quality Gates

### Phase 0 (Research) Gates
- [ ] All 6 research questions answered
- [ ] Technical risks documented with mitigations
- [ ] Architecture decisions ready for ADR (if applicable)

### Phase 1 (Design) Gates
- [ ] data-model.md approved (schema, indexes, migrations)
- [ ] contracts/chat-api.yaml valid OpenAPI 3.0
- [ ] contracts/mcp-tools.yaml defines all 10 tools
- [ ] quickstart.md provides clear implementation path
- [ ] Agent context updated
- [ ] No spec contradictions

### Phase 2 (Tasks) Gates
- [ ] tasks.md generated via `/sp.tasks`
- [ ] All 75 FRs traceable to tasks
- [ ] Tasks ≤30 minutes granularity
- [ ] Test cases defined per task
- [ ] User approval

### Phase 3 (Implementation) Gates
- [ ] 80%+ test coverage (pytest + Jest)
- [ ] All tests passing
- [ ] Chat endpoint functional
- [ ] MCP tools working (10 tools)
- [ ] Conversation persistence verified
- [ ] Multi-language tested (6 languages)
- [ ] Performance benchmarks met (p95 < 3s)

### Phase 4 (Deployment) Gates
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] OpenAI API key validated
- [ ] Rate limiting tested
- [ ] Monitoring/logging enabled
- [ ] PHR created

## Next Steps

### Immediate Actions (User Approval Required)

1. **Review this plan.md** - Confirm approach, structure, and timeline
2. **Approve Phase 0 research** - Begin research.md generation
3. **Decide on ADRs** - Confirm which architectural decisions need formal documentation

### After Approval

**Phase 0 Tasks** (Agent execution):
1. Generate `research.md` addressing 6 research questions
2. Identify architectural risks and mitigations
3. Make recommendations (ChatKit vs custom, context strategy, etc.)
4. Get user approval on research findings

**Phase 1 Tasks** (Agent execution):
1. Generate `data-model.md` with complete schema
2. Generate `contracts/chat-api.yaml` (OpenAPI 3.0)
3. Generate `contracts/mcp-tools.yaml` (10 MCP tools)
4. Generate `quickstart.md` (step-by-step guide)
5. Run `update-agent-context.sh claude`
6. Get user approval on all artifacts

**Phase 2 Tasks** (User-triggered):
1. User runs `/sp.tasks`
2. Agent generates `tasks.md` with granular tasks
3. User reviews and approves tasks
4. Implementation begins via `/sp.implement`

## Success Metrics

### Feature Completeness
- All 75 FRs implemented and tested
- All 7 user stories validated
- 10 MCP tools functional
- 6 languages supported

### Quality Metrics
- 80%+ test coverage
- p95 chat latency < 3 seconds
- 100 concurrent users supported
- Zero authentication bypasses
- Zero SQL injection vulnerabilities

### Documentation Completeness
- research.md (Phase 0)
- data-model.md (Phase 1)
- contracts/ (Phase 1)
- quickstart.md (Phase 1)
- tasks.md (Phase 2)
- ADRs (if applicable)
- PHR created

---

**Version**: 1.0.0
**Created**: 2025-12-13
**Status**: PENDING USER APPROVAL

**Ready for**: Phase 0 research execution
