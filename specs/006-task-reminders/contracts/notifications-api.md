# API Contract: Notifications Endpoints (NEW)

**Feature**: 006-task-reminders
**Date**: 2025-12-30
**Base Path**: `/api/v1/notifications`

## Overview

This document specifies the new Notifications API endpoints for managing in-app notifications triggered by task reminders and overdue status.

---

## Endpoint 1: Get Notifications

### `GET /api/v1/notifications`

**Description**: Get user's notifications with optional filtering

**Authentication**: Required (JWT)

### Request

**Query Parameters**:
```
?is_read=false      // Filter by read status (true|false, optional)
&limit=50           // Max notifications to return (default 50, max 100)
&offset=0           // Pagination offset (default 0)
&type=reminder      // Filter by type: "reminder"|"overdue" (optional)
```

### Response

**Success (200 OK)**:
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 45,
      "task_id": 123,
      "type": "reminder",
      "title": "Submit quarterly report",
      "message": "Task is due tomorrow at 3:00 PM",
      "is_read": false,
      "created_at": "2026-01-04T15:00:00Z"
    },
    {
      "id": 2,
      "user_id": 45,
      "task_id": 124,
      "type": "overdue",
      "title": "Review contract",
      "message": "This task is overdue",
      "is_read": false,
      "created_at": "2026-01-03T10:00:00Z"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0,
  "unread_count": 2
}
```

**Response Fields**:
- `items`: Array of notification objects
- `total`: Total count of notifications matching filter
- `limit`: Requested limit (for pagination)
- `offset`: Requested offset (for pagination)
- `unread_count`: Count of unread notifications (for badge display)

---

## Endpoint 2: Get Unread Count

### `GET /api/v1/notifications/unread-count`

**Description**: Get count of unread notifications (for badge display)

**Authentication**: Required (JWT)

### Response

**Success (200 OK)**:
```json
{
  "unread_count": 3
}
```

**Use Case**: Frontend polls this endpoint every 60 seconds to update bell icon badge

---

## Endpoint 3: Mark Notification as Read

### `PATCH /api/v1/notifications/{notification_id}`

**Description**: Mark a single notification as read or unread

**Authentication**: Required (JWT, notification owner only)

### Request

**Path Parameters**:
- `notification_id` (integer): ID of the notification

**Body**:
```json
{
  "is_read": true
}
```

### Response

**Success (200 OK)**:
```json
{
  "id": 1,
  "user_id": 45,
  "task_id": 123,
  "type": "reminder",
  "title": "Submit quarterly report",
  "message": "Task is due tomorrow at 3:00 PM",
  "is_read": true,              // Updated
  "created_at": "2026-01-04T15:00:00Z"
}
```

**Error Responses**:

**404 Not Found** - Notification doesn't exist or user doesn't own it:
```json
{
  "detail": "Notification not found"
}
```

---

## Endpoint 4: Mark All as Read

### `POST /api/v1/notifications/mark-all-read`

**Description**: Mark all user's notifications as read

**Authentication**: Required (JWT)

### Request

**Body**: None required

### Response

**Success (200 OK)**:
```json
{
  "updated_count": 5,
  "message": "All notifications marked as read"
}
```

**Use Case**: "Mark all as read" button in notification dropdown

---

## Endpoint 5: Delete Notification

### `DELETE /api/v1/notifications/{notification_id}`

**Description**: Delete a single notification

**Authentication**: Required (JWT, notification owner only)

### Request

**Path Parameters**:
- `notification_id` (integer): ID of the notification to delete

### Response

**Success (204 No Content)**: No response body

**Error Responses**:

**404 Not Found** - Notification doesn't exist or user doesn't own it:
```json
{
  "detail": "Notification not found"
}
```

---

## Endpoint 6: Delete All Read Notifications

### `DELETE /api/v1/notifications/read`

**Description**: Delete all read notifications for the current user

**Authentication**: Required (JWT)

### Response

**Success (200 OK)**:
```json
{
  "deleted_count": 12,
  "message": "Deleted 12 read notifications"
}
```

**Use Case**: "Clear all read" button to clean up notification list

---

## Data Flow Examples

### Example 1: Frontend Notification Polling

**1. Frontend polls for unread count** (every 60 seconds):
```http
GET /api/v1/notifications/unread-count
Authorization: Bearer eyJ...
```

**Response**:
```json
{
  "unread_count": 3
}
```

**Frontend Action**: Update bell icon badge to show "3"

---

**2. User clicks bell icon** → Fetch unread notifications:
```http
GET /api/v1/notifications?is_read=false&limit=20
Authorization: Bearer eyJ...
```

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "task_id": 123,
      "type": "reminder",
      "title": "Submit quarterly report",
      "message": "Task is due tomorrow at 3:00 PM",
      "is_read": false,
      "created_at": "2026-01-04T15:00:00Z"
    },
    // ... 2 more notifications
  ],
  "total": 3,
  "unread_count": 3
}
```

**Frontend Action**: Display notifications in dropdown panel

---

**3. User clicks a notification**:
```http
PATCH /api/v1/notifications/1
Content-Type: application/json

{
  "is_read": true
}
```

**Response**:
```json
{
  "id": 1,
  "is_read": true,
  // ... other fields
}
```

**Frontend Actions**:
1. Navigate to task details page (`/dashboard?task=${task_id}`)
2. Update local cache (mark notification as read)
3. Decrement unread count badge

---

**4. User clicks "Mark all as read"**:
```http
POST /api/v1/notifications/mark-all-read
Authorization: Bearer eyJ...
```

**Response**:
```json
{
  "updated_count": 3,
  "message": "All notifications marked as read"
}
```

**Frontend Actions**:
1. Update all notifications in local cache to `is_read: true`
2. Set badge count to 0

---

### Example 2: Scheduler Creates Notification

**Background Process** (APScheduler job runs every 60 seconds):

1. Scheduler queries tasks:
```sql
SELECT * FROM task
WHERE reminder_time <= NOW()
  AND last_reminder_sent IS NULL;
```

2. For each matched task, create notification:
```python
notification = Notification(
    user_id=task.user_id,
    task_id=task.id,
    type="reminder",
    title=task.title,
    message=f"Task is due {format_relative_time(task.due_date)}",
    is_read=False,
    created_at=datetime.now()
)
db.add(notification)
```

3. Update task to prevent duplicate:
```python
task.last_reminder_sent = datetime.now()
db.commit()
```

4. Frontend polls and detects new notification on next 60-second interval

---

## Authorization

**All endpoints require valid JWT token**:
- User can only access their own notifications (`user_id` from JWT)
- Attempting to access another user's notification returns 404

**Example Authorization Check** (backend logic):
```python
from fastapi import Depends, HTTPException
from app.auth.dependencies import get_current_user

@router.get("/api/v1/notifications/{notification_id}")
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    notification = db.get(Notification, notification_id)

    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification
```

---

## Rate Limiting Considerations

**Recommendation**: Add rate limiting to prevent abuse

**Endpoints to Limit**:
- `PATCH /notifications/{id}`: 100 requests/minute (prevent spam toggling)
- `POST /notifications/mark-all-read`: 10 requests/minute (prevent spam clicking)
- `GET /notifications/unread-count`: 120 requests/minute (60-second poll + buffer)

**Implementation**: Use FastAPI middleware or Nginx rate limiting

---

## Notification Message Templates

**Reminder Type** (when `reminder_time` is reached):
```
"Task is due {relative_time}"
```

Examples:
- "Task is due in 1 hour"
- "Task is due tomorrow at 3:00 PM"
- "Task is due in 3 days"

**Overdue Type** (when `due_date` passed and task not completed):
```
"This task is overdue"
```

**Future Enhancement**: Customizable templates per user preference

---

## Frontend Integration Pattern

### React Query Hook

```typescript
// hooks/useNotifications.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useNotifications() {
  const queryClient = useQueryClient();

  // Fetch unread notifications
  const { data: notifications } = useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: () => fetchNotifications({ isRead: false }),
    refetchInterval: 60000, // Poll every 60 seconds
  });

  // Fetch unread count
  const { data: unreadCount } = useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: fetchUnreadCount,
    refetchInterval: 60000,
  });

  // Mark as read mutation
  const markAsRead = useMutation({
    mutationFn: (id: number) => markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      queryClient.invalidateQueries(['notifications', 'unread-count']);
    },
  });

  // Mark all as read mutation
  const markAllRead = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      queryClient.invalidateQueries(['notifications', 'unread-count']);
    },
  });

  return {
    notifications: notifications?.items || [],
    unreadCount: unreadCount?.unread_count || 0,
    markAsRead,
    markAllRead,
  };
}
```

---

## Summary

**6 new notification endpoints**:
1. `GET /notifications` - List with filtering
2. `GET /notifications/unread-count` - Badge count
3. `PATCH /notifications/{id}` - Mark single as read
4. `POST /notifications/mark-all-read` - Bulk mark as read
5. `DELETE /notifications/{id}` - Delete single
6. `DELETE /notifications/read` - Delete all read

**All endpoints authenticated with JWT**, user-scoped access only.
