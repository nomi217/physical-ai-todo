---
description: "Task breakdown for Phase III AI-Powered Conversational Task Management"
---

# Tasks: Phase III - AI Chatbot

**Input**: Design documents from `/specs/004-ai-chatbot/`
**Prerequisites**: plan.md, spec.md (7 user stories), research.md, data-model.md, contracts/

**Tests**: 80%+ coverage required (pytest backend, Jest frontend)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/`, `frontend/components/`, `frontend/app/`
- **Database**: Neon PostgreSQL (migrations in `backend/alembic/`)

---

## Phase 1: Setup & Environment (6-8 tasks)

**Purpose**: Install dependencies and create project structure for AI chatbot

- [ ] T001 [P] Install MCP SDK in backend: `pip install mcp-sdk` and add to backend/requirements.txt
- [ ] T002 [P] Install OpenAI SDK in backend: `pip install openai` and add to backend/requirements.txt
- [ ] T003 [P] Create backend/app/mcp/ directory with __init__.py
- [ ] T004 [P] Create backend/app/chat/ directory with __init__.py
- [ ] T005 [P] Create frontend/components/chat/ directory
- [ ] T006 Add OPENAI_API_KEY to .env file and update .env.example with documentation
- [ ] T007 Add OPENAI_MODEL=gpt-4-turbo to .env file (configurable model selection)
- [ ] T008 Verify environment setup: run `python -c "import mcp; import openai; print('Dependencies OK')"` in backend

**Checkpoint**: Dependencies installed, directory structure created

---

## Phase 2: Foundational (Database & Models) (4-6 tasks)

**Purpose**: Core database infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create Alembic migration for conversation_messages table in backend/alembic/versions/[timestamp]_add_conversation_messages.py
- [X] T010 Run Alembic migration: `alembic upgrade head` and verify table exists in Neon PostgreSQL
- [X] T011 Create ConversationMessage SQLModel class in backend/app/models.py with fields: id, conversation_id, user_id, role, content, tool_calls, created_at
- [X] T012 Add indexes to conversation_messages table for conversation_id, user_id, created_at (in migration)
- [X] T013 Create conversation CRUD operations in backend/app/crud.py: create_message, get_conversation_history, get_user_conversations
- [X] T014 Test conversation persistence with pytest in backend/tests/test_conversation_persistence.py

**Checkpoint**: Foundation ready - conversation database schema complete, all user story implementation can now begin

---

## Phase 3: US1 - Natural Language Task Management (12-15 tasks)

**Goal**: Basic chatbot that understands task commands (add, list, update, delete, complete)

**Independent Test**: Can create, list, update, complete, and delete tasks using natural language commands. AI understands common task management phrases and executes the correct operations.

### MCP Tools Implementation (Backend)

- [X] T015 [P] [US1] Create MCP tool schema for add_task in backend/app/mcp/schemas.py with parameters: user_id, title, description
- [X] T016 [P] [US1] Create MCP tool schema for list_tasks in backend/app/mcp/schemas.py with parameters: user_id, status (all/pending/completed)
- [X] T017 [P] [US1] Create MCP tool schema for complete_task in backend/app/mcp/schemas.py with parameters: user_id, task_id
- [X] T018 [P] [US1] Create MCP tool schema for delete_task in backend/app/mcp/schemas.py with parameters: user_id, task_id
- [X] T019 [P] [US1] Create MCP tool schema for update_task in backend/app/mcp/schemas.py with parameters: user_id, task_id, title, description
- [X] T020 [US1] Implement add_task MCP tool function in backend/app/mcp/tools.py calling crud.create_task
- [X] T021 [US1] Implement list_tasks MCP tool function in backend/app/mcp/tools.py calling crud.get_tasks with filters
- [X] T022 [US1] Implement complete_task MCP tool function in backend/app/mcp/tools.py calling crud.update_task(is_completed=True)
- [X] T023 [US1] Implement delete_task MCP tool function in backend/app/mcp/tools.py calling crud.delete_task
- [X] T024 [US1] Implement update_task MCP tool function in backend/app/mcp/tools.py calling crud.update_task
- [X] T025 [US1] Initialize MCP server in backend/app/mcp/server.py and register all 5 tools

### AI Agent Integration

- [X] T026 [US1] Create system prompt for task management assistant in backend/app/chat/prompts.py defining personality and capabilities
- [X] T027 [US1] Implement OpenAI agent initialization in backend/app/chat/agent.py with GPT-4 Turbo model and function calling
- [X] T028 [US1] Implement tool execution handler in backend/app/chat/agent.py mapping OpenAI function calls to MCP tools
- [X] T029 [US1] Implement conversation context builder in backend/app/chat/conversation.py fetching last 20 messages from database

### Chat Endpoint

- [X] T030 [US1] Create POST /api/v1/chat endpoint in backend/app/routes/chat.py accepting conversation_id (optional) and message
- [X] T031 [US1] Implement stateless conversation handling: fetch history, save user message, execute AI agent, save assistant response
- [X] T032 [US1] Add JWT authentication to chat endpoint using existing auth middleware from Phase II
- [X] T033 [US1] Register chat router in backend/app/main.py with /api/v1 prefix
- [X] T034 [US1] Add request validation and error handling for chat endpoint (400, 401, 429, 500 responses)

### Backend Tests

- [X] T035 [P] [US1] Test add_task MCP tool in backend/tests/test_mcp_tools.py
- [X] T036 [P] [US1] Test list_tasks MCP tool in backend/tests/test_mcp_tools.py
- [X] T037 [P] [US1] Test complete_task MCP tool in backend/tests/test_mcp_tools.py
- [X] T038 [P] [US1] Test delete_task MCP tool in backend/tests/test_mcp_tools.py
- [X] T039 [P] [US1] Test update_task MCP tool in backend/tests/test_mcp_tools.py
- [ ] T040 [US1] Test POST /api/v1/chat endpoint for task creation flow in backend/tests/test_chat_api.py
- [ ] T041 [US1] Test chat endpoint authentication (401 unauthorized) in backend/tests/test_chat_api.py
- [ ] T042 [US1] Test chat endpoint tool execution and response format in backend/tests/test_chat_api.py

### Frontend Chat UI

- [ ] T043 [P] [US1] Create Message type in frontend/lib/types.ts with fields: id, role, content, tool_calls, timestamp
- [ ] T044 [P] [US1] Create Conversation type in frontend/lib/types.ts with fields: id, messages, created_at
- [ ] T045 [US1] Create chat API client functions in frontend/lib/api.ts: sendMessage(conversationId, message)
- [ ] T046 [US1] Create ChatContext in frontend/contexts/ChatContext.tsx for managing active conversation and messages
- [ ] T047 [US1] Create MessageItem component in frontend/components/chat/MessageItem.tsx for displaying user/assistant messages
- [ ] T048 [US1] Create MessageList component in frontend/components/chat/MessageList.tsx with auto-scroll and timestamps
- [ ] T049 [US1] Create MessageInput component in frontend/components/chat/MessageInput.tsx with send button and enter-to-send
- [ ] T050 [US1] Create ChatInterface component in frontend/components/chat/ChatInterface.tsx combining MessageList and MessageInput
- [ ] T051 [US1] Create chat page in frontend/app/chat/page.tsx with ChatInterface and ChatContext provider
- [ ] T052 [US1] Add chat route to navigation in frontend/components/layout/Navigation.tsx

### Frontend Tests

- [ ] T053 [P] [US1] Test MessageItem component rendering in frontend/__tests__/components/chat/MessageItem.test.tsx
- [ ] T054 [P] [US1] Test MessageList component with multiple messages in frontend/__tests__/components/chat/MessageList.test.tsx
- [ ] T055 [P] [US1] Test MessageInput component send functionality in frontend/__tests__/components/chat/MessageInput.test.tsx
- [ ] T056 [US1] Test ChatInterface integration (send message, receive response) in frontend/__tests__/components/chat/ChatInterface.test.tsx

**Checkpoint**: User Story 1 complete - can create, list, update, delete, complete tasks via natural language

---

## Phase 4: US2 - Stateless Conversation Persistence (6-8 tasks)

**Goal**: Conversation history saves and resumes across browser refreshes and server restarts

**Independent Test**: Can start a conversation, close the browser, reopen, and see the full conversation history. Server can restart without losing conversation state because everything is in the database.

- [ ] T057 [US2] Implement conversation history loading with sliding window (last 20 messages) in backend/app/chat/conversation.py
- [ ] T058 [US2] Implement automatic conversation ID creation for new chats in backend/app/routes/chat.py when conversation_id is null
- [ ] T059 [US2] Add get_user_conversations endpoint GET /api/v1/chat/conversations in backend/app/routes/chat.py listing all user conversations
- [ ] T060 [US2] Create ConversationSidebar component in frontend/components/chat/ConversationSidebar.tsx showing conversation list
- [ ] T061 [US2] Implement conversation switching in frontend/contexts/ChatContext.tsx loading history when conversation selected
- [ ] T062 [US2] Add "New Chat" button to ConversationSidebar creating new conversation
- [ ] T063 [US2] Test conversation persistence across browser refresh in frontend (manual validation)
- [ ] T064 [US2] Test conversation resumption after server restart in backend/tests/test_conversation_persistence.py

**Checkpoint**: User Story 2 complete - conversations persist across sessions and server restarts

---

## Phase 5: US3 - Intelligent Tool Chaining (4-6 tasks)

**Goal**: AI handles multi-step requests like "Delete all completed tasks" by chaining multiple tool calls

**Independent Test**: Can ask complex questions like "Delete all my completed tasks" or "Show me high-priority tasks and mark the oldest one as done" and the AI chains multiple tool calls correctly.

- [ ] T065 [US3] Enhance system prompt in backend/app/chat/prompts.py with multi-step reasoning instructions and examples
- [ ] T066 [US3] Implement iterative tool calling in backend/app/chat/agent.py allowing AI to call tools based on previous results
- [ ] T067 [US3] Add search_tasks MCP tool in backend/app/mcp/tools.py for finding tasks by text content
- [ ] T068 [US3] Test multi-step queries in backend/tests/test_chat_api.py: "Delete all completed tasks", "Show high-priority and mark first done"
- [ ] T069 [US3] Create ToolCallDisplay component in frontend/components/chat/ToolCallDisplay.tsx showing visual feedback for tool executions
- [ ] T070 [US3] Integrate ToolCallDisplay into MessageItem component showing what tools AI used

**Checkpoint**: User Story 3 complete - AI successfully chains tools for complex requests

---

## Phase 6: US4 - Advanced Phase II Integration (8-10 tasks)

**Goal**: Priorities, tags, subtasks accessible via chat commands

**Independent Test**: Can set task priorities, add tags, create subtasks, and manage attachments all through natural language in the chat.

- [ ] T071 [P] [US4] Create set_priority MCP tool schema in backend/app/mcp/schemas.py with parameters: user_id, task_id, priority (high/medium/low)
- [ ] T072 [P] [US4] Create manage_tags MCP tool schema in backend/app/mcp/schemas.py with parameters: user_id, task_id, tags_to_add, tags_to_remove
- [ ] T073 [P] [US4] Create manage_subtasks MCP tool schema in backend/app/mcp/schemas.py with parameters: user_id, parent_task_id, subtasks (array of titles)
- [ ] T074 [US4] Implement set_priority MCP tool function in backend/app/mcp/tools.py calling crud.update_task(priority=...)
- [ ] T075 [US4] Implement manage_tags MCP tool function in backend/app/mcp/tools.py calling crud.add_tags and crud.remove_tags
- [ ] T076 [US4] Implement manage_subtasks MCP tool function in backend/app/mcp/tools.py calling crud.create_subtask for each subtask
- [ ] T077 [US4] Update system prompt in backend/app/chat/prompts.py with Phase II feature documentation (priorities, tags, subtasks)
- [ ] T078 [US4] Test priority setting via chat: "Add high-priority task to prepare presentation" in backend/tests/test_chat_api.py
- [ ] T079 [US4] Test tag management via chat: "Tag all work tasks as urgent" in backend/tests/test_chat_api.py
- [ ] T080 [US4] Test subtask creation via chat: "Add subtasks to task 5: research, create slides, practice" in backend/tests/test_chat_api.py
- [ ] T081 [US4] Create filter_tasks MCP tool in backend/app/mcp/tools.py for filtering by priority, tags, status

**Checkpoint**: User Story 4 complete - all Phase II features accessible via chat

---

## Phase 7: US5 - Multi-Language Support (6-8 tasks) [BONUS P3]

**Goal**: 6 languages work in chat (English, Urdu, Arabic, Spanish, French, German)

**Independent Test**: Can conduct entire conversations in any of the 6 supported languages. AI understands commands and responds in the same language consistently.

- [ ] T082 [P] [US5] Create translation file frontend/public/locales/en/chat.json with English chat UI strings
- [ ] T083 [P] [US5] Create translation file frontend/public/locales/ur/chat.json with Urdu chat UI strings
- [ ] T084 [P] [US5] Create translation file frontend/public/locales/ar/chat.json with Arabic chat UI strings
- [ ] T085 [P] [US5] Create translation file frontend/public/locales/es/chat.json with Spanish chat UI strings
- [ ] T086 [P] [US5] Create translation file frontend/public/locales/fr/chat.json with French chat UI strings
- [ ] T087 [P] [US5] Create translation file frontend/public/locales/de/chat.json with German chat UI strings
- [ ] T088 [US5] Update system prompt in backend/app/chat/prompts.py with multi-language instructions: detect language, respond in same language
- [ ] T089 [US5] Test multi-language commands in backend/tests/test_chat_api.py: English, Urdu, Arabic, Spanish, French, German
- [ ] T090 [US5] Test RTL support in frontend for Arabic and Urdu messages (manual validation)

**Checkpoint**: User Story 5 complete - 6 languages supported in chat

---

## Phase 8: US6 - Conversation Context & Memory (4-6 tasks)

**Goal**: AI remembers context from earlier in conversation

**Independent Test**: Can reference tasks from previous messages without repeating IDs. AI maintains context across multiple exchanges within a conversation.

- [ ] T091 [US6] Implement context window management in backend/app/chat/conversation.py ensuring last 20 messages sent to AI
- [ ] T092 [US6] Add conversation summary tracking (optional) for very long conversations (>100 messages)
- [ ] T093 [US6] Enhance system prompt in backend/app/chat/prompts.py with context retention instructions and anaphora resolution
- [ ] T094 [US6] Test context retention: "Mark that task as done" after "Show my tasks" in backend/tests/test_chat_api.py
- [ ] T095 [US6] Test multi-turn context: "Actually, add a description to that one" after task creation in backend/tests/test_chat_api.py

**Checkpoint**: User Story 6 complete - AI remembers conversation context

---

## Phase 9: US7 - Error Handling & Helpful Responses (6-8 tasks)

**Goal**: Graceful failures with clear, conversational error messages

**Independent Test**: System gracefully handles invalid task IDs, ambiguous commands, network errors, and edge cases with helpful, conversational error messages.

- [ ] T096 [US7] Implement retry logic for OpenAI rate limits (429 errors) with exponential backoff in backend/app/chat/agent.py
- [ ] T097 [US7] Add error handling for invalid task IDs in backend/app/mcp/tools.py returning conversational error messages
- [ ] T098 [US7] Add error handling for ambiguous requests in backend/app/chat/prompts.py with clarification question templates
- [ ] T099 [US7] Add validation to chat endpoint in backend/app/routes/chat.py for empty messages, message length limits
- [ ] T100 [US7] Test invalid task ID handling: "Delete task 999" returns helpful message in backend/tests/test_chat_api.py
- [ ] T101 [US7] Test ambiguous request handling: "Mark it as done" without context asks for clarification in backend/tests/test_chat_api.py
- [ ] T102 [US7] Test network error handling: mock OpenAI API failure returns user-friendly message in backend/tests/test_chat_api.py
- [ ] T103 [US7] Test edge cases: empty message, extremely long message (>10,000 chars), rapid-fire messages in backend/tests/test_chat_api.py

**Checkpoint**: User Story 7 complete - robust error handling in place

---

## Phase 10: Polish & Deployment (8-10 tasks)

**Purpose**: Final touches, integration tests, performance optimization, documentation

- [ ] T104 [P] Create TypingIndicator component in frontend/components/chat/TypingIndicator.tsx with animation
- [ ] T105 [P] Add chat link to dashboard navigation in frontend/app/dashboard/page.tsx
- [ ] T106 [P] Add conversation timestamps to ConversationSidebar showing last message time
- [ ] T107 [P] Add message timestamps to MessageItem component showing exact send time
- [ ] T108 Create integration test for full conversation flow in backend/tests/test_integration_chat.py: create task → list → update → complete → delete
- [ ] T109 Create performance test for 100 concurrent chat sessions in backend/tests/test_performance_chat.py
- [ ] T110 Create performance test for conversation history loading (100 messages) in backend/tests/test_performance_chat.py
- [ ] T111 Add rate limiting to chat endpoint in backend/app/routes/chat.py (10 requests per minute per user)
- [ ] T112 Add logging for all AI requests, tool executions, and errors in backend/app/chat/agent.py
- [ ] T113 Create deployment checklist in specs/004-ai-chatbot/DEPLOYMENT.md with environment variables, migrations, monitoring
- [ ] T114 Update project README.md with Phase III chatbot documentation and usage examples
- [ ] T115 Run full test suite and ensure 80%+ coverage: `pytest backend/tests/ --cov=backend/app --cov-report=html`

**Checkpoint**: All tasks complete - ready for deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US6 → US7 → US5)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US2 (P1)**: Can start after US1 - Requires conversation storage from US1
- **US3 (P2)**: Can start after US1 - Requires basic tools from US1
- **US4 (P2)**: Can start after US1 - Extends tools from US1
- **US6 (P2)**: Can start after US1 - Requires conversation history from US1
- **US7 (P2)**: Can start after US1 - Adds error handling to US1
- **US5 (P3 Bonus)**: Can start after US1 - Independent multi-language feature

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- MCP tool schemas before tool implementations
- MCP tools before AI agent integration
- Backend API before frontend components
- Core components before integration components
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001-T005)
- MCP tool schemas marked [P] can run in parallel within each user story
- Backend tests marked [P] can run in parallel
- Frontend components marked [P] can run in parallel
- Translation files marked [P] can run in parallel (T082-T087)
- Different user stories can be worked on in parallel by different team members after US1 complete

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US1 - Natural Language Task Management
4. Complete Phase 4: US2 - Stateless Conversation Persistence
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo MVP chatbot

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 → Test independently → Deploy/Demo (MVP!)
3. Add US2 → Test independently → Deploy/Demo (Persistence working)
4. Add US3 → Test independently → Deploy/Demo (Smart chaining)
5. Add US4 → Test independently → Deploy/Demo (Full Phase II integration)
6. Add US6 → Test independently → Deploy/Demo (Context memory)
7. Add US7 → Test independently → Deploy/Demo (Robust errors)
8. Add US5 (Bonus) → Test independently → Deploy/Demo (Multi-language)
9. Polish → Final deployment

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (blocks others, most critical)
3. Once US1 is done:
   - Developer A: US2
   - Developer B: US3
   - Developer C: US4
4. Once US2-US4 are done:
   - Developer A: US6
   - Developer B: US7
   - Developer C: US5 (Bonus)
5. Team collaborates on Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- 80%+ test coverage required (pytest backend, Jest frontend)
- All MCP tools must validate user_id ownership before operations
- All chat endpoints must use JWT authentication from Phase II
- Stateless architecture: zero server-side memory, all state in database
- OpenAI API rate limits: implement exponential backoff retry logic
- Neon connection pooling: configure pool_size and max_overflow
- Performance target: p95 chat response latency < 3 seconds
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Success Metrics

### Feature Completeness
- All 75 functional requirements implemented and tested
- All 7 user stories validated with acceptance scenarios
- 10 MCP tools functional (5 basic + 5 advanced)
- 6 languages supported (English, Urdu, Arabic, Spanish, French, German)

### Quality Metrics
- 80%+ test coverage (pytest + Jest)
- p95 chat latency < 3 seconds (including AI processing)
- 100 concurrent users supported without degradation
- Zero authentication bypasses
- Zero SQL injection vulnerabilities
- All tests passing

### Documentation Completeness
- tasks.md (this file)
- DEPLOYMENT.md (deployment checklist)
- README.md updated with Phase III documentation
- ADRs created for architectural decisions (if applicable)
- PHR created for implementation tracking
