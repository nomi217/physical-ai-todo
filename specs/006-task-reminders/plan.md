# Implementation Plan: Task Reminders and In-App Notifications

**Branch**: `006-task-reminders` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-task-reminders/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature adds task reminders and in-app notifications to the existing To-Do application. Users can set due dates with calendar pickers, choose when to be reminded (via relative offset options: 1 hour, 1 day, 3 days, 5 days, 1 week before, or never), and receive in-app notifications when reminders trigger or tasks become overdue. The implementation uses APScheduler for background reminder checks (every 60 seconds), stores notifications in a new database table, displays them in a dropdown panel from a top-nav bell icon, and includes calendar export functionality (.ics file download) for external calendar integration.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Next.js 14 (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.104+, SQLModel, APScheduler 3.10+, icalendar library
- Frontend: React 18+, Next.js 14, TanStack Query, date-fns or similar datetime library
**Storage**: Neon Serverless PostgreSQL (existing + new `notifications` table, extend `tasks` table)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (cross-browser), deployed on DigitalOcean Kubernetes (DOKS)
**Project Type**: Web (existing backend + frontend structure)
**Performance Goals**:
- Notifications delivered within 1 minute of trigger time (60-second scheduler polling)
- API response < 200ms p95 for notification endpoints
- Calendar export generates .ics file in < 500ms for up to 1000 tasks
**Constraints**:
- No email notifications (email service removed from app)
- No real-time WebSocket (polling-based notification check every 60s)
- Background scheduler must handle server restarts gracefully
- .ics export must be compatible with Google Calendar, Apple Calendar, Outlook
**Scale/Scope**:
- Support 10,000+ concurrent users
- Handle 100,000+ tasks with due dates/reminders
- Notification table may grow large (implement cleanup strategy for old notifications)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development ✅ PASS
- ✅ Specification created via `/sp.specify` (spec.md exists)
- ✅ Clarifications completed via `/sp.clarify` (4 questions answered)
- ✅ User stories defined with Given/When/Then acceptance criteria
- ✅ Functional requirements documented (FR-001 through FR-029)
- ✅ Now proceeding with `/sp.plan` before any implementation

### II. Phase-Correct Evolution ✅ PASS
- ✅ Feature is Phase II extension (building on existing Phase II web app)
- ✅ Extends existing Task model (adds due_date, reminder_offset, reminder_time fields)
- ✅ Adds new Notification table (no breaking changes to existing tables)
- ✅ Backward compatible: Tasks without due dates/reminders continue working
- ✅ Phase II foundations exist: FastAPI backend, Next.js frontend, Neon PostgreSQL, authentication

### III. Authentication and Security First ✅ PASS
- ✅ Uses existing JWT authentication system (no new auth required)
- ✅ All notification endpoints will be protected (user_id from JWT)
- ✅ Input validation via Pydantic for all date/time fields
- ✅ Parameterized SQL queries via SQLModel (SQL injection prevention)
- ✅ CORS already configured for frontend-backend communication

### IV. Test-Driven Quality ⏳ PENDING
- ⏳ Tests to be written during implementation (pytest for backend, Jest for frontend)
- ⏳ Target: 80%+ test coverage
- ⏳ Test scenarios defined in spec (acceptance criteria)
- ⏳ Will verify before marking feature complete

### V. Modern UX and Design Standards ✅ PASS
- ✅ Responsive design (existing framework in place)
- ✅ Dark mode support (existing ThemeContext will apply)
- ✅ Professional UI patterns: calendar picker, dropdown panel, badges
- ✅ Loading states and error messages planned
- ✅ Accessibility: semantic HTML, ARIA labels for notification icon/dropdown

### VI. API-First Architecture ✅ PASS
- ✅ REST API endpoints will be designed before frontend implementation
- ✅ Contract defined in Phase 1 (contracts/ directory)
- ✅ Follows existing API conventions (/api/v1/*)
- ✅ Pydantic validation for request/response schemas
- ✅ Proper HTTP status codes (200, 201, 400, 404, 500)

### VII. Database Design Excellence ✅ PASS
- ✅ New notification table with proper indexing (user_id, task_id, read status, created_at)
- ✅ Extend tasks table with indexed fields (due_date, reminder_time)
- ✅ Timestamps on notification table (created_at)
- ✅ Foreign key constraints (notification → task, notification → user)
- ✅ Alembic migration script will be generated for schema changes

### VIII. Multi-Language and Accessibility ✅ PASS
- ✅ Existing i18n system will be extended (add new translation keys)
- ✅ RTL support already in place for Arabic/Urdu
- ✅ All new UI strings will use translation keys (no hardcoded text)
- ✅ Notification panel will use existing I18nContext
- ✅ ARIA labels for accessibility (bell icon, dropdown, notification items)

**Overall Status**: ✅ PASS - Ready to proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models.py                    # [EXTEND] Add Notification model, extend Task model
│   ├── schemas.py                   # [EXTEND] Add notification schemas, extend task schemas
│   ├── crud.py                      # [EXTEND] Add notification CRUD operations
│   ├── database.py                  # [NO CHANGE] Existing Neon connection
│   ├── main.py                      # [EXTEND] Add scheduler startup, new route includes
│   ├── scheduler.py                 # [NEW] APScheduler setup and reminder check logic
│   ├── routes/
│   │   ├── tasks.py                 # [EXTEND] Add due_date, reminder_offset to create/update
│   │   ├── notifications.py         # [NEW] Notification CRUD endpoints
│   │   └── calendar_export.py       # [NEW] .ics file generation endpoint
│   └── utils/
│       ├── reminder_calculator.py   # [NEW] Calculate reminder_time from due_date + offset
│       └── ics_generator.py         # [NEW] Generate iCalendar format files
├── alembic/
│   └── versions/
│       └── 2025_12_30_xxxx_add_reminders_notifications.py  # [NEW] Migration script
├── requirements.txt                 # [EXTEND] Add APScheduler, icalendar
└── tests/
    ├── test_scheduler.py            # [NEW] Test reminder scheduling logic
    ├── test_notifications.py        # [NEW] Test notification CRUD
    └── test_calendar_export.py      # [NEW] Test .ics generation

frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx                 # [EXTEND] Add notification icon to top nav
│   └── layout.tsx                   # [NO CHANGE] Existing root layout
├── components/
│   ├── TaskForm.tsx                 # [EXTEND] Add due_date picker, reminder offset dropdown
│   ├── TaskItem.tsx                 # [EXTEND] Add due date badge, overdue indicator
│   ├── NotificationDropdown.tsx     # [NEW] Bell icon + dropdown panel
│   ├── NotificationItem.tsx         # [NEW] Individual notification card
│   ├── UpcomingReminders.tsx        # [NEW] Dashboard widget for upcoming reminders
│   └── CalendarExportButton.tsx     # [NEW] Button to download .ics file
├── lib/
│   ├── api.ts                       # [EXTEND] Add notification API calls, calendar export
│   └── types.ts                     # [EXTEND] Add Notification type, extend Task type
├── hooks/
│   └── useNotifications.ts          # [NEW] React Query hook for notifications
└── tests/
    └── components/
        ├── NotificationDropdown.test.tsx  # [NEW] Test notification UI
        └── TaskForm.test.tsx              # [EXTEND] Test due date/reminder fields
```

**Structure Decision**: Web application structure (Option 2). This feature extends the existing Phase II backend (FastAPI) and frontend (Next.js 14) without introducing new top-level directories. All changes are additive (new files) or extensions (existing files with new functionality). No breaking changes to existing code.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All constitution gates passed. No complexity justification needed.
