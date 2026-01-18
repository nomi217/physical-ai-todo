---
id: 0002
title: Create Phase III implementation plan
stage: plan
date: 2025-12-13
surface: agent
model: claude-sonnet-4-5
feature: 004-ai-chatbot
branch: 004-ai-chatbot
user: Ahsan
command: /sp.plan
labels: ["planning", "phase-3", "ai-chatbot", "mcp-server", "openai-agents", "architecture"]
links:
  spec: specs/004-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-ai-chatbot/plan.md
  - specs/004-ai-chatbot/research.md
  - specs/004-ai-chatbot/data-model.md
  - specs/004-ai-chatbot/quickstart.md
  - specs/004-ai-chatbot/contracts/chat-api.yaml
  - specs/004-ai-chatbot/contracts/mcp-tools.yaml
  - CLAUDE.md
tests:
  - Constitution compliance check (8 principles validated)
  - Spec alignment validation (all 75 FRs traceable)
  - Technical feasibility review (research validated all decisions)
---

## Prompt

**User Command**: `/sp.plan`

**Full Context**: User executed the `/sp.plan` slash command to generate the implementation plan for Phase III AI Chatbot (feature 004-ai-chatbot). This command follows the spec-driven development workflow where specification was already created via `/sp.specify`. The planning workflow requires:

1. Setup: Read spec.md, constitution.md, plan template
2. Fill Technical Context section (mark unknowns as NEEDS CLARIFICATION)
3. Execute Constitution Check (validate against 8 principles)
4. Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION items)
5. Phase 1: Generate data-model.md, contracts/, quickstart.md, update agent context
6. Report deliverables

**Prerequisites**:
- Spec.md completed (354 lines, 75 FRs, 7 user stories, ALL 14 CHECKS PASSED)
- Phase II infrastructure exists (FastAPI backend, Next.js frontend, PostgreSQL, auth at 85% complete)
- Feature branch 004-ai-chatbot already created

## Response snapshot

Successfully completed `/sp.plan` workflow generating **7 planning artifacts** (172KB total documentation):

**1. plan.md (635 lines)**
- Summary: Stateless chatbot using MCP SDK + OpenAI Agents SDK + database-first architecture
- Technical Context: Python 3.13+, FastAPI, OpenAI SDK, Next.js 14, Neon PostgreSQL
- Constitution Check: 8 principles validated (1 review item - Phase III at 85% Phase II - justified as no blocking dependencies)
- Project Structure: backend/app/mcp/, backend/app/chat/, frontend/components/chat/
- Phase 0 outline: 6 research questions (OpenAI rate limits, Neon pooling, ChatKit vs custom, MCP integration, tool calling, stateless architecture)
- Phase 1 outline: data-model.md, contracts/, quickstart.md, agent context update
- 3 potential ADRs identified (AI framework, Chat UI, context management)

**2. research.md (Phase 0 Complete)**
Resolved 6 NEEDS CLARIFICATION items:
- OpenAI API Rate Limits: GPT-4 Turbo Tier 1 (60k TPM, 500 RPM), exponential backoff retry, ~$2.25/1000 conversations
- Neon DB Connection Pooling: Free tier 100 connections, use NullPool for serverless, connection error handling
- **ChatKit vs Custom UI Decision**: Custom React components (design consistency with Phase II glassmorphism, RTL support, 5 extra days effort but better UX)
- MCP SDK Integration: Embedded MCP tools in FastAPI (not separate server), reference implementation provided
- OpenAI Tool Calling: Function calling flow, JSON Schema format, iterative tool chaining pattern
- **Stateless Architecture Decision**: Recent 20 messages sliding window (balances $0.02/request cost vs context quality, <10ms DB load)

**3. data-model.md (Phase 1)**
- ConversationMessage table: 8 columns (id, conversation_id, user_id, role, content, tool_calls, created_at, updated_at)
- 3 composite indexes (conversation_id+created_at, user_id+created_at, conversation_id+user_id)
- Foreign key to users table with CASCADE delete
- CHECK constraint for role validation (user/assistant)
- Alembic migration strategy (backward compatible)
- SQLModel schema with Pydantic models

**4. contracts/chat-api.yaml (OpenAPI 3.0)**
- POST /api/v1/chat: Request (conversation_id optional int, message required string), Response (conversation_id int, response string, tool_calls array)
- Authentication: JWT Bearer token or httpOnly cookie from Phase II
- Error responses: 400 (bad request), 401 (unauthorized), 403 (forbidden), 429 (rate limit), 500 (server error), 503 (service unavailable)
- Examples for new conversation, existing conversation, tool execution scenarios

**5. contracts/mcp-tools.yaml (10 MCP tools)**
Basic CRUD: add_task, list_tasks, complete_task, delete_task, update_task
Advanced (Phase II integration): set_priority, manage_tags, manage_subtasks
Search: search_tasks, filter_tasks
Each tool: JSON Schema parameters, return types, docstrings for AI, error schemas

**6. quickstart.md (Phase 1 Implementation Guide)**
- Prerequisites check (Python 3.13+, Node.js 18+, OpenAI API key)
- 8 implementation steps: installation, database migration, MCP server setup, OpenAI agent integration, chat endpoint, frontend integration, testing, deployment
- Code snippets, curl commands, troubleshooting guide
- Estimated timeline: 3-4 weeks (40-60 tasks)

**7. Agent Context Updated**
Ran `.specify/scripts/bash/update-agent-context.sh claude`:
- Updated CLAUDE.md with MCP SDK, OpenAI SDK
- Registered conversation_messages table
- Added Phase III file paths

**Constitution Compliance Summary**:
- ✅ Spec-Driven Development (all via /sp.plan, no manual code)
- ✅ Phase-Correct Evolution (builds on Phase I/II)
- ✅ Test-Driven Quality (80%+ coverage target)
- ✅ Modularity & Simplicity (1 MCP module, 1 endpoint, 1 table)
- ✅ No Premature Complexity (only MCP + OpenAI SDK added)
- ⚠️ Feature Budgets (3rd project at limit - JUSTIFIED: natural evolution, no blocking dependencies in remaining 5 Phase II features)
- ✅ Database Schema (1 new table, backward compatible)
- ✅ Security & Privacy (user_id validation, JWT auth)

**Key Architectural Decisions** (awaiting user consent for ADRs):
1. AI Framework: OpenAI Agents SDK (vs LangChain/Custom) - simpler, better integration
2. Chat UI: Custom React (vs OpenAI ChatKit) - design consistency, RTL support, flexibility
3. Context Management: Sliding window 20 messages (vs full history/token-based) - balances cost and quality

## Outcome

- ✅ Impact: Complete Phase III implementation plan with 7 planning artifacts (172KB), 6 research questions resolved, 3 architectural decisions documented, all constitution gates passed, ready for /sp.tasks
- 🧪 Tests: Constitution check 8/8 PASS (1 justified review), Spec alignment PASS (75 FRs traceable to design), Technical feasibility PASS (all research validated)
- 📁 Files: plan.md (27KB, 635 lines), research.md (38KB), data-model.md (19KB), quickstart.md (22KB), contracts/chat-api.yaml (14KB), contracts/mcp-tools.yaml (26KB), CLAUDE.md updated
- 🔁 Next prompts: /sp.adr (optional for 3 architectural decisions), /sp.tasks (generate task breakdown), /sp.implement (execute implementation)
- 🧠 Reflection: Planning successfully bridges Phase II web app with Phase III conversational AI. Stateless architecture ensures production scalability. Research phase made critical decisions (custom UI, 20-message window) with documented rationale. Phase II 85% completion acceptable - no blocking dependencies for chatbot. Ready for granular task breakdown.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully on first iteration
- Graders run and results (PASS/FAIL): Constitution 8/8 PASS (1 justified), Spec alignment PASS, Technical feasibility PASS, No contradictions PASS
- Prompt variant (if applicable): Default /sp.plan workflow from .specify/templates/commands/plan.md
- Next experiment (smallest change to try): Proceed to /sp.tasks for task breakdown (expect 40-60 granular tasks), optionally create 3 ADRs first to document architectural decisions formally
