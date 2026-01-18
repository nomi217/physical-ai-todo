# Implementation Plan: Phase II - Full-Stack Web Application with Enhanced Features

**Branch**: `001-002-phase-2` | **Date**: 2025-12-08 | **Deadline**: 2025-12-15
**Spec**: [spec.md](./spec.md)

## Summary

Transform Phase I console application into a production-ready, full-stack web application with 25+ features across 10 user stories. Implements persistent PostgreSQL storage (Neon DB), modern React frontend (Next.js 14), RESTful API (FastAPI), multi-language support (6 languages), voice commands, AI integration, and stunning 3D visual effects.

**See Also**:
- [execution-strategy.md](./execution-strategy.md) - Agent-powered development plan (10 skills, 8 agents)
- [quality-framework.md](./quality-framework.md) - Performance, testing, zero-bug standards

**Key Features (10 User Stories)**:
- US1-2: Basic web CRUD + organization (priorities, tags, search, filter, sort)
- US3-4: Multi-language voice + AI chatbot (6 languages)
- US5: Interactive (drag-drop, bulk actions, keyboard shortcuts, undo/redo)
- US6: Rich details (subtasks, notes, attachments up to 10MB, OCR)
- US7: UX polish (dark/light mode, 3D effects, animations, WCAG AA)
- US8: Data management (export/import CSV/JSON, templates, analytics)
- US9-10: AI intelligence + email integration (bonus features)

**Execution**: Agent-powered (28-40 hours vs 96+ manual), quality-first (90%+ test coverage, zero bugs)

---

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.3+ (frontend)

**Primary Dependencies**:
- Backend: FastAPI 0.104+, SQLModel 0.0.14, Anthropic SDK, pytesseract, pandas
- Frontend: Next.js 14, React 18, Tailwind CSS, @dnd-kit, recharts, framer-motion

**Storage**: Neon DB (Serverless PostgreSQL) with connection pooling, Alembic migrations

**Testing**: pytest + pytest-cov (backend 90%+), Jest + Playwright (frontend 90%+)

**Target Platform**: Web (Chrome, Firefox, Safari, Edge), deployed to Vercel + Railway

**Project Type**: Full-stack web application (backend API + frontend SPA)

**Performance Goals**: API <200ms (p95), UI <100ms, First Paint <1.0s, Lighthouse >90

**Constraints**: 5-7 days timeline, 90%+ coverage mandatory, WCAG AA required, zero production bugs

**Scale/Scope**: 100+ concurrent users, 10K+ tasks/user, 6 languages, 60 functional requirements

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **PASS** - Technology stack compliant (FastAPI, SQLModel, Neon DB, Next.js 14, TypeScript)
✅ **PASS** - Phase II features correct (5 basic + 5 intermediate, no Phase III features like recurring tasks/calendar)
✅ **PASS** - Architecture evolution (Phase I preserved, new backend/frontend dirs, backward compatible)
✅ **PASS** - Spec-driven development (spec → plan → tasks → implement)
⚠️ **REVIEW** - Enhanced scope beyond constitution (justified: P2 features required for production quality, P3 clearly marked optional)

### Post-Design Re-check
- [ ] Data model maintains Phase I compatibility
- [ ] API contracts follow REST best practices
- [ ] All entities properly indexed
- [ ] Migration strategy validated

---

## Project Structure

### Documentation (this feature)

```text
specs/001-002-phase-2/
├── spec.md                    # 60 functional requirements, 10 user stories
├── plan.md                    # This file
├── execution-strategy.md      # Agent execution plan
├── quality-framework.md       # Quality standards
├── research.md                # Phase 0 output
├── data-model.md              # Phase 1: 7 entities
├── quickstart.md              # Phase 1: Setup guide
├── contracts/
│   ├── openapi.yaml           # 50+ endpoints
│   └── api-examples.md
└── tasks.md                   # Phase 2: /sp.tasks output
```

### Source Code (repository root)

```text
physical-ai-todo/
├── backend/                   # FastAPI (Python 3.13+)
│   ├── app/
│   │   ├── main.py           # FastAPI app + CORS + middleware
│   │   ├── database.py        # Neon DB connection
│   │   ├── models.py          # SQLModel (7 entities)
│   │   ├── routes/            # 50+ endpoints (tasks, subtasks, notes, attachments, etc.)
│   │   ├── services/          # AI, OCR, email, analytics
│   │   └── skills/            # Claude Code skills
│   ├── alembic/               # DB migrations
│   ├── tests/                 # pytest (90%+ coverage)
│   └── requirements.txt
│
├── frontend/                  # Next.js 14 (TypeScript)
│   ├── app/                   # App Router pages
│   ├── components/            # React components (15+)
│   ├── lib/                   # API client, utils
│   ├── hooks/                 # Custom hooks
│   ├── __tests__/             # Jest + Playwright
│   └── package.json
│
├── .claude/                   # Claude Code
│   ├── skills/                # 10 reusable skills
│   └── agents/                # 8 specialized agents
│
├── src/todo/                  # Phase I (preserved)
└── specs/                     # Feature specs
```

**Structure Decision**: Web application - separate backend/frontend. Backend is standalone FastAPI REST API. Frontend is Next.js 14 SPA. Phase I preserved in `src/todo/`.

---

## Phase 0: Research & Technology Validation

**Objective**: Resolve unknowns, validate choices, establish best practices

**Research Tasks**:
1. Neon DB connection pooling (pool size, validation, recycling)
2. Next.js 14 performance (code splitting, server vs client components)
3. Dark mode no-flicker (inline script, system detection, WCAG AA)
4. 3D effects (framer-motion vs react-spring, performance, glassmorphism)
5. Drag-drop @dnd-kit (touch support, accessibility, optimistic updates)
6. OCR integration (pytesseract accuracy, PDF extraction, preprocessing)
7. React Query caching (staleTime, cacheTime, invalidation)
8. File upload streaming (multipart, progress, 10MB handling)
9. Claude API (prompt engineering, context management, cost optimization)
10. i18n for 6 languages (RTL support, font loading)

**Deliverable**: `research.md` with decisions, rationales, alternatives for each topic

---

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete

### 1.1 Data Model (`data-model.md`)

**7 Entities**:
1. Task (extended): +display_order, +is_template
2. Subtask: task_id, title, completed, display_order
3. Note: task_id, content
4. Attachment: task_id, filename, file_url, file_size, mime_type, ocr_text
5. Template: name, title, description, priority, tags, subtasks (JSON)
6. ActivityLog: task_id, action_type, field_changed, old/new values
7. VoiceCommand: transcript, language, intent, confidence

**Indexes**: All foreign keys, frequently queried fields (completed, priority, display_order)

### 1.2 API Contracts (`contracts/openapi.yaml`)

**50+ Endpoints**:
- Tasks (10): CRUD + bulk operations
- Subtasks (5): CRUD + reorder
- Notes (4): CRUD
- Attachments (5): upload, download, OCR
- Templates (5): CRUD + instantiate
- Analytics (4): summary, timeline, productivity, activity
- Export/Import (4): CSV/JSON
- AI (9): chat, suggest, breakdown, parse, search, insights
- Email (3): send, parse, inbox address
- Voice (2): transcribe, command

### 1.3 Quickstart (`quickstart.md`)

- Prerequisites (Python 3.13+, Node 20+, Neon DB)
- Environment setup
- Backend setup (venv, pip, alembic, uvicorn)
- Frontend setup (npm install, npm run dev)
- Testing (pytest, npm test)
- Common issues

### 1.4 Agent Context Update

Run: `.specify/scripts/bash/update-agent-context.sh claude`

---

## Phase 2: Task Breakdown

**Delegated to**: `/sp.tasks` command

**Expected**: 150+ tasks in `tasks.md` organized by phase, user story, priority, parallelizability

---

## Implementation Strategy (See execution-strategy.md)

**10 Custom Skills**: fastapi-crud, nextjs-component, sqlmodel-schema, api-client, alembic-migration, test-generator, dark-mode, analytics-dashboard, ocr-service, email-integration

**8 Specialized Agents**: db-architect, backend-builder, frontend-builder, ai-engineer, file-handler, data-migrator, ux-polisher, qa-tester

**3-Phase Execution**:
- Phase 1: Foundation (8h parallel) - DB + API + frontend setup + AI
- Phase 2: Core Features (12h parallel) - Interactive + rich details + data + files
- Phase 3: Polish (6h sequential) - QA + animations + deployment

**Time**: 28-40 hours (vs 96+ manual) = 60-70% savings

---

## Quality Assurance (See quality-framework.md)

**Performance**:
- API p95 <200ms, UI <100ms, FCP <1.0s, Lighthouse >90
- Database indexes, React.memo, code splitting, caching

**Testing**:
- 90%+ coverage (70% unit, 20% integration, 10% E2E)
- CI enforces coverage minimums
- Playwright for user flows

**Dark Mode**:
- No flicker (inline script before hydration)
- Persisted in localStorage
- System preference detection
- WCAG AA contrast (4.5:1 minimum)
- 200ms smooth transitions

**3D Effects**:
- 60fps (16ms budget)
- GPU-accelerated transforms
- Reduce-motion support
- Graceful degradation

---

## Risk Mitigation

1. **Scope creep**: P1/P2 first, P3 bonus, time-box to 2x estimate
2. **Performance**: indexes, memoization, code splitting, perf tests in CI
3. **Dark mode flicker**: inline script, localStorage, comprehensive testing
4. **Agent coordination**: dependency graph, parallel execution, TodoWrite tracking
5. **Coverage failure**: test-generator skill, CI enforcement, QA checklist

---

## Success Criteria

**Phase 0 Complete**: All research documented, technology choices justified
**Phase 1 Complete**: data-model.md, contracts/, quickstart.md, agent context updated
**Phase 2 Complete**: tasks.md with 150+ tasks
**Implementation Complete**: All P1/P2 features (18), 90%+ coverage, quality gates passed, perfect dark mode, performance targets met, deployed
**Bonus Complete**: P3 features, 6 languages, 3D effects, demo video

---

## Deliverables

### Design Artifacts (Phase 1)
1. ✅ plan.md
2. ⏳ research.md
3. ⏳ data-model.md
4. ⏳ contracts/openapi.yaml
5. ⏳ quickstart.md

### Implementation (Phase 2+)
6. ⏳ tasks.md
7. ⏳ Backend code
8. ⏳ Frontend code
9. ⏳ Tests (90%+)
10. ⏳ Deployment

---

## Next Steps

1. Create Phase 0 artifacts (research.md) - 2h
2. Create Phase 1 artifacts (data-model.md, contracts/, quickstart.md) - 3h
3. Run `/sp.tasks` - 30min
4. Review and approve - 1h
5. Begin implementation via `/sp.implement` - 28-40h

**Total**: 35-47 hours (~5-6 days)

**Plan Status**: Phase 0 (Research) - Ready to begin
**Last Updated**: 2025-12-08
**Next Action**: Create research.md
