# Research: Task Reminders and In-App Notifications

**Feature**: 006-task-reminders
**Date**: 2025-12-30
**Phase**: 0 - Research & Decision Making

## Overview

This document consolidates research findings for implementing task reminders and in-app notifications. All technical decisions are documented with rationale and alternatives considered.

---

## Decision 1: Background Task Scheduler

**Decision**: Use **APScheduler** with SQLAlchemy jobstore for persistent scheduling

**Rationale**:
1. **Lightweight**: Runs in-process with FastAPI, no separate infrastructure needed (vs Celery + Redis/RabbitMQ)
2. **Persistence**: SQLAlchemy jobstore survives server restarts without losing scheduled reminders
3. **FastAPI Integration**: Well-documented integration patterns with FastAPI lifespan events
4. **Sufficient Scale**: Handles 100k+ scheduled jobs with proper database indexing
5. **Simplicity**: Single dependency (`apscheduler==3.10.4`), no message broker required

**Alternatives Considered**:
- **Celery + Redis**: Too heavy for this use case; requires separate Redis instance and Celery workers. Overkill for 60-second polling.
- **Cron Jobs**: Not suitable for dynamic reminders (would need external cron + database polling script). Less elegant integration.
- **FastAPI Background Tasks**: Not persistent across restarts; designed for short-lived tasks, not recurring schedules.

**Implementation Pattern**:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(url=DATABASE_URL)
}
scheduler = AsyncIOScheduler(jobstores=jobstores)

@scheduler.scheduled_job('interval', seconds=60)
async def check_reminders():
    # Query tasks where reminder_time <= now AND notification not sent
    # Create notifications for matched tasks
```

---

## Decision 2: Datetime Picker Component

**Decision**: Use **react-datepicker** with date-fns for date/time selection

**Rationale**:
1. **Popular**: 8.6k+ GitHub stars, actively maintained, 3M+ npm downloads/week
2. **Customizable**: Supports time picking, min/max dates, custom styling
3. **Accessible**: ARIA labels, keyboard navigation, screen reader compatible
4. **Lightweight**: ~50KB gzipped, no jQuery dependency
5. **i18n Support**: Works with existing date-fns localization

**Alternatives Considered**:
- **shadcn/ui DatePicker**: Good option but adds Radix UI dependency. More setup than react-datepicker.
- **MUI DatePicker**: Requires @mui/x-date-pickers (larger bundle), paid features for some advanced use cases.
- **Native HTML5 `<input type="datetime-local">`**: Inconsistent browser support, poor UX (especially on Safari).

**Integration**:
```tsx
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

<DatePicker
  selected={dueDate}
  onChange={(date) => setDueDate(date)}
  showTimeSelect
  timeIntervals={15}
  dateFormat="MMM d, yyyy h:mm aa"
  minDate={new Date()}
  placeholderText="Select due date"
/>
```

---

## Decision 3: iCalendar (.ics) File Generation

**Decision**: Use **icalendar** Python library for .ics file generation

**Rationale**:
1. **RFC 5545 Compliant**: Generates spec-compliant iCalendar files compatible with all major calendar apps
2. **Mature**: 10+ years in production, 900+ GitHub stars, actively maintained
3. **Simple API**: Clean Python API for creating events, alarms, and calendar metadata
4. **No Dependencies**: Pure Python implementation

**Alternatives Considered**:
- **Manual String Building**: Error-prone, hard to maintain RFC compliance, reinventing the wheel
- **ics** Python library: Simpler but less feature-complete than icalendar, smaller community

**Implementation Pattern**:
```python
from icalendar import Calendar, Event
from datetime import datetime

def generate_ics(tasks: List[Task]) -> bytes:
    cal = Calendar()
    cal.add('prodid', '-//Physical AI Todo//EN')
    cal.add('version', '2.0')

    for task in tasks:
        if task.due_date:
            event = Event()
            event.add('summary', task.title)
            event.add('description', task.description or '')
            event.add('dtstart', task.due_date)
            event.add('dtend', task.due_date)
            event.add('dtstamp', datetime.now())
            event.add('uid', f'task-{task.id}@physical-ai-todo.com')
            cal.add_component(event)

    return cal.to_ical()
```

---

## Decision 4: Notification Storage Strategy

**Decision**: Store all notifications in a dedicated `notifications` table with soft-delete capability

**Rationale**:
1. **Audit Trail**: Preserves notification history for debugging and analytics
2. **Scalability**: Separate table prevents bloating the `tasks` table
3. **Flexible Queries**: Efficient filtering by read status, notification type, date range
4. **Cleanup Strategy**: Can implement periodic cleanup of old read notifications (e.g., delete after 30 days)

**Schema Design**:
```python
class Notification(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    task_id: int = Field(foreign_key="task.id", index=True)
    type: str = Field(max_length=50)  # "reminder", "overdue"
    title: str = Field(max_length=200)
    message: str = Field(max_length=500)
    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.now, index=True)
```

**Indexes**:
- `user_id` + `is_read` (composite) for efficient "unread notifications" queries
- `task_id` for quick lookup when task is deleted (cascade cleanup)
- `created_at` for date-range queries and cleanup jobs

**Alternatives Considered**:
- **Embedded in Task Table**: Would create 1:N relationship complexity, harder to query unread notifications across all tasks
- **Ephemeral (No Storage)**: Loses notification history, can't show "you had 5 reminders today" analytics

---

## Decision 5: Reminder Calculation Logic

**Decision**: Calculate `reminder_time` on **backend when task is created/updated**, store as datetime field

**Rationale**:
1. **Single Source of Truth**: Backend owns the calculation, frontend just displays result
2. **Consistency**: All clients (web, future mobile) see the same reminder time
3. **Queryable**: Scheduler can efficiently query `WHERE reminder_time <= NOW()` without recomputing
4. **Timezone Handling**: Backend handles UTC storage, frontend converts to user's local time for display

**Calculation Logic**:
```python
from datetime import datetime, timedelta

OFFSET_MAPPING = {
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1),
    "3d": timedelta(days=3),
    "5d": timedelta(days=5),
    "1w": timedelta(weeks=1),
}

def calculate_reminder_time(due_date: datetime, offset: str | None) -> datetime | None:
    if not due_date or not offset or offset == "never":
        return None

    delta = OFFSET_MAPPING.get(offset)
    if not delta:
        raise ValueError(f"Invalid offset: {offset}")

    reminder_time = due_date - delta

    # Validation: reminder must be in the future
    if reminder_time <= datetime.now():
        raise ValueError("Reminder time would be in the past")

    return reminder_time
```

**Alternatives Considered**:
- **Frontend Calculation**: Would require duplicating logic in TypeScript, risk of inconsistency
- **Calculate On-Demand**: Would make scheduler queries complex (`WHERE due_date - offset <= NOW()` - no index benefit)

---

## Decision 6: Notification Polling Strategy (Frontend)

**Decision**: Use **React Query** with 60-second polling interval + manual refetch on user actions

**Rationale**:
1. **Existing Infrastructure**: Project already uses TanStack Query for data fetching
2. **Automatic Refetching**: Built-in polling with `refetchInterval: 60000`
3. **Smart Deduplication**: Multiple components can use same query, single network request
4. **Optimistic Updates**: Can mark as read immediately with `useMutation` optimistic updates

**Implementation**:
```tsx
const { data: notifications } = useQuery({
  queryKey: ['notifications', 'unread'],
  queryFn: () => fetchNotifications({ isRead: false }),
  refetchInterval: 60000, // Poll every 60 seconds
  refetchOnWindowFocus: true,
});
```

**Alternatives Considered**:
- **WebSocket**: More complex infrastructure, requires WebSocket server setup, overkill for 60-second latency tolerance
- **Server-Sent Events (SSE)**: Simpler than WebSocket but still requires persistent connection, not necessary for this use case

---

## Decision 7: Overdue Detection Strategy

**Decision**: Same scheduler job checks both `reminder_time` and `due_date` for overdue status

**Rationale**:
1. **Efficiency**: Single scheduler job handles both reminder and overdue checks
2. **Consistent Timing**: Both run on same 60-second interval
3. **Simple Logic**: `if due_date < now AND not completed AND not notified_overdue`

**Deduplication Strategy**:
Add `last_overdue_notification_sent` timestamp to Task model to prevent duplicate overdue notifications:
```python
class Task(SQLModel, table=True):
    # ... existing fields ...
    due_date: datetime | None = Field(default=None, index=True)
    reminder_offset: str | None = Field(max_length=10)
    reminder_time: datetime | None = Field(default=None, index=True)
    last_reminder_sent: datetime | None = None
    last_overdue_notification_sent: datetime | None = None
```

Scheduler logic:
```python
async def check_reminders_and_overdue():
    now = datetime.now()

    # Check reminders
    reminder_tasks = await get_tasks_due_for_reminder(now)
    for task in reminder_tasks:
        await create_notification(task, type="reminder")
        await update_task(task.id, last_reminder_sent=now)

    # Check overdue
    overdue_tasks = await get_overdue_tasks(now)
    for task in overdue_tasks:
        if not task.last_overdue_notification_sent:  # Only send once
            await create_notification(task, type="overdue")
            await update_task(task.id, last_overdue_notification_sent=now)
```

---

## Decision 8: Task Form UX Pattern

**Decision**: Due date picker appears first, reminder offset dropdown appears only when due date is set

**Rationale**:
1. **Progressive Disclosure**: Simplifies UI, users only see reminder options after setting a due date
2. **Validation Simplification**: Can validate offset against due date in real-time
3. **Clear Dependency**: Visually communicates that reminders require a due date

**UI Flow**:
```tsx
1. User clicks "Due Date" field → DatePicker opens
2. User selects date/time → Due date set
3. Reminder dropdown appears below with options:
   - Never (default)
   - 1 hour before
   - 1 day before
   - 3 days before
   - 5 days before
   - 1 week before (grayed out if due date < 7 days from now)
4. User selects offset → Calculated reminder time shows as badge
```

---

## Best Practices Applied

### APScheduler Integration
- Use AsyncIOScheduler for FastAPI async compatibility
- Configure jobstore with connection pooling for database efficiency
- Implement graceful shutdown in FastAPI lifespan context
- Add error handling and logging for failed reminder checks

### Timezone Handling
- Store all datetimes in UTC in database
- Convert to user's local timezone in frontend display only
- Use ISO 8601 format for API transport (includes timezone info)

### Database Indexes
- Composite index on `(user_id, is_read)` for notification queries
- Index on `reminder_time` for efficient scheduler queries
- Index on `due_date` for overdue checks and filtering

### Error Handling
- Validate due date is in future (both frontend and backend)
- Validate reminder offset doesn't result in past time
- Handle edge case: user changes timezone (reminder time stays absolute in UTC)
- Handle scheduler failures gracefully (log errors, don't crash app)

### Performance Optimizations
- Scheduler query limits to tasks needing action (`WHERE reminder_time <= NOW()`)
- Batch notification creation if many tasks trigger at once
- Use connection pooling for database (already configured in Neon setup)
- Lazy-load notification dropdown content (only fetch on icon click)

---

## Dependencies to Add

### Backend (`requirements.txt`)
```
apscheduler==3.10.4
icalendar==5.0.11
```

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "react-datepicker": "^4.25.0",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "@types/react-datepicker": "^4.19.0"
  }
}
```

---

## Security Considerations

1. **Authorization**: All notification endpoints verify `current_user` from JWT
2. **Input Validation**: Pydantic schemas validate all date/time inputs
3. **SQL Injection**: SQLModel parameterized queries prevent injection
4. **Rate Limiting**: Consider adding rate limit to notification mark-as-read endpoint (prevent spam)
5. **XSS Prevention**: Frontend escapes notification content before rendering

---

## Summary

All technical decisions have been made with clear rationale. The architecture leverages existing infrastructure (FastAPI, SQLModel, React Query) while adding minimal new dependencies (APScheduler, icalendar, react-datepicker). The solution is simple, maintainable, and scales to 100k+ users with proper database indexing.

**Ready to proceed to Phase 1: Data Model & Contracts**
