# Feature Specification: Phase II - Full-Stack Web Application + AI Features

**Feature Branch**: `001-002-phase-2`
**Created**: 2025-12-07
**Deadline**: 2025-12-12
**Points**: 150 + Bonus
**Status**: Draft
**Input**: "Full-stack web application with Next.js, FastAPI, SQLModel, Neon DB + Bonus AI features"

## User Scenarios & Testing

### User Story 1 - Basic Web Todo Management (Priority: P1)

As a user, I want to manage my tasks through a modern web interface with persistent database storage, so I can access my tasks from any browser and have them saved permanently.

**Why this priority**: Core functionality - must work before any advanced features. This is the MVP.

**Independent Test**: Can create, view, update, delete, and mark tasks complete through the web UI. Data persists after browser refresh or app restart.

**Acceptance Scenarios**:

1. **Given** I am on the web dashboard, **When** I create a new task with title "Buy groceries", **Then** it appears in my task list immediately
2. **Given** I have tasks in my list, **When** I refresh the browser, **Then** all my tasks are still visible (persisted in Neon DB)
3. **Given** I have a task, **When** I click the checkbox, **Then** the task is marked complete with visual feedback
4. **Given** I have a completed task, **When** I click edit and change the title, **Then** the task updates immediately in the database

---

### User Story 2 - Advanced Task Organization (Priority: P2)

As a user, I want to organize my tasks with priorities and tags, and quickly find tasks using search and filters, so I can manage complex task lists efficiently.

**Why this priority**: Enhances usability significantly, especially for users with many tasks. Required for Phase II completion.

**Independent Test**: Can assign priorities (high/medium/low) and tags to tasks. Can search by text, filter by status/priority/tags, and sort by different criteria.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I set priority to "High" and add tags "work, urgent", **Then** the task shows with a red priority badge and both tags
2. **Given** I have 20 tasks with different priorities, **When** I filter by "High priority", **Then** only high-priority tasks are displayed
3. **Given** I have tasks with various titles, **When** I type "meeting" in the search box, **Then** only tasks containing "meeting" are shown
4. **Given** I have tasks, **When** I sort by priority, **Then** tasks are ordered: High → Medium → Low

---

### User Story 3 - Multi-language Voice Commands (Priority: P3 - Bonus)

As a user, I want to add and manage tasks using voice commands in my native language (English, Urdu, Arabic, Spanish, French, or German), so I can quickly capture tasks hands-free regardless of my language preference.

**Why this priority**: Bonus feature for extra credit. Demonstrates Physical AI integration and comprehensive multi-language support with 6 languages.

**Independent Test**: Can speak commands in any of the 6 supported languages and the system understands and creates tasks. Language auto-detection works correctly.

**Acceptance Scenarios**:

1. **Given** I am on the dashboard, **When** I click the microphone icon and say "Add task call doctor" (English), **Then** a new task "call doctor" is created
2. **Given** I switch to Urdu, **When** I say "نیا کام شامل کریں خریداری" (Add task shopping), **Then** a task "shopping" is created
3. **Given** I switch to Arabic, **When** I say "أضف مهمة اجتماع" (Add task meeting), **Then** a task "meeting" is created
4. **Given** I switch to Spanish, **When** I say "Agregar tarea compras" (Add task shopping), **Then** the task is created
5. **Given** I switch to French, **When** I say "Ajouter tâche réunion" (Add task meeting), **Then** the task is created
6. **Given** I switch to German, **When** I say "Aufgabe hinzufügen Einkaufen" (Add task shopping), **Then** the task is created
7. **Given** voice recognition is active in any language, **When** I say "Complete task 5", **Then** task with ID 5 is marked complete

---

### User Story 4 - Multi-language AI Assistant with Claude Code (Priority: P3 - Bonus)

As a user, I want an AI chatbot assistant powered by Claude that can help me manage tasks conversationally in my preferred language, understand context, and provide intelligent suggestions.

**Why this priority**: Bonus feature demonstrating reusable intelligence via Claude Code Subagents and comprehensive multi-language AI support.

**Independent Test**: Can type natural language commands in any of the 6 supported languages and get intelligent responses in the same language.

**Acceptance Scenarios**:

1. **Given** I open the AI chat panel in English, **When** I type "What tasks do I have for today?", **Then** the AI lists all tasks in English and highlights high-priority ones
2. **Given** I have multiple high-priority tasks, **When** I ask "What should I focus on?" in any language, **Then** the AI suggests tasks based on priority and context in that language
3. **Given** I type "Add a task to prepare presentation" in English, **Then** the AI creates a task with title "Prepare presentation"
4. **Given** I ask in Urdu "میرے کام دکھائیں" (Show my tasks), **Then** the AI responds in Urdu with the task list
5. **Given** I ask in Arabic "ما هي المهام العاجلة؟" (What are the urgent tasks?), **Then** the AI responds in Arabic
6. **Given** I ask in Spanish "¿Cuáles son mis tareas?" (What are my tasks?), **Then** the AI responds in Spanish
7. **Given** I ask in French "Quelles sont mes tâches?" (What are my tasks?), **Then** the AI responds in French
8. **Given** I ask in German "Was sind meine Aufgaben?" (What are my tasks?), **Then** the AI responds in German

---

### User Story 5 - Interactive Task Management (Priority: P2)

As a user, I want to interact with my tasks naturally through drag-and-drop reordering, bulk actions, and inline editing, so I can manage large task lists efficiently without repetitive actions.

**Why this priority**: Dramatically improves UX for power users and makes the app feel modern and responsive. Essential for Phase II completion.

**Independent Test**: Can drag tasks to reorder them, select multiple tasks for bulk operations, edit task titles directly in the list without modals, and undo mistakes.

**Acceptance Scenarios**:

1. **Given** I have 10 tasks, **When** I drag a task from position 5 to position 2, **Then** the task moves and the new order persists in the database
2. **Given** I have 20 tasks, **When** I select checkboxes for 5 tasks and click "Bulk Complete", **Then** all 5 tasks are marked complete simultaneously
3. **Given** I see a task in the list, **When** I double-click the title, **Then** I can edit it inline without opening a modal
4. **Given** I accidentally delete a task, **When** I press Ctrl+Z, **Then** the task is restored
5. **Given** I select 10 tasks, **When** I click "Bulk Add Tag" and choose "urgent", **Then** all 10 tasks get the "urgent" tag
6. **Given** I press Ctrl+N anywhere, **When** the shortcut triggers, **Then** the new task form opens with focus on the title field
7. **Given** I have tasks selected, **When** I press Delete key, **Then** a confirmation dialog appears to bulk delete

---

### User Story 6 - Rich Task Details (Priority: P2)

As a user, I want to add subtasks, detailed notes, and file attachments to my tasks, so I can break down complex projects and keep all related information in one place.

**Why this priority**: Transforms simple todos into a comprehensive task management system. Critical for professional use cases.

**Independent Test**: Can create subtasks within tasks, add formatted notes, attach documents/images, and view all details in an organized panel.

**Acceptance Scenarios**:

1. **Given** I have a task "Launch website", **When** I add subtasks "Design mockup", "Write copy", "Deploy", **Then** all subtasks appear as a checklist under the parent task
2. **Given** I have a task with 5 subtasks, **When** I complete 3 subtasks, **Then** the task shows progress "3/5 (60%)" visually
3. **Given** I open a task detail panel, **When** I add a note "Meeting notes: Client wants blue theme", **Then** the note is saved with timestamp
4. **Given** I have a task, **When** I attach a PDF file "requirements.pdf", **Then** the file is uploaded and appears as a link in the task
5. **Given** I attach an image with text (screenshot), **When** the AI OCR processes it, **Then** extracted text is added to task notes automatically
6. **Given** I have multiple notes on a task, **When** I view them, **Then** they appear chronologically with timestamps and edit history

---

### User Story 7 - UX Polish & Accessibility (Priority: P2)

As a user, I want a polished, accessible interface with dark mode, keyboard shortcuts, and smooth interactions, so I can use the app comfortably for extended periods in any environment.

**Why this priority**: Professional polish differentiates a great product from a good one. Essential for user retention.

**Independent Test**: Can toggle dark mode, navigate entirely with keyboard, see smooth animations, and use the app comfortably at night.

**Acceptance Scenarios**:

1. **Given** I'm using the app at night, **When** I toggle dark mode, **Then** all colors switch to a dark theme with proper contrast (WCAG AA compliant)
2. **Given** I press "/" key, **When** the shortcut triggers, **Then** focus moves to the search box
3. **Given** I'm in the task list, **When** I press "j" and "k" keys, **Then** I navigate down and up through tasks (vim-style)
4. **Given** I perform any action, **When** the UI updates, **Then** smooth animations provide visual feedback (fade-in, slide, etc.)
5. **Given** I make changes, **When** I press Ctrl+Z / Ctrl+Y, **Then** undo/redo works for all actions (delete, edit, complete, tag, etc.)
6. **Given** I use the app, **When** I check accessibility, **Then** all interactive elements have ARIA labels and keyboard focus indicators

**Keyboard Shortcuts**:
- `Ctrl+N` / `Cmd+N`: New task
- `/`: Focus search
- `Escape`: Close modals/dialogs
- `Ctrl+Z` / `Cmd+Z`: Undo
- `Ctrl+Y` / `Cmd+Y`: Redo
- `j` / `k`: Navigate tasks (down/up)
- `Space`: Mark task complete/incomplete
- `Delete`: Delete selected tasks
- `Ctrl+A` / `Cmd+A`: Select all tasks
- `?`: Show keyboard shortcuts help

**3D Effects & Visual Delight**:
- Card elevation with 3D transforms on hover
- Perspective transforms for task cards
- Glassmorphism effects (frosted glass backgrounds)
- Depth layers with parallax scrolling
- 3D flip animations for task completion
- Floating action button with 3D depth
- Smooth spring animations (react-spring)
- Particle effects on task completion
- Neon glow effects in dark mode
- Morphing shapes and gradients

---

### User Story 8 - Data Management & Analytics (Priority: P2)

As a user, I want to export/import my tasks, create reusable templates, view productivity analytics, and see activity history, so I can analyze my patterns and integrate with other tools.

**Why this priority**: Power users need data portability and insights. Demonstrates professional-grade features.

**Independent Test**: Can export tasks to CSV/JSON, import from other tools, save templates for recurring task types, view analytics dashboard, and see complete activity history.

**Acceptance Scenarios**:

1. **Given** I have 50 tasks, **When** I click "Export to CSV", **Then** a CSV file downloads with all task data (id, title, description, priority, tags, dates)
2. **Given** I have a CSV from another tool, **When** I import it, **Then** all valid tasks are created with proper mapping (title, description, etc.)
3. **Given** I create a task "Weekly team meeting" with tags "work, recurring", **When** I save it as a template, **Then** I can later create new tasks from this template in one click
4. **Given** I open the analytics dashboard, **When** I view it, **Then** I see charts showing: tasks completed over time, completion rate by priority, most used tags, average tasks per day
5. **Given** I view a task's activity history, **When** I check it, **Then** I see: "Created Dec 7 2pm", "Priority changed to High Dec 8 10am", "Completed Dec 9 3pm"
6. **Given** I view my personal productivity insights, **When** I check the dashboard, **Then** I see: "You complete most tasks on Mondays", "Peak productivity: 2pm-4pm", "Average completion time: 2.3 days"

**Analytics Metrics**:
- Total tasks (all time, this week, this month)
- Completion rate (% of tasks completed)
- Tasks by priority breakdown (pie chart)
- Tasks by tag (bar chart)
- Completion timeline (line chart)
- Average time to complete
- Most productive days/hours
- Overdue tasks trend

---

### User Story 9 - AI-Powered Intelligence (Priority: P3 - Bonus)

As a user, I want AI to help me manage tasks intelligently through automatic categorization, task breakdown, smart search, productivity insights, and context-aware suggestions, so I can work smarter with minimal effort.

**Why this priority**: Showcases cutting-edge AI capabilities and reusable Claude Code skills. Differentiates the app significantly.

**Independent Test**: AI automatically suggests priorities/tags, breaks down complex tasks, provides semantic search, analyzes productivity patterns, and offers proactive suggestions.

**Acceptance Scenarios**:

1. **Given** I create a task "Prepare Q4 presentation for board meeting next week", **When** AI analyzes it, **Then** it suggests priority "High", tags "work, presentation, urgent", and auto-detects it's complex
2. **Given** I have a complex task, **When** I click "AI Breakdown", **Then** Claude breaks it into 5-7 actionable subtasks with time estimates
3. **Given** I search for "urgent work items", **When** AI processes the query, **Then** semantic search returns high-priority work tasks even if they don't contain those exact words
4. **Given** I type "Buy milk tomorrow at 3pm", **When** AI parses it, **Then** it creates task "Buy milk" with auto-detected metadata (future: due date if Phase III)
5. **Given** I use the app daily, **When** I open the AI insights panel, **Then** AI says: "You tend to procrastinate on 'documentation' tasks. Consider breaking them into smaller pieces."
6. **Given** I'm working on task "Design homepage", **When** AI provides suggestions, **Then** it recommends related tasks like "Get design feedback" or "Export assets"
7. **Given** I have 3 unrelated tasks, **When** AI analyzes them, **Then** it suggests: "These tasks could be grouped under project 'Website Redesign'"

**AI Features**:
- **Auto-categorization**: Suggests priority/tags based on title/description
- **Task Breakdown**: Splits complex tasks into subtasks automatically
- **Smart Search**: Semantic search understands intent, not just keywords
- **Natural Language Parser**: Extracts metadata from freeform text
- **Productivity Insights**: Analyzes patterns and suggests improvements
- **Context-Aware Suggestions**: Recommends next tasks or related actions
- **Task Summarization**: Condenses long descriptions into key points
- **Dependency Detection**: Identifies when tasks depend on each other

---

### User Story 10 - Email Integration & OCR (Priority: P3 - Bonus)

As a user, I want to email tasks to others, forward emails to create tasks automatically, and extract text from uploaded documents via OCR, so I can integrate my email workflow seamlessly.

**Why this priority**: Bridges the gap between email and task management. Highly practical for professional users.

**Independent Test**: Can send tasks via email, forward emails to a special address to create tasks, and upload images/PDFs that get OCR-processed automatically.

**Acceptance Scenarios**:

1. **Given** I have a task "Review contract by Friday", **When** I click "Email Task" and enter "colleague@example.com", **Then** an email is sent with task details (title, description, priority, subtasks)
2. **Given** I receive an email "Action: Prepare budget report", **When** I forward it to "tasks@my-todo-app.com", **Then** a task is created with the email subject as title and body as description
3. **Given** I attach a scanned receipt (image), **When** AI OCR processes it, **Then** extracted text like "Total: $45.99, Date: Dec 7" is added to task notes
4. **Given** I upload a PDF with meeting notes, **When** OCR extracts text, **Then** key action items are detected and suggested as subtasks
5. **Given** I click "Share Task" on a task, **When** I select "Copy Email Link", **Then** a shareable link is copied that opens the task when clicked
6. **Given** I have tasks with email integration, **When** I reply to a task email, **Then** my reply is added as a comment/note on the task

**Email Features**:
- Send task via email (formatted, includes all details)
- Email-to-task (forward emails to create tasks)
- OCR for attachments (extract text from images/PDFs)
- Email notifications for task updates (optional)
- Shareable email links for tasks
- Reply-to-comment integration

---

### User Story 11 - Daily Focus & AI Task Help (Priority: P2)

As a user, I want a distraction-free focus mode to see only today's tasks and get AI assistance to understand and complete my tasks better, so I can stay productive and get intelligent help when needed.

**Why this priority**: Modern productivity apps need focus modes. AI task help makes the app feel intelligent and helpful. Both are simple additions with high user value.

**Independent Test**: Can switch to focus mode to see filtered tasks, can ask AI for help on any task (explanation, steps, alternatives).

**Acceptance Scenarios**:

1. **Given** I have 50 tasks, **When** I click "Focus Mode" or press Ctrl+F, **Then** I see only tasks I need to work on today (not completed, high/medium priority)
2. **Given** I'm in focus mode, **When** I view the interface, **Then** it shows a clean, minimal layout with no distractions (no sidebar, no analytics, just tasks)
3. **Given** I have a task "Build authentication system", **When** I right-click and select "AI Help → Explain this task", **Then** AI provides a simple explanation in 2-3 sentences
4. **Given** I have a complex task, **When** I select "AI Help → Give me steps", **Then** AI breaks it down into 5-7 actionable steps
5. **Given** I have a task "Design homepage", **When** I select "AI Help → Suggest alternatives", **Then** AI suggests 3-4 different approaches with pros/cons
6. **Given** I have a task, **When** I select "AI Help → Best time to do this", **Then** AI analyzes my productivity patterns and suggests optimal time
7. **Given** I'm in focus mode, **When** I enable Pomodoro timer (optional), **Then** timer starts at 25 minutes and alerts me when done

**Focus Mode Features**:
- Keyboard shortcut: Ctrl+F / Cmd+F
- Clean minimal UI (no sidebar, header only)
- Shows only: incomplete tasks with high/medium priority
- Optional Pomodoro timer (25min work, 5min break)
- Task count: "3 tasks in focus"
- Exit focus mode: Esc key or "Exit Focus" button

**AI Task Help Features**:
- Right-click context menu on any task
- AI options:
  - 🤖 Explain this task (simple words)
  - 🤖 Give me steps to complete
  - 🤖 Suggest alternatives
  - 🤖 Best time to do this
- Response appears in a popover/modal
- Responses cached to save API costs
- Works in all 6 languages (EN, UR, AR, ES, FR, DE)

---

### Edge Cases

**Existing Edge Cases:**
- What happens when no internet connection? → Show offline message, queue actions for when back online
- How does system handle very long task titles (>200 chars)? → Reject with validation error
- What if voice recognition fails or misunderstands? → Show transcription for user to confirm/edit before saving
- How to handle empty search results? → Show helpful empty state with suggestions
- What if database connection fails? → Show error message, retry logic with exponential backoff
- How does AI handle ambiguous commands? → Ask clarifying questions before acting
- What if user speaks mixed English/Urdu? → Detect language per phrase, handle gracefully

**New Edge Cases (Interactive Features):**
- What if user drags task but drops in invalid location? → Snap back to original position with visual feedback
- What if bulk action fails for some tasks? → Show partial success message ("5/10 tasks completed, 5 failed")
- What if undo history gets too long? → Limit to last 50 actions, show "Undo limit reached"
- What if file attachment exceeds size limit? → Reject with error "File too large (max 10MB)"
- What if OCR fails to extract text from image? → Add attachment without text, show warning
- What if email sending fails? → Queue for retry, show notification
- What if exported CSV has special characters? → Properly escape CSV fields, use UTF-8 encoding
- What if analytics has no data (new user)? → Show empty state with helpful onboarding tips
- What if keyboard shortcut conflicts with browser? → Document conflicts, allow customization
- What if dark mode images don't have proper contrast? → Provide theme-aware image variants

## Requirements

### Functional Requirements - Core (P1)

- **FR-001**: System MUST provide a web-based UI accessible from modern browsers (Chrome, Firefox, Safari, Edge)
- **FR-002**: System MUST persist all task data in Neon DB (PostgreSQL) with immediate consistency
- **FR-003**: System MUST provide RESTful API with endpoints for all CRUD operations
- **FR-004**: Users MUST be able to create tasks with title (required, 1-200 chars) and description (optional, max 2000 chars)
- **FR-005**: System MUST display all tasks in a responsive list view (mobile + desktop)
- **FR-006**: Users MUST be able to update task title and description
- **FR-007**: Users MUST be able to delete tasks with confirmation dialog
- **FR-008**: Users MUST be able to mark tasks complete/incomplete with visual feedback
- **FR-009**: System MUST assign unique sequential IDs to tasks
- **FR-010**: System MUST record created_at and updated_at timestamps in ISO 8601 format

### Functional Requirements - Enhanced (P2)

- **FR-011**: Users MUST be able to assign priority levels (high, medium, low) to tasks
- **FR-012**: Users MUST be able to add multiple tags to categorize tasks
- **FR-013**: System MUST provide real-time search across task titles and descriptions
- **FR-014**: System MUST allow filtering by completion status, priority, and tags
- **FR-015**: System MUST support sorting by: created_at, updated_at, priority, title
- **FR-016**: System MUST display visual priority indicators (colors/badges)
- **FR-017**: System MUST handle tag management (add, remove, autocomplete)

### Functional Requirements - Interactive Features (P2)

- **FR-018**: Users MUST be able to drag and drop tasks to reorder them with persistence
- **FR-019**: System MUST support bulk selection via checkboxes for multiple tasks
- **FR-020**: Users MUST be able to perform bulk actions (complete, delete, tag, priority) on selected tasks
- **FR-021**: Users MUST be able to edit task titles inline (double-click) without modals
- **FR-022**: System MUST implement undo/redo functionality for all destructive actions
- **FR-023**: System MUST support keyboard shortcuts for common actions (create, search, navigate, etc.)
- **FR-024**: System MUST track action history for undo stack (last 50 actions)

### Functional Requirements - Rich Task Details (P2)

- **FR-025**: Users MUST be able to create subtasks within parent tasks
- **FR-026**: System MUST display subtask progress (e.g., "3/5 completed - 60%")
- **FR-027**: Users MUST be able to add timestamped notes to tasks
- **FR-028**: Users MUST be able to attach files (PDF, images, documents) up to 10MB each
- **FR-029**: System MUST support OCR for extracting text from image attachments
- **FR-030**: System MUST display attachment previews and download links

### Functional Requirements - UX Polish (P2)

- **FR-031**: System MUST support dark mode toggle with WCAG AA contrast compliance
- **FR-032**: System MUST persist theme preference (light/dark) in localStorage
- **FR-033**: UI MUST provide smooth animations for state changes (200-300ms)
- **FR-034**: System MUST implement keyboard navigation (j/k for up/down, / for search)
- **FR-035**: All interactive elements MUST have ARIA labels and focus indicators
- **FR-036**: System MUST display keyboard shortcut help modal (? key)

### Functional Requirements - Data Management (P2)

- **FR-037**: Users MUST be able to export tasks to CSV format with all fields
- **FR-038**: Users MUST be able to export tasks to JSON format
- **FR-039**: Users MUST be able to import tasks from CSV/JSON with validation
- **FR-040**: Users MUST be able to save tasks as reusable templates
- **FR-041**: Users MUST be able to create new tasks from templates
- **FR-042**: System MUST display analytics dashboard with charts (completion rate, tasks by priority, timeline)
- **FR-043**: System MUST track activity history for each task (created, modified, completed timestamps)
- **FR-044**: System MUST display productivity insights (most productive days, average completion time)

### Functional Requirements - Focus Mode & AI Help (P2)

- **FR-045**: System MUST provide a focus mode showing only high/medium priority incomplete tasks
- **FR-046**: Focus mode MUST be accessible via keyboard shortcut (Ctrl+F / Cmd+F)
- **FR-047**: Focus mode MUST display minimal UI (no sidebar, no distractions)
- **FR-048**: Focus mode MUST show task count (e.g., "3 tasks in focus")
- **FR-049**: System MUST provide optional Pomodoro timer in focus mode (25min work, 5min break)
- **FR-050**: Users MUST be able to request AI help on any task via context menu
- **FR-051**: AI MUST explain tasks in simple language (2-3 sentences)
- **FR-052**: AI MUST provide step-by-step breakdown for task completion (5-7 steps)
- **FR-053**: AI MUST suggest alternative approaches with pros/cons
- **FR-054**: AI MUST suggest optimal time to complete task based on user patterns
- **FR-055**: AI help responses MUST be cached to optimize API costs
- **FR-056**: AI help MUST work in all 6 supported languages

### Functional Requirements - Bonus Features (P3)

- **FR-057**: System MUST support voice input for task creation and commands
- **FR-058**: System MUST support voice commands in 6 languages (English, Urdu, Arabic, Spanish, French, German)
- **FR-059**: System MUST integrate Claude AI chatbot for conversational task management
- **FR-060**: AI chatbot MUST understand natural language commands in all 6 supported languages
- **FR-061**: AI chatbot MUST provide intelligent task suggestions based on context
- **FR-062**: System MUST implement Claude Code Subagents for reusable intelligence patterns
- **FR-063**: System MUST use Agent Skills for cloud-native blueprints
- **FR-064**: AI MUST auto-suggest priorities and tags based on task content
- **FR-065**: AI MUST break down complex tasks into subtasks automatically
- **FR-066**: System MUST implement semantic search (understands intent, not just keywords)
- **FR-067**: AI MUST parse natural language input to extract metadata
- **FR-068**: System MUST analyze user patterns and provide productivity insights
- **FR-069**: AI MUST suggest related or next tasks based on context
- **FR-070**: Users MUST be able to email tasks to recipients
- **FR-071**: System MUST support email-to-task via forwarding to special address
- **FR-072**: System MUST use OCR to extract text from PDF attachments

### Non-Functional Requirements

- **NFR-001**: API response time MUST be < 500ms for 95th percentile
- **NFR-002**: UI MUST be responsive and usable on mobile devices (320px+)
- **NFR-003**: System MUST handle at least 100 concurrent users without degradation
- **NFR-004**: System MUST validate all inputs with clear error messages
- **NFR-005**: Voice recognition accuracy MUST be > 80% for common commands
- **NFR-006**: AI responses MUST be returned within 3 seconds

### Key Entities

- **Task**: Represents a todo item with title, description, completion status, priority (high/medium/low), tags (array), display_order, created_at, updated_at timestamps
- **Subtask**: Child task within a parent task, has title, completed status, display_order
- **Note**: Timestamped text note attached to a task with created_at, updated_at
- **Attachment**: File (PDF, image, doc) attached to task with filename, url, size, mime_type, ocr_text
- **Template**: Saved task configuration for quick creation (title, description, priority, tags, subtasks)
- **ActivityLog**: Audit trail for task changes (action_type, field_changed, old_value, new_value, timestamp)
- **Priority**: Enum (high, medium, low) with visual representations (colors, badges)
- **Tag**: String label for categorization, can be reused across tasks, supports autocomplete
- **VoiceCommand**: Represents transcribed voice input with detected language and intent
- **AIConversation**: Chat history between user and Claude assistant for context
- **UndoAction**: Reversible action stored in undo stack (action_type, data, timestamp)

## Success Criteria

### Measurable Outcomes - Core

- **SC-001**: Users can complete all 5 CRUD operations via web UI successfully
- **SC-002**: Data persists in Neon DB and survives app restarts (100% reliability)
- **SC-003**: All API endpoints respond within 500ms under normal load
- **SC-004**: UI is fully responsive on devices from 320px to 1920px width
- **SC-005**: System handles 100+ tasks without performance degradation

### Measurable Outcomes - Enhanced

- **SC-006**: Search returns results within 200ms as user types
- **SC-007**: Filters and sorts update UI within 100ms
- **SC-008**: Users can assign priorities and tags to tasks in < 5 seconds
- **SC-009**: Tag autocomplete suggests existing tags after typing 2 characters

### Measurable Outcomes - Bonus

- **SC-010**: Voice recognition successfully transcribes commands with >80% accuracy
- **SC-011**: AI chatbot responds to task queries within 3 seconds
- **SC-012**: All 6 languages (English, Urdu, Arabic, Spanish, French, German) correctly handle task creation and queries
- **SC-013**: Language auto-detection works with >90% accuracy
- **SC-014**: RTL languages (Arabic, Urdu) display correctly in UI
- **SC-015**: Claude Code Subagents demonstrate reusable intelligence patterns (at least 2 custom skills)

## Technical Architecture

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.13+)
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: Neon DB (Serverless PostgreSQL)
- **AI Integration**: Anthropic Claude API
- **Speech-to-Text**: Web Speech API (browser) + OpenAI Whisper (fallback)
- **Server**: Uvicorn (ASGI)

#### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui or custom
- **State**: React hooks + SWR/TanStack Query
- **Voice**: Web Speech API
- **AI Chat**: Custom chat UI + Claude API

#### Infrastructure
- **Database**: Neon DB (cloud PostgreSQL)
- **Deployment**: Vercel (frontend) + Railway/Render (backend)
- **Environment**: Docker containers (optional)

### Data Model

```typescript
// Core Task Entity (Extended)
interface Task {
  id: number;                    // Auto-increment primary key
  title: string;                 // Max 200 chars, required
  description: string;           // Max 2000 chars, optional
  completed: boolean;            // Default false
  priority: 'high' | 'medium' | 'low';  // Default 'medium'
  tags: string[];                // Array of tag strings
  display_order: number;         // For drag-drop ordering, default auto-increment
  is_template: boolean;          // Flag for template tasks, default false
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp

  // Relations (populated on request)
  subtasks?: Subtask[];          // Array of child subtasks
  notes?: Note[];                // Array of notes
  attachments?: Attachment[];    // Array of file attachments
  activity_logs?: ActivityLog[]; // Audit trail
}

// Subtask Entity
interface Subtask {
  id: number;
  task_id: number;               // Foreign key to parent task
  title: string;                 // Max 200 chars, required
  completed: boolean;            // Default false
  display_order: number;         // Order within parent task
  created_at: string;
  updated_at: string;
}

// Note Entity
interface Note {
  id: number;
  task_id: number;               // Foreign key to task
  content: string;               // Max 5000 chars, required
  created_at: string;
  updated_at: string;
}

// Attachment Entity
interface Attachment {
  id: number;
  task_id: number;               // Foreign key to task
  filename: string;              // Original filename
  file_url: string;              // S3/storage URL
  file_size: number;             // Size in bytes (max 10MB)
  mime_type: string;             // e.g., "application/pdf", "image/png"
  ocr_text: string | null;       // Extracted text via OCR (for images/PDFs)
  created_at: string;
}

// Template Entity
interface Template {
  id: number;
  name: string;                  // Template name (e.g., "Weekly Review")
  title: string;                 // Task title
  description: string;           // Task description
  priority: 'high' | 'medium' | 'low';
  tags: string[];
  subtasks: string[];            // Array of subtask titles
  created_at: string;
  updated_at: string;
}

// Activity Log Entity
interface ActivityLog {
  id: number;
  task_id: number;               // Foreign key to task
  action_type: 'created' | 'updated' | 'completed' | 'deleted' | 'tagged' | 'priority_changed';
  field_changed: string | null;  // e.g., "title", "priority", "tags"
  old_value: string | null;      // Previous value (JSON string)
  new_value: string | null;      // New value (JSON string)
  created_at: string;
}

// Undo Action (Client-side only, not persisted)
interface UndoAction {
  id: string;                    // UUID
  action_type: 'create' | 'update' | 'delete' | 'complete' | 'bulk_action';
  data: any;                     // Snapshot of affected data for reversal
  timestamp: number;             // Unix timestamp
}

// Voice Command Entity
interface VoiceCommand {
  id: number;
  transcript: string;            // What was said
  language: 'en' | 'ur' | 'ar' | 'es' | 'fr' | 'de';  // Detected language
  intent: string;                // Parsed intent (create_task, complete_task, etc.)
  confidence: number;            // 0-1 confidence score
  created_at: string;
}

// Chat Message Entity
interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  language: 'en' | 'ur' | 'ar' | 'es' | 'fr' | 'de';  // Message language
  created_at: string;
}

// Analytics Response (Computed, not stored)
interface AnalyticsSummary {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  completion_rate: number;       // Percentage
  tasks_by_priority: {
    high: number;
    medium: number;
    low: number;
  };
  tasks_by_tag: Record<string, number>;  // { "work": 15, "personal": 8 }
  completion_timeline: {
    date: string;                // YYYY-MM-DD
    completed: number;
  }[];
  avg_completion_time_hours: number;
  most_productive_day: string;   // "Monday", "Tuesday", etc.
  most_productive_hour: number;  // 0-23
}
```

### API Endpoints

```
Base URL: http://localhost:8000/api/v1

# Task Management (Enhanced)
GET    /tasks                      # List all tasks with query params
GET    /tasks/{id}                 # Get single task with relations (subtasks, notes, attachments)
POST   /tasks                      # Create new task
PUT    /tasks/{id}                 # Update task (full)
PATCH  /tasks/{id}                 # Partial update
DELETE /tasks/{id}                 # Delete task (soft delete, logged in activity)
PATCH  /tasks/reorder              # Bulk reorder tasks (drag-drop) - body: [{ id, display_order }]

# Bulk Actions
POST   /tasks/bulk/complete        # Bulk complete - body: { task_ids: number[] }
POST   /tasks/bulk/delete          # Bulk delete - body: { task_ids: number[] }
POST   /tasks/bulk/tag             # Bulk add tag - body: { task_ids: number[], tag: string }
POST   /tasks/bulk/priority        # Bulk set priority - body: { task_ids: number[], priority: string }

# Subtasks
GET    /tasks/{task_id}/subtasks   # List subtasks for a task
POST   /tasks/{task_id}/subtasks   # Create subtask
PATCH  /subtasks/{id}               # Update subtask (title, completed)
DELETE /subtasks/{id}               # Delete subtask
PATCH  /subtasks/reorder            # Reorder subtasks - body: [{ id, display_order }]

# Notes
GET    /tasks/{task_id}/notes      # List notes for a task
POST   /tasks/{task_id}/notes      # Create note
PATCH  /notes/{id}                  # Update note content
DELETE /notes/{id}                  # Delete note

# Attachments
GET    /tasks/{task_id}/attachments # List attachments for a task
POST   /tasks/{task_id}/attachments # Upload file (multipart/form-data, max 10MB)
GET    /attachments/{id}/download   # Download attachment
DELETE /attachments/{id}             # Delete attachment
POST   /attachments/{id}/ocr        # Trigger OCR on image/PDF attachment

# Templates
GET    /templates                   # List all templates
GET    /templates/{id}              # Get single template
POST   /templates                   # Create template from task or custom
POST   /templates/{id}/instantiate  # Create task from template
DELETE /templates/{id}               # Delete template

# Analytics & Insights
GET    /analytics/summary           # Get overall analytics (completion rate, tasks by priority, etc.)
GET    /analytics/timeline          # Get completion timeline (last 30 days)
GET    /analytics/productivity      # Get productivity insights (best day, hour, avg completion time)
GET    /tasks/{id}/activity         # Get activity log for a task

# Data Management
GET    /export/csv                  # Export all tasks to CSV
GET    /export/json                 # Export all tasks to JSON
POST   /import/csv                  # Import tasks from CSV (multipart/form-data)
POST   /import/json                 # Import tasks from JSON

# Voice Features
POST   /voice/transcribe            # Transcribe voice to text
POST   /voice/command               # Execute voice command

# AI Chatbot (Enhanced)
POST   /ai/chat                     # Send message to AI
GET    /ai/history                  # Get chat history
DELETE /ai/history                  # Clear chat history
POST   /ai/suggest-tags             # AI suggests tags for task - body: { title, description }
POST   /ai/suggest-priority         # AI suggests priority - body: { title, description }
POST   /ai/breakdown                # AI breaks down task into subtasks - body: { task_id }
POST   /ai/parse-nl                 # Parse natural language input - body: { text }
POST   /ai/semantic-search          # Semantic search - body: { query }
GET    /ai/insights                 # Get AI productivity insights

# Email Integration
POST   /email/send-task             # Send task via email - body: { task_id, recipient_email }
POST   /email/parse                 # Parse email to create task - body: { email_subject, email_body }
GET    /email/inbox-address         # Get unique inbox address for forwarding emails

# Focus Mode & AI Help
GET    /focus/tasks                 # Get tasks for focus mode (high/medium priority, incomplete)
POST   /ai/help/explain             # AI explains task - body: { task_id, language }
POST   /ai/help/steps               # AI provides completion steps - body: { task_id, language }
POST   /ai/help/alternatives        # AI suggests alternatives - body: { task_id, language }
POST   /ai/help/best-time           # AI suggests best time - body: { task_id, user_history }

Query Parameters for GET /tasks:
- search: string (search in title/description/notes)
- completed: boolean
- priority: high|medium|low
- tags: comma-separated string
- sort: created_at|updated_at|priority|title|display_order
- order: asc|desc
- limit: number (pagination, default 50)
- offset: number (pagination, default 0)
- include: comma-separated (subtasks,notes,attachments,activity_logs)
```

### Project Structure

```
physical-ai-todo/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app + CORS
│   │   ├── database.py          # Neon DB connection
│   │   ├── models.py            # SQLModel models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── crud.py              # Database operations
│   │   ├── routes/
│   │   │   ├── tasks.py         # Task CRUD endpoints
│   │   │   ├── voice.py         # Voice command endpoints
│   │   │   └── chat.py          # AI chatbot endpoints
│   │   ├── services/
│   │   │   ├── voice_service.py # Speech processing
│   │   │   └── ai_service.py    # Claude integration
│   │   └── skills/              # Claude Code Skills
│   │       ├── task_analyzer.py
│   │       └── urdu_translator.py
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main dashboard
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── TaskList.tsx
│   │   ├── TaskForm.tsx
│   │   ├── TaskItem.tsx
│   │   ├── FilterBar.tsx
│   │   ├── PriorityBadge.tsx
│   │   ├── VoiceInput.tsx       # Voice command button
│   │   ├── ChatBot.tsx          # AI chat panel
│   │   └── LanguageToggle.tsx   # English/Urdu switch
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   ├── types.ts             # TypeScript types
│   │   └── voice.ts             # Voice utilities
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env.local
│
├── src/todo/                     # Phase I code (reference)
├── specs/
│   └── 001-002-phase-2/
│       ├── spec.md              # This file
│       ├── plan.md              # Implementation plan
│       └── tasks.md             # Task breakdown
├── .claude/
│   └── skills/                  # Claude Code Skills
│       ├── task-analyzer.md
│       └── urdu-support.md
└── README.md
```

## Implementation Timeline (5 Days + Bonus)

### Day 1 (Dec 7): Planning & Backend Setup ✓
- [x] Create Phase II specification
- [ ] Create implementation plan
- [ ] Set up Neon DB account and database
- [ ] Initialize FastAPI project structure
- [ ] Create SQLModel models with priority and tags
- [ ] Set up database connection and test
- [ ] Implement basic CRUD endpoints

### Day 2 (Dec 8): Complete Backend API
- [ ] Add search, filter, sort logic to GET /tasks
- [ ] Implement validation for all endpoints
- [ ] Enable CORS for frontend
- [ ] Test all API endpoints with Postman
- [ ] Add error handling and logging
- [ ] Document API with OpenAPI/Swagger

### Day 3 (Dec 9): Frontend Core
- [ ] Initialize Next.js 14 project with TypeScript
- [ ] Set up Tailwind CSS and component library
- [ ] Create layout and basic routing
- [ ] Build API client functions
- [ ] Implement TaskList and TaskItem components
- [ ] Build TaskForm (create/edit) with priority and tags
- [ ] Connect to backend API and test

### Day 4 (Dec 10): Frontend Enhanced + Voice
- [ ] Implement search, filter, sort UI
- [ ] Add loading states and error handling
- [ ] Make responsive for mobile
- [ ] Polish UI with proper styling
- [ ] Implement voice input button
- [ ] Integrate Web Speech API for voice recognition
- [ ] Test voice commands (English)

### Day 5 (Dec 11): AI Features + Urdu Support
- [ ] Integrate Claude API for chatbot
- [ ] Build chat UI component
- [ ] Implement natural language command parsing
- [ ] Add Urdu language support
- [ ] Create Claude Code Skills for task analysis
- [ ] Test AI chatbot with various queries
- [ ] Add language toggle (English/Urdu)

### Day 6 (Dec 12): Final Polish & Submission
- [ ] End-to-end testing of all features
- [ ] Fix bugs and edge cases
- [ ] Update README with full setup instructions
- [ ] Create demo video showing all features
- [ ] Prepare hackathon submission
- [ ] Deploy to Vercel + Railway (optional)
- [ ] Submit before deadline ⏰

## Out of Scope (Deferred to Phase III or Later)

- ❌ User authentication / multi-user accounts (Phase III)
- ❌ Due dates and calendar integration (Phase III)
- ❌ Reminders and notifications (Phase III)
- ❌ Recurring tasks (Phase III)
- ❌ Real-time multi-user collaboration (Phase V)
- ❌ Mobile native apps (iOS/Android) (Future)
- ❌ Offline-first PWA with service workers (Phase IV)
- ❌ Advanced calendar sync (Google Calendar, Outlook) (Phase III)
- ❌ Team workspaces and permissions (Phase V)
- ❌ Custom webhooks for integrations (Phase V)
- ❌ API rate limiting and quotas (Phase V)
- ❌ Advanced AI features (auto-scheduling, time blocking) (Phase III+)

## Dependencies

### Backend (`requirements.txt`)
```
# Core Framework
fastapi==0.104.1
sqlmodel==0.0.14
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
pydantic==2.5.0

# Database
psycopg2-binary==2.9.9
alembic==1.13.0            # Database migrations

# AI & NLP
anthropic==0.7.8
openai==1.6.1              # For GPT models and Whisper API
langchain==0.1.0           # AI orchestration (optional)

# File Handling & OCR
python-multipart==0.0.6    # File uploads
Pillow==10.1.0             # Image processing
pytesseract==0.3.10        # OCR for images
PyPDF2==3.0.1              # PDF text extraction
pdf2image==1.16.3          # Convert PDF to images for OCR

# Email Integration
python-emails==0.6         # Send emails
mailparser==3.15.0         # Parse incoming emails
sendgrid==6.11.0           # SendGrid email service (optional)

# Data Export/Import
pandas==2.1.4              # CSV/JSON processing

# Utilities
python-slugify==8.0.1      # Generate slugs
httpx==0.26.0              # Async HTTP client
```

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.3",

    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",

    "@anthropic-ai/sdk": "^0.9.1",
    "@tanstack/react-query": "^5.14.2",

    "i18next": "^23.7.0",
    "react-i18next": "^13.5.0",
    "next-i18next": "^15.2.0",

    "@dnd-kit/core": "^6.1.0",
    "@dnd-kit/sortable": "^8.0.0",
    "@dnd-kit/utilities": "^3.2.2",

    "react-dropzone": "^14.2.3",
    "react-markdown": "^9.0.1",
    "recharts": "^2.10.3",

    "framer-motion": "^10.16.16",
    "react-hotkeys-hook": "^4.4.1",

    "date-fns": "^3.0.6",
    "papaparse": "^5.4.1",
    "file-saver": "^2.0.5",

    "lucide-react": "^0.294.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.6",
    "@types/react": "^18.2.46",
    "@types/react-dom": "^18.2.18",
    "@types/papaparse": "^5.3.12",
    "eslint": "^8.56.0",
    "eslint-config-next": "14.0.4"
  }
}
```

### Key Library Purposes

**Backend:**
- `pytesseract` + `pdf2image`: OCR for image/PDF attachments
- `python-emails` / `sendgrid`: Send tasks via email
- `pandas`: CSV/JSON export/import
- `alembic`: Database schema migrations

**Frontend:**
- `@dnd-kit/*`: Drag-and-drop for task reordering
- `react-dropzone`: File upload UI
- `recharts`: Analytics charts
- `framer-motion`: Smooth animations
- `react-hotkeys-hook`: Keyboard shortcuts
- `papaparse`: CSV parsing
- `lucide-react`: Icon library

## Environment Variables

### Backend (`.env`)
```bash
DATABASE_URL=postgresql://user:password@neon-host/dbname
ANTHROPIC_API_KEY=sk-ant-xxxxx
CORS_ORIGINS=http://localhost:3000,https://your-domain.vercel.app
```

### Frontend (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## Bonus Features Overview

### 1. Reusable Intelligence via Claude Code Subagents
- Create custom Agent Skills for task analysis
- Skill 1: Task priority recommender (analyzes title/description to suggest priority)
- Skill 2: Tag suggester (analyzes content to recommend tags)
- Skill 3: Multi-language translator for seamless language switching

### 2. Cloud-Native Blueprints via Agent Skills
- Create blueprint skill for deploying to Vercel + Railway
- Automated setup skill for Neon DB + FastAPI boilerplate
- Infrastructure-as-code templates for easy replication

### 3. Multi-language Support (6 Languages)
- **Supported Languages**: English, Urdu, Arabic, Spanish, French, German
- UI text translation with RTL support (Arabic, Urdu)
- Voice commands in all 6 languages
- AI chatbot responds in user's selected language
- Language auto-detection from voice/text input
- Language switcher in UI with flag icons

### 4. Voice Commands
- Voice-to-text transcription using Web Speech API
- Intelligent command parsing and execution
- Supports actions: add, complete, delete, search, list, filter
- Works across all 6 supported languages
- Confidence scoring for transcription accuracy

## Success Metrics

- ✅ All Phase I features working in web UI
- ✅ All Phase II enhanced features (priority, tags, search, filter, sort)
- ✅ Data persists in Neon DB
- ✅ Responsive design (mobile + desktop)
- ✅ Voice commands working in 6 languages (English, Urdu, Arabic, Spanish, French, German)
- ✅ AI chatbot functional with context awareness
- ✅ At least 2 Claude Code Skills implemented
- ✅ Clean, documented codebase
- ✅ Demo video showcasing all features
- ✅ Deployed and accessible online

## Risk Mitigation

1. **Tight Timeline**: Focus on P1 features first (core CRUD), then P2 (enhancements), then bonus features (voice, AI, multi-language)
2. **Voice API Limitations**: Use Web Speech API (free, browser-based) with potential Whisper API fallback for unsupported languages
3. **Claude API Costs**: Implement caching, limit context size, add rate limiting, use smaller models for simple queries
4. **Multi-language Complexity**:
   - Phase implementation: Start with English, add one language at a time
   - Use i18next or similar library for translations
   - RTL support (Arabic, Urdu): Test early with CSS direction changes
   - Voice recognition: Web Speech API may have varying support across languages
5. **Database Issues**: Test Neon DB connection early on Day 1, have local PostgreSQL backup for development
6. **Deployment Issues**: Test deployment early on Day 4, don't wait until Day 6
7. **Translation Quality**: Use Claude API for dynamic translations, pre-translate UI strings manually for accuracy
