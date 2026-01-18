# API Contract: Calendar Export Endpoint (NEW)

**Feature**: 006-task-reminders
**Date**: 2025-12-30
**Base Path**: `/api/v1/calendar`

## Overview

This document specifies the new Calendar Export API endpoint for generating .ics (iCalendar) files that users can import into Google Calendar, Apple Calendar, Outlook, etc.

---

## Endpoint: Export Tasks to Calendar

### `GET /api/v1/calendar/export`

**Description**: Generate and download an .ics file containing all user's tasks with due dates

**Authentication**: Required (JWT)

### Request

**Query Parameters**:
```
?include_completed=false    // Include completed tasks (default: false)
&date_range_start=2026-01-01  // Optional: Only tasks due after this date (ISO 8601)
&date_range_end=2026-12-31    // Optional: Only tasks due before this date (ISO 8601)
```

**Headers**:
```
Authorization: Bearer <jwt_token>
Accept: text/calendar
```

### Response

**Success (200 OK)**:

**Headers**:
```
Content-Type: text/calendar; charset=utf-8
Content-Disposition: attachment; filename="tasks-2025-12-30.ics"
```

**Body** (.ics file content):
```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Physical AI Todo//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:My Tasks
X-WR-TIMEZONE:UTC

BEGIN:VEVENT
UID:task-123@physical-ai-todo.com
DTSTAMP:20251230T100000Z
DTSTART:20260105T150000Z
DTEND:20260105T150000Z
SUMMARY:Submit quarterly report
DESCRIPTION:Compile Q4 financial data and submit to board
STATUS:TENTATIVE
CLASS:PUBLIC
TRANSP:OPAQUE
END:VEVENT

BEGIN:VEVENT
UID:task-124@physical-ai-todo.com
DTSTAMP:20251230T100000Z
DTSTART:20260110T140000Z
DTEND:20260110T140000Z
SUMMARY:Review contract
DESCRIPTION:Review legal contract with external counsel
STATUS:TENTATIVE
CLASS:PUBLIC
TRANSP:OPAQUE
END:VEVENT

END:VCALENDAR
```

**Error Responses**:

**401 Unauthorized** - Missing/invalid JWT:
```json
{
  "detail": "Not authenticated"
}
```

**204 No Content** - User has no tasks with due dates:
Response is empty with 204 status code (no .ics file generated)

---

## iCalendar Format Specification

### VCALENDAR Properties

| Property | Value | Description |
|----------|-------|-------------|
| `VERSION` | `2.0` | iCalendar version (RFC 5545) |
| `PRODID` | `-//Physical AI Todo//EN` | Product identifier |
| `CALSCALE` | `GREGORIAN` | Calendar scale |
| `METHOD` | `PUBLISH` | Calendar method (publish for export) |
| `X-WR-CALNAME` | `My Tasks` | Calendar name (custom property) |
| `X-WR-TIMEZONE` | `UTC` | Default timezone |

### VEVENT Properties (Per Task)

| Property | Source | Example | Description |
|----------|--------|---------|-------------|
| `UID` | `task-{task.id}@physical-ai-todo.com` | `task-123@physical-ai-todo.com` | Unique event identifier |
| `DTSTAMP` | Current timestamp | `20251230T100000Z` | When event was created/modified |
| `DTSTART` | `task.due_date` | `20260105T150000Z` | Event start time (due date) |
| `DTEND` | `task.due_date` | `20260105T150000Z` | Event end time (same as start for tasks) |
| `SUMMARY` | `task.title` | `Submit quarterly report` | Event title |
| `DESCRIPTION` | `task.description` or empty | `Compile Q4 financial data...` | Event description |
| `STATUS` | `TENTATIVE` or `CONFIRMED` | `TENTATIVE` | Event status (TENTATIVE if not completed, CONFIRMED if completed) |
| `CLASS` | `PUBLIC` | `PUBLIC` | Privacy classification |
| `TRANSP` | `OPAQUE` | `OPAQUE` | Time transparency (blocks time) |

### Optional Properties (Future Enhancement)

- `CATEGORIES`: Could map to `task.tags` (e.g., `CATEGORIES:work,finance`)
- `PRIORITY`: Could map to `task.priority` (1-9 scale, 1=high, 5=medium, 9=low)
- `VALARM`: Could add reminder alarms based on `task.reminder_offset`

---

## Data Flow Example

### Example 1: Basic Export

**Request**:
```http
GET /api/v1/calendar/export
Authorization: Bearer eyJ...
Accept: text/calendar
```

**Backend Processing**:
1. Authenticate user from JWT (user_id = 45)
2. Query tasks:
   ```sql
   SELECT * FROM task
   WHERE user_id = 45
     AND due_date IS NOT NULL
     AND completed = false
   ORDER BY due_date ASC;
   ```
3. Generate iCalendar file:
   ```python
   from icalendar import Calendar, Event

   cal = Calendar()
   cal.add('prodid', '-//Physical AI Todo//EN')
   cal.add('version', '2.0')

   for task in tasks:
       event = Event()
       event.add('uid', f'task-{task.id}@physical-ai-todo.com')
       event.add('summary', task.title)
       event.add('description', task.description or '')
       event.add('dtstart', task.due_date)
       event.add('dtend', task.due_date)
       event.add('dtstamp', datetime.now())
       event.add('status', 'TENTATIVE')
       cal.add_component(event)

   return cal.to_ical()
   ```
4. Return .ics file with appropriate headers

**Response**:
- Content-Type: `text/calendar`
- File downloads to user's device as `tasks-2025-12-30.ics`

---

### Example 2: Export with Filters

**Request**:
```http
GET /api/v1/calendar/export?include_completed=true&date_range_start=2026-01-01&date_range_end=2026-03-31
Authorization: Bearer eyJ...
```

**Backend Processing**:
1. Query tasks with filters:
   ```sql
   SELECT * FROM task
   WHERE user_id = 45
     AND due_date IS NOT NULL
     AND due_date >= '2026-01-01'
     AND due_date <= '2026-03-31'
   ORDER BY due_date ASC;
   ```
   (Note: `completed` filter removed since `include_completed=true`)

2. Generate .ics file with filtered tasks
3. Return file

---

### Example 3: No Tasks with Due Dates

**Request**:
```http
GET /api/v1/calendar/export
Authorization: Bearer eyJ...
```

**Backend Query Result**: 0 tasks found

**Response (204 No Content)**:
- No body
- Status: 204
- No file download

**Frontend Behavior**: Show message "No tasks with due dates to export"

---

## Frontend Integration

### Button Component

```tsx
// components/CalendarExportButton.tsx
import { downloadCalendar } from '@/lib/api';

export function CalendarExportButton() {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    try {
      setIsExporting(true);
      const blob = await downloadCalendar();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tasks-${new Date().toISOString().split('T')[0]}.ics`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success('Calendar file downloaded');
    } catch (error) {
      toast.error('Failed to export calendar');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={isExporting}
      className="btn-secondary"
    >
      {isExporting ? 'Exporting...' : 'Export to Calendar'}
    </button>
  );
}
```

### API Client Function

```typescript
// lib/api.ts
export async function downloadCalendar(
  filters?: {
    includeCompleted?: boolean;
    dateRangeStart?: string;
    dateRangeEnd?: string;
  }
): Promise<Blob> {
  const params = new URLSearchParams();
  if (filters?.includeCompleted) params.append('include_completed', 'true');
  if (filters?.dateRangeStart) params.append('date_range_start', filters.dateRangeStart);
  if (filters?.dateRangeEnd) params.append('date_range_end', filters.dateRangeEnd);

  const response = await fetch(
    `${API_BASE_URL}/calendar/export?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Accept': 'text/calendar',
      },
    }
  );

  if (response.status === 204) {
    throw new Error('No tasks with due dates to export');
  }

  if (!response.ok) {
    throw new Error('Failed to export calendar');
  }

  return response.blob();
}
```

---

## Importing into Calendar Apps

### Google Calendar

1. User downloads `tasks-2025-12-30.ics` file
2. Opens Google Calendar (web or mobile)
3. Clicks Settings → Import & Export → Select file
4. Uploads the .ics file
5. Tasks appear as events in Google Calendar

**Result**: Each task becomes a calendar event at its due date/time

### Apple Calendar (iOS/macOS)

1. User downloads .ics file
2. Double-clicks the file (or opens in Mail)
3. iOS/macOS Calendar app opens
4. User confirms import
5. Tasks appear in default calendar

### Outlook (Desktop/Web)

1. User downloads .ics file
2. Opens Outlook Calendar
3. File → Import → Select .ics file
4. Outlook imports events into selected calendar

---

## Implementation Notes

### Timezone Handling

**Storage**: All `due_date` values are stored in UTC in database
**Export**: .ics file uses UTC timestamps (indicated by `Z` suffix: `20260105T150000Z`)
**Import**: Calendar apps convert UTC to user's local timezone automatically

### Event Updates

**Important**: .ics export is a **one-time snapshot**

- If user updates a task's due date after exporting, the calendar event is NOT automatically updated
- User must **re-export and re-import** to sync changes
- Each re-import creates **duplicate events** (unless user deletes old events first)

**Future Enhancement**: Consider adding `LAST-MODIFIED` property to help calendar apps detect changes

### File Naming Convention

**Format**: `tasks-{YYYY-MM-DD}.ics`

**Example**: `tasks-2025-12-30.ics`

**Rationale**: Date in filename helps users identify when the export was created

---

## Error Handling

### Backend Validation

```python
from fastapi import HTTPException

@router.get("/calendar/export")
async def export_calendar(
    include_completed: bool = False,
    date_range_start: datetime | None = None,
    date_range_end: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Validate date range
    if date_range_start and date_range_end:
        if date_range_start > date_range_end:
            raise HTTPException(400, "Invalid date range: start must be before end")

    # Query tasks
    query = select(Task).where(
        Task.user_id == current_user.id,
        Task.due_date.is_not(None)
    )

    if not include_completed:
        query = query.where(Task.completed == False)

    if date_range_start:
        query = query.where(Task.due_date >= date_range_start)

    if date_range_end:
        query = query.where(Task.due_date <= date_range_end)

    tasks = db.exec(query).all()

    if not tasks:
        return Response(status_code=204)  # No content

    # Generate .ics file
    ics_content = generate_ics(tasks)

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=tasks-{date.today()}.ics"
        }
    )
```

---

## Performance Considerations

### Query Optimization

**Indexes Used**:
- `task.user_id` (existing)
- `task.due_date` (new index from migration)
- `task.completed` (existing)

**Query Example** (optimized with indexes):
```sql
SELECT * FROM task
WHERE user_id = 45
  AND due_date IS NOT NULL
  AND completed = false
ORDER BY due_date ASC;
-- Uses: idx_task_user_id + idx_task_due_date + idx_task_completed
```

### File Size Limits

**Typical Sizes**:
- 100 tasks ≈ 15 KB
- 1,000 tasks ≈ 150 KB
- 10,000 tasks ≈ 1.5 MB

**Recommendation**: No hard limit needed (users unlikely to have 10k+ tasks with due dates)

**Future Enhancement**: If file size becomes an issue, add pagination or date range requirement

---

## Summary

**Single endpoint**: `GET /api/v1/calendar/export`

**Features**:
- Generates RFC 5545-compliant .ics files
- Compatible with all major calendar applications
- Optional filtering by completion status and date range
- Timezone-safe (UTC export, calendar apps handle local conversion)
- Graceful handling when no tasks exist

**Limitations** (by design):
- One-time export (no real-time sync)
- Re-importing creates duplicates
- No automatic update propagation

**Use Case**: Users who want to see task deadlines in their existing calendar workflow (Google Calendar, Apple Calendar, Outlook)
