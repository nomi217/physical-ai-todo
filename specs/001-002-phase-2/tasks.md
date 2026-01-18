# Implementation Tasks - Phase II Enhanced

**Feature**: Phase II - Full-Stack Web Application (11 User Stories)
**Branch**: `001-002-phase-2`
**Generated**: 2025-12-08
**Total Tasks**: 185

---

## Overview

This document contains **actionable implementation tasks** for all 11 user stories, organized by priority tier and dependency order.

**User Story Summary**:
- **P1 (MVP)**: US1 - Basic Web CRUD (15 tasks)
- **P2 (Core)**: US2, US5, US6, US7, US8, US11 (98 tasks)
- **P3 (Bonus)**: US3, US4, US9, US10 (48 tasks)
- **Setup/Polish**: Infrastructure + final polish (24 tasks)

**Task Format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- `[P]` = Parallelizable
- `[Story]` = User story label (US1, US2, etc.)

---

## Task Summary by Phase

| Phase | User Story | Tasks | Parallel | Priority | Description |
|-------|------------|-------|----------|----------|-------------|
| 1 | Setup | 10 | 6 | - | Project initialization, dependencies |
| 2 | Foundation | 14 | 8 | - | Database, core models, API skeleton |
| 3 | US1 (P1) | 15 | 8 | P1 | Basic web CRUD (MVP) |
| 4 | US2 (P2) | 12 | 7 | P2 | Priorities, tags, search, filter, sort |
| 5 | US5 (P2) | 15 | 9 | P2 | Drag-drop, bulk actions, inline edit, undo |
| 6 | US6 (P2) | 18 | 10 | P2 | Subtasks, notes, attachments, OCR |
| 7 | US7 (P2) | 16 | 10 | P2 | Dark mode, 3D effects, keyboard shortcuts |
| 8 | US8 (P2) | 14 | 8 | P2 | Export/import, templates, analytics |
| 9 | US11 (P2) | 9 | 5 | P2 | Focus mode, AI task help |
| 10 | US3 (P3) | 10 | 6 | P3 | Voice commands (6 languages) |
| 11 | US4 (P3) | 10 | 6 | P3 | AI chatbot |
| 12 | US9 (P3) | 12 | 7 | P3 | AI intelligence features |
| 13 | US10 (P3) | 16 | 9 | P3 | Email integration, OCR |
| 14 | Polish | 14 | 8 | - | Testing, deployment, docs |

**Total**: 185 tasks | **Parallel Opportunities**: 107 tasks marked [P]

---

## MVP Scope

**Minimum Viable Product** = Phase 1 + Phase 2 + Phase 3 (US1)

**Total MVP Tasks**: 39 tasks
**Estimated Time**: 12-15 hours
**Deliverable**: Functional web-based todo app with CRUD operations

---

## Phase 1: Setup & Project Initialization

**Goal**: Initialize backend and frontend projects with all dependencies

**Estimated Time**: 2-3 hours

### Tasks

- [X] T001 Create backend directory structure: backend/app/{models,routes,services,skills}/
- [X] T002 Create frontend directory structure: frontend/{app,components,lib,hooks,__tests__}/
- [X] T003 [P] Create backend/requirements.txt with FastAPI, SQLModel, uvicorn, psycopg2-binary, anthropic, pytesseract, pandas, python-multipart, Pillow, PyPDF2, python-emails, alembic
- [X] T004 [P] Create frontend/package.json with Next.js 14, React 18, TypeScript, Tailwind, @dnd-kit, recharts, framer-motion, react-spring, @tanstack/react-query, papaparse
- [X] T005 [P] Create backend/.env.example with DATABASE_URL, ANTHROPIC_API_KEY, CORS_ORIGINS placeholders
- [X] T006 [P] Create frontend/.env.local.example with NEXT_PUBLIC_API_URL, NEXT_PUBLIC_ANTHROPIC_API_KEY
- [ ] T007 Set up Neon DB account and create database instance, save connection string
- [X] T008 [P] Initialize Alembic in backend/alembic/ with env.py configured for SQLModel
- [X] T009 [P] Create backend/app/main.py with FastAPI app, CORS middleware, basic health check endpoint
- [X] T010 [P] Create frontend/app/layout.tsx with Next.js App Router, ThemeProvider, globals.css

**Validation**: Both projects install dependencies successfully, servers start without errors

---

## Phase 2: Foundation (Database + API Skeleton + Frontend Setup)

**Goal**: Create core models, database migrations, API skeleton, and frontend foundation

**Estimated Time**: 6-8 hours

**Dependencies**: Phase 1 complete

### Tasks

#### Backend Foundation

- [X] T011 [P] Create backend/app/database.py with Neon DB engine, connection pooling (pool_size=10, max_overflow=20), session management
- [X] T012 [P] Create backend/app/models.py with Task model (id, title, description, completed, priority, tags, display_order, is_template, created_at, updated_at) per data-model.md
- [X] T013 [P] Add Subtask model to backend/app/models.py (id, task_id, title, completed, display_order, created_at, updated_at)
- [X] T014 [P] Add Note model to backend/app/models.py (id, task_id, content, created_at, updated_at)
- [X] T015 [P] Add Attachment model to backend/app/models.py (id, task_id, filename, file_url, file_size, mime_type, ocr_text, created_at)
- [X] T016 [P] Add Template model to backend/app/models.py (id, name, title, description, priority, tags, subtasks as JSON, created_at, updated_at)
- [X] T017 [P] Add ActivityLog model to backend/app/models.py (id, task_id, action_type, field_changed, old_value, new_value, created_at)
- [X] T018 Generate Alembic migration for all 7 entities with indexes on foreign keys and frequently queried fields (completed, priority, display_order, created_at)
- [X] T019 Run Alembic migration: alembic upgrade head, verify tables created in Neon DB
- [X] T020 [P] Create backend/app/schemas.py with Pydantic schemas for TaskCreate, TaskUpdate, TaskResponse (with optional relations)

#### Frontend Foundation

- [X] T021 [P] Create frontend/lib/types.ts with TypeScript interfaces matching backend models
- [X] T022 [P] Create frontend/lib/api.ts with API client base URL, fetch wrapper, error handling
- [X] T023 [P] Set up @tanstack/react-query in frontend/app/layout.tsx with QueryClientProvider
- [X] T024 [P] Create frontend/app/globals.css with Tailwind base, dark mode CSS variables, smooth transitions

**Validation**: Database has 7 tables with proper indexes, API starts, frontend compiles

---

## Phase 3: US1 - Basic Web Todo Management (P1 - MVP)

**Goal**: Implement complete CRUD functionality via web UI with persistent storage

**User Story**: As a user, I want to manage my tasks through a modern web interface with persistent database storage

**Independent Test**: Can create, view, update, delete, and mark tasks complete through the web UI. Data persists after browser refresh.

**Estimated Time**: 8-10 hours

**Dependencies**: Phase 2 complete

### Tasks

#### Backend API (US1)

- [ ] T025 [P] [US1] Create backend/app/routes/tasks.py with GET /tasks endpoint (list with pagination limit=50, offset=0)
- [ ] T026 [P] [US1] Implement GET /tasks/{id} endpoint in backend/app/routes/tasks.py (single task with optional relations)
- [ ] T027 [P] [US1] Implement POST /tasks endpoint in backend/app/routes/tasks.py (create task with validation)
- [ ] T028 [P] [US1] Implement PUT /tasks/{id} endpoint in backend/app/routes/tasks.py (full update)
- [ ] T029 [P] [US1] Implement PATCH /tasks/{id} endpoint in backend/app/routes/tasks.py (partial update)
- [ ] T030 [P] [US1] Implement DELETE /tasks/{id} endpoint in backend/app/routes/tasks.py (soft delete with activity log)
- [ ] T031 [US1] Register task routes in backend/app/main.py with /api/v1 prefix

#### Frontend Components (US1)

- [ ] T032 [P] [US1] Create frontend/components/TaskList.tsx with task rendering, empty state, loading state
- [ ] T033 [P] [US1] Create frontend/components/TaskItem.tsx with task card, checkbox for completion, edit/delete buttons
- [ ] T034 [P] [US1] Create frontend/components/TaskForm.tsx with title/description inputs, priority select, tag input, submit handling
- [ ] T035 [P] [US1] Create frontend/lib/api.ts functions: useTasks(), useCreateTask(), useUpdateTask(), useDeleteTask() with React Query
- [ ] T036 [US1] Create frontend/app/page.tsx main dashboard with TaskList, TaskForm modal, create button
- [ ] T037 [US1] Connect TaskList to API using useTasks() hook, implement optimistic updates for completion toggle
- [ ] T038 [US1] Implement task create/edit/delete functionality with proper error handling and success toasts
- [ ] T039 [US1] Add responsive design (mobile + desktop) with Tailwind breakpoints, test on 320px to 1920px widths

**Validation**: All CRUD operations work, data persists in Neon DB, UI responsive on all devices

---

## Phase 4: US2 - Advanced Task Organization (P2)

**Goal**: Add priorities, tags, search, filter, and sort capabilities

**User Story**: As a user, I want to organize my tasks with priorities and tags, and quickly find tasks using search and filters

**Independent Test**: Can assign priorities/tags, search by text, filter by status/priority/tags, sort by different criteria

**Estimated Time**: 5-6 hours

**Dependencies**: Phase 3 complete

### Tasks

- [ ] T040 [P] [US2] Add search query parameter to GET /tasks in backend/app/routes/tasks.py (full-text search on title + description)
- [ ] T041 [P] [US2] Add filter query parameters to GET /tasks: completed, priority, tags (comma-separated)
- [ ] T042 [P] [US2] Add sort query parameter to GET /tasks: created_at, updated_at, priority, title, display_order (with asc/desc order)
- [ ] T043 [P] [US2] Add database indexes for search performance in new Alembic migration (title GIN index for PostgreSQL)
- [ ] T044 [P] [US2] Create frontend/components/FilterBar.tsx with search input, priority filter dropdown, tag filter multi-select, sort dropdown
- [ ] T045 [P] [US2] Create frontend/components/PriorityBadge.tsx with color coding (red=high, amber=medium, green=low)
- [ ] T046 [P] [US2] Create frontend/components/TagInput.tsx with autocomplete for existing tags, multi-tag support
- [ ] T047 [US2] Add priority and tags fields to TaskForm.tsx with proper UI controls
- [ ] T048 [US2] Integrate FilterBar into frontend/app/page.tsx with URL query params for filters (bookmarkable)
- [ ] T049 [US2] Implement tag autocomplete in TagInput using existing tags from API
- [ ] T050 [US2] Add visual priority indicators to TaskItem (colored border/badge)
- [ ] T051 [US2] Test search performance with 1000+ tasks, verify <200ms response time

**Validation**: Search returns results in <200ms, filters update UI instantly, tags autocomplete works

---

## Phase 5: US5 - Interactive Task Management (P2)

**Goal**: Drag-drop reordering, bulk actions, inline editing, keyboard shortcuts, undo/redo

**User Story**: As a user, I want to interact with my tasks naturally through drag-and-drop, bulk actions, and keyboard shortcuts

**Independent Test**: Can drag tasks to reorder, select multiple for bulk operations, edit inline, undo mistakes

**Estimated Time**: 7-8 hours

**Dependencies**: Phase 3 complete

### Tasks

#### Drag-Drop

- [ ] T052 [P] [US5] Add PATCH /tasks/reorder endpoint in backend/app/routes/tasks.py (accepts array of {id, display_order})
- [ ] T053 [US5] Install @dnd-kit/core, @dnd-kit/sortable, @dnd-kit/utilities in frontend
- [ ] T054 [US5] Wrap TaskList.tsx with DndContext and SortableContext from @dnd-kit
- [ ] T055 [US5] Make TaskItem.tsx sortable with useSortable hook, add drag handle icon
- [ ] T056 [US5] Implement onDragEnd handler to update display_order optimistically and call API

#### Bulk Actions

- [ ] T057 [P] [US5] Add POST /tasks/bulk/complete endpoint in backend/app/routes/tasks.py (body: {task_ids: number[]})
- [ ] T058 [P] [US5] Add POST /tasks/bulk/delete endpoint in backend/app/routes/tasks.py
- [ ] T059 [P] [US5] Add POST /tasks/bulk/tag endpoint in backend/app/routes/tasks.py (body: {task_ids, tag})
- [ ] T060 [P] [US5] Add POST /tasks/bulk/priority endpoint in backend/app/routes/tasks.py (body: {task_ids, priority})
- [ ] T061 [P] [US5] Create frontend/components/BulkActions.tsx toolbar with Complete, Delete, Tag, Priority buttons
- [ ] T062 [US5] Add checkbox selection to TaskItem.tsx, track selected tasks in TaskList state
- [ ] T063 [US5] Show BulkActions toolbar when tasks selected, hide when none selected
- [ ] T064 [US5] Implement bulk operations with confirmation dialogs for destructive actions

#### Inline Editing & Undo

- [ ] T065 [P] [US5] Create frontend/lib/undo.ts with undo stack manager (max 50 actions)
- [ ] T066 [US5] Add inline edit mode to TaskItem.tsx (double-click title to edit, Enter to save, Esc to cancel)
- [ ] T067 [US5] Implement undo/redo functionality using frontend/lib/undo.ts, track create/update/delete/complete/bulk actions
- [ ] T068 [US5] Add keyboard shortcuts with react-hotkeys-hook: Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+N (new task), / (search focus), j/k (navigate), Space (toggle complete), Delete (delete selected)
- [ ] T069 [US5] Create frontend/components/KeyboardShortcuts.tsx help overlay (triggered by ? key)

**Validation**: Drag-drop persists order, bulk actions work, inline edit saves, undo/redo functional

---

## Phase 6: US6 - Rich Task Details (P2)

**Goal**: Subtasks, notes, file attachments, OCR

**User Story**: As a user, I want to add subtasks, notes, and file attachments to my tasks

**Independent Test**: Can create subtasks with progress tracking, add notes with timestamps, attach files up to 10MB, OCR extracts text

**Estimated Time**: 9-10 hours

**Dependencies**: Phase 3 complete

### Tasks

#### Subtasks

- [ ] T070 [P] [US6] Create backend/app/routes/subtasks.py with GET /tasks/{task_id}/subtasks endpoint
- [ ] T071 [P] [US6] Add POST /tasks/{task_id}/subtasks endpoint in backend/app/routes/subtasks.py
- [ ] T072 [P] [US6] Add PATCH /subtasks/{id} endpoint (update title/completed)
- [ ] T073 [P] [US6] Add DELETE /subtasks/{id} endpoint
- [ ] T074 [P] [US6] Add PATCH /subtasks/reorder endpoint for drag-drop reordering
- [ ] T075 [P] [US6] Create frontend/components/SubtaskList.tsx with checklist UI, progress indicator (3/5 - 60%)
- [ ] T076 [US6] Add subtask creation input to SubtaskList, handle Enter key to create
- [ ] T077 [US6] Show SubtaskList in task detail panel or expanded TaskItem

#### Notes

- [ ] T078 [P] [US6] Create backend/app/routes/notes.py with GET /tasks/{task_id}/notes endpoint
- [ ] T079 [P] [US6] Add POST /tasks/{task_id}/notes endpoint (create note with timestamp)
- [ ] T080 [P] [US6] Add PATCH /notes/{id} endpoint (edit note content)
- [ ] T081 [P] [US6] Add DELETE /notes/{id} endpoint
- [ ] T082 [P] [US6] Create frontend/components/NoteEditor.tsx with textarea, character count (max 5000), timestamps
- [ ] T083 [US6] Display notes chronologically in task detail panel with edit history

#### Attachments & OCR

- [ ] T084 [P] [US6] Create backend/app/services/ocr_service.py with pytesseract integration, PDF text extraction (PyPDF2), image preprocessing
- [ ] T085 [P] [US6] Create backend/app/routes/attachments.py with GET /tasks/{task_id}/attachments endpoint
- [ ] T086 [P] [US6] Add POST /tasks/{task_id}/attachments endpoint (multipart upload, max 10MB, stream to disk)
- [ ] T087 [P] [US6] Add GET /attachments/{id}/download endpoint
- [ ] T088 [P] [US6] Add DELETE /attachments/{id} endpoint
- [ ] T089 [P] [US6] Add POST /attachments/{id}/ocr endpoint (trigger OCR, extract text, store in ocr_text field)
- [ ] T090 [P] [US6] Create frontend/components/AttachmentUpload.tsx with react-dropzone, file preview, progress bar
- [ ] T091 [US6] Validate file size (<10MB), mime types (pdf, png, jpg, docx) on frontend and backend
- [ ] T092 [US6] Display attachments with download links and OCR extracted text in task detail panel

**Validation**: Subtasks show progress, notes have timestamps, files upload successfully, OCR extracts text

---

## Phase 7: US7 - UX Polish & Accessibility (P2)

**Goal**: Dark/light mode (perfect, no flicker), 3D effects, animations, WCAG AA accessibility

**User Story**: As a user, I want a polished interface with dark mode, 3D effects, and smooth interactions

**Independent Test**: Dark mode toggles instantly with no flicker, persisted preference, 3D effects performant at 60fps, keyboard navigation works

**Estimated Time**: 8-9 hours

**Dependencies**: Phase 3 complete

### Tasks

#### Dark Mode (Perfect Implementation)

- [ ] T093 [P] [US7] Create frontend/components/ThemeProvider.tsx with theme context (light/dark/system modes)
- [ ] T094 [US7] Add inline script to frontend/app/layout.tsx <head> to read localStorage theme BEFORE React hydration (prevents flicker)
- [ ] T095 [US7] Update frontend/app/globals.css with CSS variables for light theme (--background, --foreground, --primary, etc.)
- [ ] T096 [US7] Add .dark class to globals.css with dark theme variables (WCAG AA contrast: 4.5:1 minimum)
- [ ] T097 [US7] Add 200ms smooth transitions to all theme-affected properties in globals.css
- [ ] T098 [P] [US7] Create frontend/components/ThemeToggle.tsx with Sun/Moon icons, three-way toggle (light/dark/system)
- [ ] T099 [US7] Add system preference detection (prefers-color-scheme) with mediaQuery listener
- [ ] T100 [US7] Test dark mode in all components, verify no flicker on page load, test contrast with axe-core

#### 3D Effects & Animations

- [ ] T101 [P] [US7] Install framer-motion and react-spring in frontend
- [ ] T102 [P] [US7] Add 3D card elevation to TaskItem.tsx with CSS perspective transform (translateZ), hover effects
- [ ] T103 [P] [US7] Create glassmorphism effect for modals/popovers using backdrop-filter: blur(10px) in globals.css
- [ ] T104 [P] [US7] Add 3D flip animation to TaskItem when task completed using framer-motion
- [ ] T105 [P] [US7] Create floating action button for "New Task" with 3D elevation shadow
- [ ] T106 [P] [US7] Add neon glow effects to priority badges in dark mode (box-shadow with theme colors)
- [ ] T107 [P] [US7] Add parallax scrolling to dashboard header using framer-motion scroll animations
- [ ] T108 [US7] Add spring physics animations for modal open/close, dropdowns using react-spring
- [ ] T109 [US7] Add will-change hints for GPU acceleration, test 60fps performance with Chrome DevTools
- [ ] T110 [US7] Add reduce-motion media query support for accessibility (disable animations if user prefers reduced motion)

#### Accessibility

- [ ] T111 [P] [US7] Add ARIA labels to all interactive elements (buttons, inputs, checkboxes)
- [ ] T112 [P] [US7] Add keyboard focus indicators with visible outline (2px solid primary color)
- [ ] T113 [US7] Test keyboard navigation: Tab, Shift+Tab, Enter, Space, Escape
- [ ] T114 [US7] Run axe-core accessibility audit, fix all violations
- [ ] T115 [US7] Test with screen reader (NVDA/JAWS), ensure all content accessible

**Validation**: Dark mode perfect (no flicker), 3D effects run at 60fps, WCAG AA compliant, keyboard navigation works

---

## Phase 8: US8 - Data Management & Analytics (P2)

**Goal**: Export/import (CSV/JSON), task templates, analytics dashboard, activity history

**User Story**: As a user, I want to export my data, use templates, view analytics, and see activity history

**Independent Test**: Can export to CSV/JSON, import from other tools, save/use templates, view analytics charts

**Estimated Time**: 7-8 hours

**Dependencies**: Phase 3 complete

### Tasks

#### Export/Import

- [ ] T116 [P] [US8] Create backend/app/services/export_service.py with pandas-based CSV export (all fields)
- [ ] T117 [P] [US8] Add backend/app/routes/export.py with GET /export/csv endpoint (returns CSV file download)
- [ ] T118 [P] [US8] Add GET /export/json endpoint in backend/app/routes/export.py
- [ ] T119 [P] [US8] Add POST /import/csv endpoint in backend/app/routes/export.py (multipart upload, validate, create tasks)
- [ ] T120 [P] [US8] Add POST /import/json endpoint with validation, conflict resolution
- [ ] T121 [P] [US8] Create frontend export buttons with file-saver library (download CSV/JSON)
- [ ] T122 [US8] Create frontend import UI with file upload, validation feedback, import preview

#### Templates

- [ ] T123 [P] [US8] Create backend/app/routes/templates.py with GET /templates endpoint
- [ ] T124 [P] [US8] Add POST /templates endpoint (create from existing task or custom)
- [ ] T125 [P] [US8] Add POST /templates/{id}/instantiate endpoint (create task from template)
- [ ] T126 [P] [US8] Add DELETE /templates/{id} endpoint
- [ ] T127 [P] [US8] Create frontend/components/TemplateLibrary.tsx with grid of template cards
- [ ] T128 [US8] Add "Save as Template" button to TaskForm, "Create from Template" in dashboard

#### Analytics

- [ ] T129 [P] [US8] Create backend/app/services/analytics_service.py with aggregation queries (completion rate, tasks by priority, timeline)
- [ ] T130 [P] [US8] Add backend/app/routes/analytics.py with GET /analytics/summary endpoint (total tasks, completed, pending, completion rate, tasks by priority/tag)
- [ ] T131 [P] [US8] Add GET /analytics/timeline endpoint (completion data for last 30 days)
- [ ] T132 [P] [US8] Add GET /analytics/productivity endpoint (most productive day/hour, avg completion time)
- [ ] T133 [P] [US8] Add GET /tasks/{id}/activity endpoint for activity log
- [ ] T134 [P] [US8] Create frontend/components/AnalyticsDashboard.tsx with recharts (line chart for timeline, pie chart for priorities, bar chart for tags)
- [ ] T135 [P] [US8] Create frontend/app/analytics/page.tsx with full analytics view
- [ ] T136 [US8] Add activity history display to task detail panel (created, modified, completed timestamps)

**Validation**: Export/import works with CSV and JSON, templates create tasks correctly, analytics displays accurate data

---

## Phase 9: US11 - Daily Focus & AI Task Help (P2)

**Goal**: Focus mode with filtered view and AI assistance for task understanding

**User Story**: As a user, I want a distraction-free focus mode and AI help to understand my tasks

**Independent Test**: Can enter focus mode (Ctrl+F), see only relevant tasks, ask AI for explanations/steps/alternatives

**Estimated Time**: 4-5 hours

**Dependencies**: Phase 3 complete (for focus mode), Phase 11/12 desirable but not required (for AI features)

### Tasks

#### Focus Mode

- [ ] T137 [P] [US11] Add GET /focus/tasks endpoint in backend/app/routes/tasks.py (filters: incomplete, priority high/medium only)
- [ ] T138 [P] [US11] Create frontend/app/focus/page.tsx with minimal layout (no sidebar, header only)
- [ ] T139 [P] [US11] Add Ctrl+F keyboard shortcut to enter focus mode, Esc to exit
- [ ] T140 [US11] Display task count in focus mode ("3 tasks in focus")
- [ ] T141 [US11] Add optional Pomodoro timer component (25min work, 5min break) with browser notifications

#### AI Task Help

- [ ] T142 [P] [US11] Add POST /ai/help/explain endpoint in backend/app/routes/ai.py (uses Claude API to explain task in 2-3 sentences)
- [ ] T143 [P] [US11] Add POST /ai/help/steps endpoint (AI breaks down task into 5-7 steps)
- [ ] T144 [P] [US11] Add POST /ai/help/alternatives endpoint (AI suggests 3-4 alternative approaches)
- [ ] T145 [P] [US11] Add POST /ai/help/best-time endpoint (AI analyzes user patterns, suggests optimal time)
- [ ] T146 [P] [US11] Implement response caching in backend (cache key: task_id + help_type, TTL: 1 hour)
- [ ] T147 [US11] Add right-click context menu to TaskItem with AI Help submenu (Explain, Steps, Alternatives, Best Time)
- [ ] T148 [US11] Display AI responses in popover/modal with loading state, error handling
- [ ] T149 [US11] Support all 6 languages for AI help (pass language parameter from user preference)

**Validation**: Focus mode filters correctly, Pomodoro timer works, AI help provides useful responses in all languages

---

## Phase 10: US3 - Multi-language Voice Commands (P3 - Bonus)

**Goal**: Voice input for task creation in 6 languages

**User Story**: As a user, I want to add and manage tasks using voice commands in my native language

**Independent Test**: Can speak commands in EN, UR, AR, ES, FR, DE and system understands

**Estimated Time**: 5-6 hours

**Dependencies**: Phase 3 complete

### Tasks

- [ ] T150 [P] [US3] Add POST /voice/transcribe endpoint in backend/app/routes/voice.py (Web Speech API fallback to Whisper API)
- [ ] T151 [P] [US3] Add POST /voice/command endpoint (parses transcript, executes action: create, complete, delete)
- [ ] T152 [P] [US3] Implement language detection in voice service (6 languages: en, ur, ar, es, fr, de)
- [ ] T153 [P] [US3] Create VoiceCommand model entry logging in backend
- [ ] T154 [P] [US3] Create frontend/components/VoiceInput.tsx with microphone button, recording indicator
- [ ] T155 [P] [US3] Integrate Web Speech API for browser-based voice recognition
- [ ] T156 [US3] Add language selector to VoiceInput (6 language flags)
- [ ] T157 [US3] Display transcription for user to confirm before creating task
- [ ] T158 [US3] Test voice commands in all 6 languages, verify >80% accuracy
- [ ] T159 [US3] Add voice command help overlay (what commands are supported)

**Validation**: Voice commands work in all 6 languages with >80% accuracy

---

## Phase 11: US4 - Multi-language AI Assistant (P3 - Bonus)

**Goal**: Conversational AI chatbot in 6 languages

**User Story**: As a user, I want an AI chatbot to help me manage tasks conversationally

**Independent Test**: Can chat with AI in any of 6 languages, get intelligent responses

**Estimated Time**: 5-6 hours

**Dependencies**: Phase 3 complete

### Tasks

- [ ] T160 [P] [US4] Add ChatMessage model to backend/app/models.py (id, role, content, language, created_at)
- [ ] T161 [P] [US4] Create backend/app/services/ai_service.py with Claude API integration, conversation context management
- [ ] T162 [P] [US4] Add POST /ai/chat endpoint in backend/app/routes/ai.py (sends message, gets response)
- [ ] T163 [P] [US4] Add GET /ai/history endpoint (returns chat history)
- [ ] T164 [P] [US4] Add DELETE /ai/history endpoint (clears conversation)
- [ ] T165 [P] [US4] Create frontend/components/ChatBot.tsx with message list, input field, send button
- [ ] T166 [P] [US4] Create frontend/app/chat/page.tsx with full chat interface
- [ ] T167 [US4] Implement language detection and response in same language as user input
- [ ] T168 [US4] Add chat context awareness (knows user's tasks, can reference them)
- [ ] T169 [US4] Test chatbot in all 6 languages, verify intelligent task management suggestions

**Validation**: Chatbot responds intelligently in all 6 languages, understands task context

---

## Phase 12: US9 - AI-Powered Intelligence (P3 - Bonus)

**Goal**: Auto-categorization, task breakdown, semantic search, productivity insights

**User Story**: As a user, I want AI to help me categorize tasks, break them down, and provide insights

**Independent Test**: AI suggests tags/priorities, breaks down complex tasks, semantic search understands intent

**Estimated Time**: 6-7 hours

**Dependencies**: Phase 3 complete

### Tasks

- [ ] T170 [P] [US9] Add POST /ai/suggest-tags endpoint in backend/app/routes/ai.py (analyzes title/description, suggests tags)
- [ ] T171 [P] [US9] Add POST /ai/suggest-priority endpoint (suggests priority based on keywords, urgency indicators)
- [ ] T172 [P] [US9] Add POST /ai/breakdown endpoint (splits complex task into 5-7 subtasks with Claude)
- [ ] T173 [P] [US9] Add POST /ai/parse-nl endpoint (extracts metadata from natural language: "Buy milk tomorrow at 3pm")
- [ ] T174 [P] [US9] Add POST /ai/semantic-search endpoint (understands "urgent work items" without exact keyword match)
- [ ] T175 [P] [US9] Add GET /ai/insights endpoint (analyzes user patterns: "You complete most tasks on Mondays")
- [ ] T176 [P] [US9] Create backend/app/skills/task_analyzer.py with auto-categorization logic
- [ ] T177 [P] [US9] Create backend/app/skills/task_breakdown.py with task splitting rules
- [ ] T178 [US9] Add "AI Suggest" buttons to TaskForm (auto-fill priority/tags)
- [ ] T179 [US9] Add "AI Breakdown" button to complex tasks (creates subtasks automatically)
- [ ] T180 [US9] Implement semantic search in search bar with toggle (keyword vs semantic)
- [ ] T181 [US9] Display AI insights in analytics dashboard

**Validation**: AI suggestions accurate, task breakdown creates useful subtasks, semantic search understands intent

---

## Phase 13: US10 - Email Integration & OCR (P3 - Bonus)

**Goal**: Send tasks via email, email-to-task, OCR for attachments

**User Story**: As a user, I want to email tasks and create tasks from emails

**Independent Test**: Can send task via email, forward emails to create tasks, OCR extracts text from images/PDFs

**Estimated Time**: 8-9 hours

**Dependencies**: Phase 6 complete (for OCR), Phase 3 for basic features

### Tasks

#### Email Sending

- [ ] T182 [P] [US10] Create backend/app/services/email_service.py with SendGrid/SMTP integration
- [ ] T183 [P] [US10] Add POST /email/send-task endpoint in backend/app/routes/email.py (sends formatted email with task details)
- [ ] T184 [P] [US10] Create email template for tasks (HTML with task title, description, priority, subtasks)
- [ ] T185 [US10] Add "Email Task" button to TaskItem, modal for recipient email input

#### Email-to-Task

- [ ] T186 [P] [US10] Add POST /email/parse endpoint (parses email subject + body, creates task)
- [ ] T187 [P] [US10] Set up email webhook receiver (SendGrid inbound parse or SMTP listener)
- [ ] T188 [P] [US10] Add GET /email/inbox-address endpoint (returns unique inbox address for user)
- [ ] T189 [US10] Implement email parsing logic (subject → title, body → description, detect priority keywords)
- [ ] T190 [US10] Test email-to-task by forwarding emails to inbox address

#### Enhanced OCR

- [ ] T191 [P] [US10] Enhance backend/app/services/ocr_service.py with multi-language support (en, ur, ar via Tesseract)
- [ ] T192 [P] [US10] Add image preprocessing (grayscale, contrast enhancement, noise reduction) for better OCR accuracy
- [ ] T193 [P] [US10] Add PDF page-by-page OCR (convert to images, extract text from each page)
- [ ] T194 [P] [US10] Implement auto-detection of action items in OCR text ("TODO:", "Action:", "Task:")
- [ ] T195 [US10] Auto-create subtasks from detected action items in OCR text
- [ ] T196 [US10] Test OCR with handwritten notes, scanned documents, screenshots
- [ ] T197 [US10] Add OCR quality indicator (confidence score) in frontend

**Validation**: Email sending works, email-to-task creates valid tasks, OCR handles images/PDFs/handwriting

---

## Phase 14: Polish & Deployment

**Goal**: Final testing, documentation, deployment

**Estimated Time**: 6-7 hours

**Dependencies**: All P1 and P2 phases complete (P3 optional)

### Tasks

#### Testing

- [ ] T198 [P] Write pytest unit tests for all backend CRUD operations in backend/tests/unit/test_crud.py (target 90%+ coverage)
- [ ] T199 [P] Write pytest integration tests for API endpoints in backend/tests/integration/test_api.py
- [ ] T200 [P] Write Jest unit tests for React components in frontend/__tests__/components/
- [ ] T201 [P] Write Playwright E2E tests for all user flows in frontend/e2e/ (create, edit, delete, search, filter, dark mode)
- [ ] T202 Run pytest with coverage: pytest --cov=app --cov-report=term-missing, verify 90%+ coverage
- [ ] T203 Run npm test with coverage, verify 90%+ coverage
- [ ] T204 Run Playwright E2E tests, verify all user stories pass
- [ ] T205 Run Lighthouse audit, verify Performance >90, Accessibility >95

#### Documentation

- [ ] T206 [P] Update README.md with feature list, setup instructions, screenshots
- [ ] T207 [P] Generate API documentation from OpenAPI spec (Swagger UI auto-generated)
- [ ] T208 [P] Create frontend/README.md with component documentation, development guide
- [ ] T209 [P] Create backend/README.md with API documentation, environment setup
- [ ] T210 [US7] Create keyboard shortcuts reference doc (all shortcuts listed)

#### Deployment

- [ ] T211 Deploy backend to Railway/Render, configure environment variables (DATABASE_URL, ANTHROPIC_API_KEY)
- [ ] T212 Deploy frontend to Vercel, configure NEXT_PUBLIC_API_URL
- [ ] T213 Run production smoke tests (create task, complete task, dark mode toggle)
- [ ] T214 Monitor production for 24 hours, check logs for errors
- [ ] T215 Create demo video showcasing all features (5 minutes max)

**Validation**: 90%+ test coverage, documentation complete, deployed to production, all features working

---

## Dependencies & Execution Order

### Critical Path

```
Phase 1 (Setup)
  ↓
Phase 2 (Foundation)
  ↓
Phase 3 (US1) ← MVP Minimum
  ↓
Phase 4-9 (P2 Features) ← Can be parallelized
  ↓
Phase 14 (Polish & Deploy)
```

### Parallel Execution Opportunities

**After Phase 3 Complete** - These can run in parallel:
- Phase 4 (US2) - Organization features
- Phase 5 (US5) - Interactive features
- Phase 6 (US6) - Rich details
- Phase 7 (US7) - UX polish
- Phase 8 (US8) - Data management
- Phase 9 (US11) - Focus mode & AI help

**P3 Bonus Features** - Can start after Phase 3:
- Phase 10 (US3) - Voice
- Phase 11 (US4) - AI Chat
- Phase 12 (US9) - AI Intelligence
- Phase 13 (US10) - Email

**Recommended Order for Efficiency**:
1. Setup + Foundation (Phases 1-2) - Sequential
2. US1 MVP (Phase 3) - Sequential
3. US2 + US5 + US7 (Phases 4, 5, 7) - Parallel (frontend-heavy)
4. US6 + US8 + US11 (Phases 6, 8, 9) - Parallel (backend-heavy)
5. Bonus features (Phases 10-13) - Parallel (if time permits)
6. Polish (Phase 14) - Sequential

---

## Implementation Strategy

### Week 1: MVP + Core Features (P1 + P2)

**Day 1-2**: Phases 1-3 (Setup + Foundation + US1 MVP)
**Day 3-4**: Phases 4-9 (P2 features in parallel)
**Day 5**: Phase 14 (Testing + Deploy)

### Week 2: Bonus Features (P3) - Optional

**Day 6-7**: Phases 10-13 (Voice, AI Chat, Intelligence, Email)
**Day 8**: Additional Polish + Demo Video

---

## Validation Checklist

Before marking phase complete, verify:

- [ ] All tasks in phase checked off
- [ ] Independent test criteria passed
- [ ] No console errors in browser
- [ ] No TypeScript compilation errors
- [ ] API responses < 200ms (p95)
- [ ] UI interactions < 100ms
- [ ] Tests written and passing (if in testing phase)
- [ ] Code reviewed for quality
- [ ] Git commit created with descriptive message

---

## Next Steps

1. ✅ Review tasks.md with team
2. ⏳ Start Phase 1 (Setup) - estimated 2-3 hours
3. ⏳ Complete MVP (Phases 1-3) - target: end of Day 2
4. ⏳ Implement P2 features (Phases 4-9) - target: end of Day 4
5. ⏳ Polish & Deploy (Phase 14) - target: end of Day 5

**Total Estimated Time**:
- MVP Only: 12-15 hours
- MVP + P2: 55-65 hours
- Full (MVP + P2 + P3): 90-100 hours

**With Agent Assistance** (60-70% time savings):
- MVP Only: 5-6 hours
- MVP + P2: 22-26 hours
- Full: 36-40 hours

---

**Tasks.md Generated**: 2025-12-08
**Total Tasks**: 185
**Ready for Implementation**: ✅
