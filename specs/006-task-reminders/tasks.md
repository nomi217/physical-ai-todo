# Implementation Tasks: Task Reminders and In-App Notifications

**Feature**: 006-task-reminders
**Branch**: `006-task-reminders`
**Date**: 2025-12-30

## Overview

This document breaks down the implementation of task reminders and in-app notifications into actionable tasks organized by user story priority. Each user story phase represents an independently testable increment that delivers value.

**Total Tasks**: 52 tasks
**Estimated Time**: 12-15 hours (distributed across 5 user stories)
**Parallel Opportunities**: 23 parallelizable tasks marked with [P]

---

## Dependencies & Execution Order

### User Story Completion Order

```
Phase 1: Setup (foundational)
  ↓
Phase 2: User Story 1 (P1) - Set Due Date and Reminder
  ↓
Phase 3: User Story 2 (P2) - Receive In-App Notifications (depends on US1 data model)
  ↓
Phase 4: User Story 3 (P3) - View Upcoming Reminders (depends on US1, can run parallel to US2)
  ↓
Phase 5: User Story 4 (P4) - Notification Management (depends on US2)
  ↓
Phase 6: User Story 5 (P5) - Export Tasks to Calendar (depends on US1, independent of US2-4)
  ↓
Phase 7: Polish & Integration
```

### Independent Test Criteria by User Story

**US1** (P1): Create task with due date + reminder offset → verify saved correctly, reminder_time calculated accurately
**US2** (P2): Simulate reminder trigger time → verify notification created in database + appears in dropdown
**US3** (P3): Create 5 tasks with different reminder times → verify widget shows next 5 in chronological order
**US4** (P4): Generate 10 notifications → verify bulk "mark all read" updates all records
**US5** (P5): Create 3 tasks with due dates → export .ics → import to Google Calendar → verify 3 events appear

---

## MVP Scope Recommendation

**Minimum Viable Product**: User Story 1 only (P1)

Delivers: Users can set due dates and reminders on tasks via calendar picker. Core value delivered even without active notification system.

**MVP+ (Recommended)**: User Stories 1 + 2 (P1 + P2)

Delivers: Full reminder workflow (set reminders → receive notifications). Complete core feature loop.

---

## Phase 1: Setup & Dependencies

**Goal**: Install dependencies, run database migration, create foundational infrastructure

**Duration**: ~45 minutes

### Backend Setup

- [X] T001 Add APScheduler and icalendar to backend/requirements.txt
- [X] T002 Install backend dependencies via pip install -r backend/requirements.txt
- [X] T003 [P] Generate Alembic migration script for database schema changes in backend/alembic/versions/
- [X] T004 Apply database migration via alembic upgrade head
- [X] T005 Verify new columns added to tasks table (due_date, reminder_offset, reminder_time, last_reminder_sent, last_overdue_notification_sent)
- [X] T006 Verify new notifications table created with proper indexes

### Frontend Setup

- [X] T007 Add react-datepicker and date-fns to frontend/package.json
- [X] T008 Install frontend dependencies via npm install

---

## Phase 2: User Story 1 - Set Due Date and Reminder (P1)

**Goal**: Users can set due dates with calendar picker and choose reminder offset from preset options

**Independent Test**: Create task with due_date="2026-01-05 15:00" + reminder_offset="1d" → verify task.reminder_time="2026-01-04 15:00" in database

**Duration**: ~3 hours

### Backend - Data Models & Validation

- [X] T009 [P] [US1] Extend Task model in backend/app/models.py with new fields (due_date, reminder_offset, reminder_time, last_reminder_sent, last_overdue_notification_sent)
- [X] T010 [P] [US1] Create Notification model in backend/app/models.py (id, user_id, task_id, type, title, message, is_read, created_at)
- [X] T011 [P] [US1] Add TaskCreate schema in backend/app/schemas.py with due_date and reminder_offset fields
- [X] T012 [P] [US1] Add TaskUpdate schema in backend/app/schemas.py with optional due_date and reminder_offset fields
- [X] T013 [P] [US1] Add Pydantic validators in backend/app/schemas.py (due_date must be future, reminder_offset valid enum, reminder_time feasibility check)
- [X] T014 [P] [US1] Create NotificationCreate and NotificationRead schemas in backend/app/schemas.py

### Backend - Business Logic

- [X] T015 [P] [US1] Create reminder_calculator.py utility in backend/app/utils/ with calculate_reminder_time function (maps offset to timedelta, validates result is future)
- [X] T016 [US1] Update create_task function in backend/app/crud.py to calculate and save reminder_time when due_date + reminder_offset provided
- [X] T017 [US1] Update update_task function in backend/app/crud.py to recalculate reminder_time when due_date or reminder_offset changes
- [X] T018 [US1] Update patch_task function in backend/app/crud.py to handle partial updates of due_date/reminder_offset

### Backend - API Endpoints

- [X] T019 [US1] Update POST /api/v1/tasks endpoint in backend/app/routes/tasks.py to accept due_date and reminder_offset in request body
- [X] T020 [US1] Update PUT /api/v1/tasks/{id} endpoint in backend/app/routes/tasks.py to handle due_date and reminder_offset updates
- [X] T021 [US1] Update PATCH /api/v1/tasks/{id} endpoint in backend/app/routes/tasks.py for partial updates
- [X] T022 [US1] Update GET /api/v1/tasks endpoint in backend/app/routes/tasks.py to return new fields in response
- [X] T023 [US1] Add validation error responses (400) for invalid due dates or reminder offsets

### Frontend - Types & API

- [X] T024 [P] [US1] Extend Task interface in frontend/lib/types.ts with due_date, reminder_offset, reminder_time fields
- [X] T025 [P] [US1] Create Notification interface in frontend/lib/types.ts
- [X] T026 [US1] Update createTask function in frontend/lib/api.ts to include due_date and reminder_offset in request
- [X] T027 [US1] Update updateTask function in frontend/lib/api.ts to include new fields

### Frontend - UI Components

- [X] T028 [US1] Install react-datepicker CSS in frontend/components/TaskForm.tsx (import 'react-datepicker/dist/react-datepicker.css')
- [X] T029 [US1] Add due date picker to TaskForm.tsx using DatePicker component (showTimeSelect, minDate=now, timeIntervals=15)
- [X] T030 [US1] Add reminder offset dropdown to TaskForm.tsx (only visible when due_date set, options: Never/1h/1d/3d/5d/1w)
- [X] T031 [US1] Add state management in TaskForm.tsx for dueDate (Date | null) and reminderOffset (string)
- [X] T032 [US1] Add validation in TaskForm.tsx to disable invalid offset options when due date is too soon
- [X] T033 [US1] Update TaskForm submit handler to send due_date as ISO string and reminder_offset to API
- [X] T034 [P] [US1] Add due date badge to TaskItem.tsx component (shows formatted due date when set)
- [X] T035 [P] [US1] Add reminder indicator icon to TaskItem.tsx (shows clock icon when reminder_offset is set)

### Testing & Verification

- [ ] T036 [US1] Manual test: Create task with due date tomorrow 3 PM + reminder "1 day before" → verify task saved with correct reminder_time in database
- [ ] T037 [US1] Manual test: Try to set due date in past → verify validation error shown
- [ ] T038 [US1] Manual test: Set due date 2 hours from now + select "1 day before" → verify validation error or option disabled
- [ ] T039 [US1] Manual test: Edit existing task to add due date + reminder → verify update successful

**US1 Complete**: ✅ Users can now set due dates and reminders on tasks

---

## Phase 3: User Story 2 - Receive In-App Notifications (P2)

**Goal**: Background scheduler creates notifications when reminders trigger or tasks become overdue; users see notifications in dropdown panel

**Independent Test**: Set task.reminder_time to 1 minute from now in database → wait 60 seconds → verify notification created + appears in dropdown with unread badge

**Duration**: ~4 hours

**Dependencies**: US1 complete (needs Task model with reminder fields)

### Backend - Scheduler

- [X] T040 [P] [US2] Create scheduler.py in backend/app/ with APScheduler AsyncIOScheduler setup and SQLAlchemy jobstore configuration
- [X] T041 [US2] Implement check_reminders_and_overdue scheduled job in backend/app/scheduler.py (runs every 60 seconds)
- [X] T042 [US2] Add reminder query logic: SELECT tasks WHERE reminder_time <= NOW() AND last_reminder_sent IS NULL AND completed = false
- [X] T043 [US2] Add overdue query logic: SELECT tasks WHERE due_date <= NOW() AND completed = false AND last_overdue_notification_sent IS NULL
- [X] T044 [US2] Implement notification creation for reminder type (user_id, task_id, type="reminder", title=task.title, message="Task is due soon")
- [X] T045 [US2] Implement notification creation for overdue type (type="overdue", message="This task is overdue")
- [X] T046 [US2] Update task.last_reminder_sent and task.last_overdue_notification_sent timestamps to prevent duplicates
- [X] T047 [US2] Add scheduler initialization to FastAPI lifespan context manager in backend/app/main.py
- [X] T048 [US2] Add scheduler shutdown logic to FastAPI lifespan context manager

### Backend - Notification Endpoints

- [X] T049 [P] [US2] Create notifications.py route module in backend/app/routes/
- [X] T050 [P] [US2] Implement GET /api/v1/notifications endpoint with filtering (is_read, type, limit, offset)
- [X] T051 [P] [US2] Implement GET /api/v1/notifications/unread-count endpoint
- [X] T052 [P] [US2] Implement PATCH /api/v1/notifications/{id} endpoint to mark as read
- [X] T053 [P] [US2] Add notification CRUD functions to backend/app/crud.py (get_notifications, get_unread_count, mark_as_read)
- [X] T054 [US2] Include notifications router in backend/app/main.py (app.include_router)
- [X] T055 [US2] Add authorization check: user can only access their own notifications (user_id from JWT)

### Frontend - Notification Dropdown

- [X] T056 [P] [US2] Create useNotifications.ts hook in frontend/hooks/ with React Query for fetching notifications (refetchInterval: 60000)
- [X] T057 [P] [US2] Add fetchNotifications function to frontend/lib/api.ts (GET /notifications with filters)
- [X] T058 [P] [US2] Add fetchUnreadCount function to frontend/lib/api.ts (GET /notifications/unread-count)
- [X] T059 [P] [US2] Add markNotificationRead function to frontend/lib/api.ts (PATCH /notifications/{id})
- [X] T060 [P] [US2] Create NotificationDropdown.tsx component in frontend/components/ with bell icon + unread badge
- [X] T061 [US2] Implement dropdown panel in NotificationDropdown.tsx (absolute positioning, shadow, max-height with scroll)
- [X] T062 [US2] Add click-outside detection to close dropdown in NotificationDropdown.tsx
- [X] T063 [P] [US2] Create NotificationItem.tsx component in frontend/components/ (displays title, message, timestamp, read status)
- [X] T064 [US2] Add onClick handler in NotificationItem.tsx to navigate to task and mark notification as read
- [X] T065 [US2] Add NotificationDropdown to top navigation bar in frontend/app/dashboard/page.tsx

### Frontend - Overdue Indicator

- [X] T066 [P] [US2] Add overdue detection logic in TaskItem.tsx (check if due_date < now && !completed)
- [X] T067 [P] [US2] Add red badge/warning icon to TaskItem.tsx for overdue tasks

### Testing & Verification

- [ ] T068 [US2] Manual test: Update a task's reminder_time to 30 seconds from now → wait 60 seconds → verify notification appears in dropdown with badge count
- [ ] T069 [US2] Manual test: Set task due_date in past → verify overdue notification created and task shows red indicator
- [ ] T070 [US2] Manual test: Click notification → verify navigates to task and marks notification as read
- [ ] T071 [US2] Manual test: Verify unread count badge updates correctly when notifications marked as read

**US2 Complete**: ✅ Users now receive notifications for reminders and overdue tasks

---

## Phase 4: User Story 3 - View Upcoming Reminders (P3)

**Goal**: Dashboard widget shows next 5 upcoming reminders in chronological order

**Independent Test**: Create 5 tasks with reminders at different times (today + tomorrow) → verify widget shows all 5 sorted by reminder_time ascending

**Duration**: ~1.5 hours

**Dependencies**: US1 complete (needs reminder data model)
**Can run parallel to**: US2 (independent features)

### Backend

- [ ] T072 [P] [US3] Add GET /api/v1/tasks/upcoming-reminders endpoint in backend/app/routes/tasks.py (query: reminder_time > NOW() ORDER BY reminder_time ASC LIMIT 5)
- [ ] T073 [P] [US3] Add get_upcoming_reminders function to backend/app/crud.py with 24-hour window filter

### Frontend

- [ ] T074 [P] [US3] Create UpcomingReminders.tsx component in frontend/components/
- [ ] T075 [P] [US3] Add fetchUpcomingReminders function to frontend/lib/api.ts
- [ ] T076 [US3] Implement widget UI in UpcomingReminders.tsx (list of next 5 reminders with formatted time, empty state: "No upcoming reminders")
- [ ] T077 [US3] Add UpcomingReminders widget to dashboard in frontend/app/dashboard/page.tsx
- [ ] T078 [US3] Add React Query hook in UpcomingReminders.tsx with polling (refetchInterval: 60000)

### Testing & Verification

- [ ] T079 [US3] Manual test: Create 5 tasks with reminders (3 today, 2 tomorrow) → verify widget shows 5 sorted chronologically
- [ ] T080 [US3] Manual test: Wait for a reminder to pass → verify it disappears from upcoming list
- [ ] T081 [US3] Manual test: Create task with no reminder → verify it doesn't appear in widget

**US3 Complete**: ✅ Users can now see upcoming reminders at a glance

---

## Phase 5: User Story 4 - Notification Management (P4)

**Goal**: Users can mark all notifications as read, delete notifications, and filter by read status

**Independent Test**: Generate 10 unread notifications → click "Mark all as read" → verify all 10 updated to is_read=true and badge shows 0

**Duration**: ~1.5 hours

**Dependencies**: US2 complete (needs notification system working)

### Backend

- [ ] T082 [P] [US4] Implement POST /api/v1/notifications/mark-all-read endpoint in backend/app/routes/notifications.py
- [ ] T083 [P] [US4] Implement DELETE /api/v1/notifications/{id} endpoint in backend/app/routes/notifications.py
- [ ] T084 [P] [US4] Implement DELETE /api/v1/notifications/read endpoint in backend/app/routes/notifications.py (delete all read notifications for user)
- [ ] T085 [P] [US4] Add mark_all_read, delete_notification, delete_read_notifications functions to backend/app/crud.py

### Frontend

- [ ] T086 [P] [US4] Add markAllNotificationsRead function to frontend/lib/api.ts (POST /notifications/mark-all-read)
- [ ] T087 [P] [US4] Add deleteNotification function to frontend/lib/api.ts (DELETE /notifications/{id})
- [ ] T088 [US4] Add "Mark all as read" button to NotificationDropdown.tsx header
- [ ] T089 [US4] Add delete button to NotificationItem.tsx with confirmation
- [ ] T090 [US4] Add filter toggle in NotificationDropdown.tsx ("All" | "Unread only")
- [ ] T091 [US4] Update useNotifications.ts hook to include markAllRead and deleteNotification mutations with optimistic updates

### Testing & Verification

- [ ] T092 [US4] Manual test: Create 10 unread notifications → click "Mark all as read" → verify all marked as read and badge = 0
- [ ] T093 [US4] Manual test: Delete individual notification → verify removed from list
- [ ] T094 [US4] Manual test: Toggle "Unread only" filter → verify only unread notifications shown

**US4 Complete**: ✅ Users can now manage their notification list

---

## Phase 6: User Story 5 - Export Tasks to Calendar (P5)

**Goal**: Users can download .ics file containing all tasks with due dates for import into calendar apps

**Independent Test**: Create 3 tasks with due dates → click "Export to Calendar" → download .ics file → import to Google Calendar → verify 3 events created

**Duration**: ~2 hours

**Dependencies**: US1 complete (needs tasks with due dates)
**Can run parallel to**: US2, US3, US4 (independent feature)

### Backend

- [ ] T095 [P] [US5] Create ics_generator.py utility in backend/app/utils/ with generate_ics function (uses icalendar library)
- [ ] T096 [P] [US5] Implement iCalendar VCALENDAR generation with proper headers (VERSION=2.0, PRODID, CALSCALE=GREGORIAN)
- [ ] T097 [P] [US5] Implement VEVENT generation per task (UID, DTSTART, DTEND, SUMMARY, DESCRIPTION, STATUS, DTSTAMP)
- [ ] T098 [P] [US5] Create calendar_export.py route module in backend/app/routes/
- [ ] T099 [US5] Implement GET /api/v1/calendar/export endpoint with query params (include_completed, date_range_start, date_range_end)
- [ ] T100 [US5] Add query logic to filter tasks by user_id and due_date IS NOT NULL
- [ ] T101 [US5] Return Response with media_type="text/calendar" and Content-Disposition attachment header
- [ ] T102 [US5] Include calendar export router in backend/app/main.py
- [ ] T103 [US5] Handle empty result (no tasks with due dates) with 204 No Content response

### Frontend

- [ ] T104 [P] [US5] Create CalendarExportButton.tsx component in frontend/components/
- [ ] T105 [P] [US5] Add downloadCalendar function to frontend/lib/api.ts (GET /calendar/export, returns Blob)
- [ ] T106 [US5] Implement button click handler in CalendarExportButton.tsx to download .ics file (create blob URL, trigger download, revoke URL)
- [ ] T107 [US5] Add loading state and error handling to CalendarExportButton.tsx
- [ ] T108 [US5] Add CalendarExportButton to dashboard in frontend/app/dashboard/page.tsx
- [ ] T109 [US5] Add toast notifications for success/error states

### Testing & Verification

- [ ] T110 [US5] Manual test: Create 3 tasks with due dates → click "Export to Calendar" → verify .ics file downloads with correct filename (tasks-YYYY-MM-DD.ics)
- [ ] T111 [US5] Manual test: Open .ics file in text editor → verify RFC 5545 format (BEGIN:VCALENDAR, BEGIN:VEVENT for each task)
- [ ] T112 [US5] Manual test: Import .ics file into Google Calendar → verify 3 events appear at correct dates/times
- [ ] T113 [US5] Manual test: Export when no tasks have due dates → verify 204 response or empty file with appropriate message

**US5 Complete**: ✅ Users can now export tasks to external calendars

---

## Phase 7: Polish & Integration

**Goal**: Translation strings, cleanup, final testing, deployment preparation

**Duration**: ~1 hour

### Internationalization

- [ ] T114 [P] Add English translation keys to frontend/public/locales/en/common.json (dueDate, reminder, reminderOptions, notifications, markAllRead, exportToCalendar, overdue, upcomingReminders)
- [ ] T115 [P] Add Urdu translations to frontend/public/locales/ur/common.json
- [ ] T116 [P] Add Arabic translations to frontend/public/locales/ar/common.json
- [ ] T117 [P] Add Spanish translations to frontend/public/locales/es/common.json
- [ ] T118 [P] Add French translations to frontend/public/locales/fr/common.json
- [ ] T119 [P] Add German translations to frontend/public/locales/de/common.json

### Final Integration & Testing

- [ ] T120 Complete end-to-end test: Create task with due date → wait for reminder → receive notification → mark as read → export to calendar
- [ ] T121 Test scheduler persistence: Restart backend server → verify scheduled reminders still work
- [ ] T122 Test timezone handling: Create task in different timezone → verify times stored/displayed correctly
- [ ] T123 Update CLAUDE.md if needed with any new technologies or patterns discovered during implementation
- [ ] T124 Commit all changes with message: "feat(reminders): Complete task reminders and in-app notifications feature"
- [ ] T125 Create pull request for 006-task-reminders branch → main

---

## Parallel Execution Opportunities

### Setup Phase (can all run in parallel after dependencies installed)
- T003 (backend migration generation)
- T007-T008 (frontend package installation)

### User Story 1 - Backend (can run in parallel)
- T009-T014 (all model and schema definitions are independent)
- T015 (reminder calculator utility)

### User Story 1 - Frontend (can run in parallel)
- T024-T025 (type definitions)
- T034-T035 (TaskItem badges - different UI elements)

### User Story 2 - Backend Routes (can run in parallel)
- T049-T052 (all notification endpoint implementations)

### User Story 2 - Frontend (can run in parallel)
- T056-T059 (all API functions and hooks)
- T060, T063, T066-T067 (independent UI components)

### User Stories 3, 4, 5 (can run completely in parallel once US1 is complete)
- US3 (T072-T081): Independent widget feature
- US5 (T095-T113): Independent export feature
- US4 requires US2 complete, but can start as soon as US2 is done

### I18n Translations (can all run in parallel)
- T114-T119 (6 language files, independent)

---

## Task Completion Checklist

### Phase 1: Setup ✅
- [ ] All dependencies installed
- [ ] Database migrated successfully
- [ ] New tables and columns verified

### Phase 2: US1 - Set Due Date and Reminder ✅
- [ ] Task model extended
- [ ] API endpoints accept due_date + reminder_offset
- [ ] Frontend shows calendar picker + offset dropdown
- [ ] Reminder_time calculated correctly

### Phase 3: US2 - Receive Notifications ✅
- [ ] APScheduler running and checking every 60 seconds
- [ ] Notifications created for reminders and overdue tasks
- [ ] Notification dropdown shows unread count badge
- [ ] Clicking notification navigates to task

### Phase 4: US3 - View Upcoming Reminders ✅
- [ ] Dashboard widget shows next 5 reminders
- [ ] Reminders sorted chronologically
- [ ] Widget updates via polling

### Phase 5: US4 - Notification Management ✅
- [ ] Mark all as read works
- [ ] Delete individual notifications works
- [ ] Filter by unread status works

### Phase 6: US5 - Export to Calendar ✅
- [ ] .ics file generates correctly
- [ ] File downloads with proper filename
- [ ] Imports successfully into Google Calendar/Apple Calendar

### Phase 7: Polish ✅
- [ ] All translation strings added (6 languages)
- [ ] End-to-end testing complete
- [ ] Committed and PR created

---

## Notes

**Testing Strategy**: Manual testing is specified throughout. Constitution requires 80%+ test coverage but tests are marked as pending in constitution check. Automated tests (pytest, Jest) can be added in a follow-up iteration if needed.

**Estimated Total Time**: 12-15 hours across all phases

**Critical Path**: Setup → US1 → US2 → US4 → Polish (minimum viable path)

**Recommended Delivery**:
1. **Sprint 1**: Setup + US1 (MVP - due dates and reminders set)
2. **Sprint 2**: US2 (notifications delivered)
3. **Sprint 3**: US3 + US5 (parallel - widget + export)
4. **Sprint 4**: US4 + Polish (notification management + translations)

**Deployment**: After Phase 7 complete, changes will deploy to http://161-35-250-151.nip.io/ via DigitalOcean Kubernetes CI/CD pipeline.
