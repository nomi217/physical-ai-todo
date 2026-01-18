# API Contract: Task Endpoints (Extended)

**Feature**: 006-task-reminders
**Date**: 2025-12-30
**Base Path**: `/api/v1/tasks`

## Overview

This document specifies the API changes to the existing Task endpoints to support due dates and reminders. Existing endpoints are extended to accept new fields.

---

## Endpoint 1: Create Task (EXTENDED)

### `POST /api/v1/tasks`

**Description**: Create a new task with optional due date and reminder

**Authentication**: Required (JWT)

### Request

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body** (existing fields + new fields):
```json
{
  "title": "Submit quarterly report",
  "description": "Compile Q4 financial data and submit to board",
  "priority": "high",
  "tags": ["work", "finance"],

  // NEW: Due date and reminder fields
  "due_date": "2026-01-05T15:00:00Z",           // ISO 8601, optional
  "reminder_offset": "1d"                        // "1h"|"1d"|"3d"|"5d"|"1w"|"never"|null, optional
}
```

**Validation Rules**:
- `due_date`: Must be ISO 8601 datetime string, must be in the future (if provided)
- `reminder_offset`: Must be one of: "1h", "1d", "3d", "5d", "1w", "never", or null
- If `reminder_offset` is provided, `due_date` must also be provided
- Calculated `reminder_time` must be in the future (server validates)

### Response

**Success (201 Created)**:
```json
{
  "id": 123,
  "user_id": 45,
  "title": "Submit quarterly report",
  "description": "Compile Q4 financial data and submit to board",
  "completed": false,
  "priority": "high",
  "tags": ["work", "finance"],
  "display_order": 10,
  "is_template": false,
  "created_at": "2025-12-30T10:00:00Z",
  "updated_at": "2025-12-30T10:00:00Z",

  // NEW: Returned reminder fields
  "due_date": "2026-01-05T15:00:00Z",
  "reminder_offset": "1d",
  "reminder_time": "2026-01-04T15:00:00Z"       // Calculated by backend
}
```

**Error Responses**:

**400 Bad Request** - Invalid input:
```json
{
  "detail": "Due date must be in the future"
}
```
```json
{
  "detail": "Reminder time would be in the past with this offset"
}
```
```json
{
  "detail": "Reminder offset requires a due date"
}
```

**401 Unauthorized** - Missing/invalid JWT:
```json
{
  "detail": "Not authenticated"
}
```

---

## Endpoint 2: Update Task (EXTENDED)

### `PUT /api/v1/tasks/{task_id}`

**Description**: Full replacement of task including due date/reminder changes

**Authentication**: Required (JWT, task owner only)

### Request

**Path Parameters**:
- `task_id` (integer): ID of the task to update

**Body**: Same as Create Task (all fields required for PUT)

### Response

**Success (200 OK)**: Same structure as Create Task response

**Notes**:
- If `due_date` or `reminder_offset` changes, backend recalculates `reminder_time`
- If previous reminder was scheduled and time changes, old scheduler job is cancelled
- Returns updated `reminder_time` in response

---

## Endpoint 3: Patch Task (EXTENDED)

### `PATCH /api/v1/tasks/{task_id}`

**Description**: Partial update of task (can update only due date/reminder without changing other fields)

**Authentication**: Required (JWT, task owner only)

### Request

**Path Parameters**:
- `task_id` (integer): ID of the task to update

**Body** (all fields optional):
```json
{
  "due_date": "2026-01-10T14:00:00Z",  // Update due date only
  "reminder_offset": "3d"               // Update reminder offset only
}
```

**Use Cases**:
- Update only `due_date`: `{"due_date": "2026-01-10T14:00:00Z"}`
- Remove reminder: `{"reminder_offset": "never"}` or `{"reminder_offset": null}`
- Change offset: `{"reminder_offset": "1w"}`
- Remove due date: `{"due_date": null}` (also removes reminder)

### Response

**Success (200 OK)**: Full task object with updated fields

**Notes**:
- Setting `due_date` to null also clears `reminder_offset` and `reminder_time`
- Setting `reminder_offset` to "never" or null clears `reminder_time` but keeps `due_date`

---

## Endpoint 4: Get Tasks (EXTENDED)

### `GET /api/v1/tasks`

**Description**: List tasks with optional filtering, now includes due date/reminder data

**Authentication**: Required (JWT)

### Request

**Query Parameters** (existing + new):
```
?limit=50
&offset=0
&search=report
&completed=false
&priority=high
&tags=work,finance
&sort=due_date             // NEW: Can sort by due_date
&order=asc                 // NEW: Sort order for due_date
```

**New Query Parameters**:
- `sort=due_date`: Sort by due date (upcoming first with `order=asc`)
- Filter by overdue status (future enhancement, not in MVP)

### Response

**Success (200 OK)**:
```json
{
  "items": [
    {
      "id": 123,
      "title": "Submit quarterly report",
      // ... all task fields ...
      "due_date": "2026-01-05T15:00:00Z",
      "reminder_offset": "1d",
      "reminder_time": "2026-01-04T15:00:00Z"
    },
    {
      "id": 124,
      "title": "Review contract",
      // ... all task fields ...
      "due_date": null,              // No due date set
      "reminder_offset": null,
      "reminder_time": null
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

**Notes**:
- Tasks without due dates have `due_date`, `reminder_offset`, `reminder_time` as `null`
- Frontend can detect overdue by comparing `due_date < now()`

---

## Endpoint 5: Get Single Task (EXTENDED)

### `GET /api/v1/tasks/{task_id}`

**Description**: Get task details including due date and reminder info

**Authentication**: Required (JWT, task owner only)

### Response

**Success (200 OK)**: Same structure as Create Task response, includes all reminder fields

---

## Data Flow Examples

### Example 1: Create Task with Reminder

**Request**:
```http
POST /api/v1/tasks
Content-Type: application/json
Authorization: Bearer eyJ...

{
  "title": "Dentist appointment",
  "due_date": "2026-01-15T14:00:00Z",
  "reminder_offset": "1h"
}
```

**Backend Processing**:
1. Validate: `due_date` is in future ✓
2. Validate: `reminder_offset` is valid ✓
3. Calculate: `reminder_time = 2026-01-15T14:00:00Z - 1 hour = 2026-01-15T13:00:00Z`
4. Validate: `reminder_time` is in future ✓
5. Create task record with all fields
6. No immediate scheduler action (APScheduler polls every 60s)

**Response**:
```json
{
  "id": 125,
  "title": "Dentist appointment",
  "due_date": "2026-01-15T14:00:00Z",
  "reminder_offset": "1h",
  "reminder_time": "2026-01-15T13:00:00Z",
  // ... other fields ...
}
```

### Example 2: Update Reminder Offset

**Request**:
```http
PATCH /api/v1/tasks/125
Content-Type: application/json

{
  "reminder_offset": "3d"
}
```

**Backend Processing**:
1. Fetch existing task (due_date = "2026-01-15T14:00:00Z")
2. Recalculate: `reminder_time = 2026-01-15T14:00:00Z - 3 days = 2026-01-12T14:00:00Z`
3. Validate: New reminder_time is in future ✓
4. Update task record
5. (Scheduler will pick up new time on next poll)

**Response**:
```json
{
  "id": 125,
  "due_date": "2026-01-15T14:00:00Z",
  "reminder_offset": "3d",
  "reminder_time": "2026-01-12T14:00:00Z",  // Updated
  // ... other fields ...
}
```

### Example 3: Remove Reminder (Keep Due Date)

**Request**:
```http
PATCH /api/v1/tasks/125

{
  "reminder_offset": "never"
}
```

**Backend Processing**:
1. Set `reminder_offset = null`
2. Set `reminder_time = null`
3. Keep `due_date` unchanged

**Response**:
```json
{
  "id": 125,
  "due_date": "2026-01-15T14:00:00Z",        // Unchanged
  "reminder_offset": null,                   // Removed
  "reminder_time": null,                     // Removed
  // ... other fields ...
}
```

---

## Error Scenarios

### Scenario 1: Due Date in the Past

**Request**:
```json
{
  "due_date": "2020-01-01T12:00:00Z"
}
```

**Response (400)**:
```json
{
  "detail": "Due date must be in the future"
}
```

### Scenario 2: Reminder Offset Too Large

**Request**:
```json
{
  "due_date": "2026-01-02T10:00:00Z",  // 2 days from now
  "reminder_offset": "1w"               // 7 days before
}
```

**Response (400)**:
```json
{
  "detail": "Reminder time would be in the past with this offset"
}
```

### Scenario 3: Reminder Without Due Date

**Request**:
```json
{
  "title": "Task without due date",
  "reminder_offset": "1d"               // No due_date provided
}
```

**Response (400)**:
```json
{
  "detail": "Reminder offset requires a due date"
}
```

---

## Backward Compatibility

**All new fields are optional and nullable**:
- Existing API clients that don't send `due_date` or `reminder_offset` continue working unchanged
- Tasks created without these fields have `null` values, no reminder behavior
- Existing tasks in database get `null` values for new fields after migration

**No breaking changes** to existing task endpoints.
