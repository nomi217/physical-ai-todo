# Quickstart: Task Reminders and In-App Notifications

**Feature**: 006-task-reminders
**Date**: 2025-12-30
**For**: Developers implementing this feature

## Overview

This quickstart guide provides step-by-step instructions for implementing the task reminders and notifications feature. Follow the order below for smooth implementation.

---

## Prerequisites

Before starting implementation, ensure:

- [x] Phase II web application is deployed and working
- [x] Neon PostgreSQL database is accessible
- [x] FastAPI backend is running
- [x] Next.js frontend is running
- [x] User authentication (JWT) is working
- [x] You have completed `/sp.tasks` to break down into actionable tasks

---

## Step 1: Backend Setup

### 1.1 Install Dependencies

Add to `backend/requirements.txt`:
```txt
apscheduler==3.10.4
icalendar==5.0.11
```

Install:
```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Database Migration

Generate migration script:
```bash
cd backend
alembic revision --autogenerate -m "Add reminders and notifications"
```

Review the generated migration in `backend/alembic/versions/`, then apply:
```bash
alembic upgrade head
```

**Verify** tables created:
```sql
-- Should see new columns in task table
\d task

-- Should see new notification table
\d notification
```

---

## Step 2: Backend Implementation

### 2.1 Extend Models (`app/models.py`)

Add new fields to `Task` model and create `Notification` model:

```python
# See data-model.md for complete SQLModel definitions

class Task(SQLModel, table=True):
    # ... existing fields ...

    # NEW fields
    due_date: datetime | None = Field(default=None, index=True)
    reminder_offset: str | None = Field(default=None, max_length=10)
    reminder_time: datetime | None = Field(default=None, index=True)
    last_reminder_sent: datetime | None = None
    last_overdue_notification_sent: datetime | None = None

class Notification(SQLModel, table=True):
    # See data-model.md for complete schema
    ...
```

### 2.2 Update Schemas (`app/schemas.py`)

Add Pydantic validation schemas:

```python
from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    tags: list[str] | None = None

    # NEW fields
    due_date: datetime | None = None
    reminder_offset: str | None = None

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v and v <= datetime.now():
            raise ValueError('Due date must be in the future')
        return v

    # See data-model.md for complete validation logic
```

### 2.3 Create Reminder Calculator (`app/utils/reminder_calculator.py`)

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

    if reminder_time <= datetime.now():
        raise ValueError("Reminder time would be in the past")

    return reminder_time
```

### 2.4 Create Scheduler (`app/scheduler.py`)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
from sqlmodel import select
from app.models import Task, Notification
from app.database import get_session

scheduler = AsyncIOScheduler()

def init_scheduler(database_url: str):
    jobstore = SQLAlchemyJobStore(url=database_url)
    scheduler.add_jobstore(jobstore)

    @scheduler.scheduled_job('interval', seconds=60, id='check_reminders')
    async def check_reminders():
        async with get_session() as db:
            now = datetime.now()

            # Check for due reminders
            reminder_tasks = await db.exec(
                select(Task).where(
                    Task.reminder_time <= now,
                    Task.last_reminder_sent.is_(None),
                    Task.completed == False
                )
            ).all()

            for task in reminder_tasks:
                # Create notification
                notification = Notification(
                    user_id=task.user_id,
                    task_id=task.id,
                    type="reminder",
                    title=task.title,
                    message=f"Task is due soon",
                    is_read=False
                )
                db.add(notification)
                task.last_reminder_sent = now

            # Check for overdue tasks
            overdue_tasks = await db.exec(
                select(Task).where(
                    Task.due_date <= now,
                    Task.completed == False,
                    Task.last_overdue_notification_sent.is_(None)
                )
            ).all()

            for task in overdue_tasks:
                notification = Notification(
                    user_id=task.user_id,
                    task_id=task.id,
                    type="overdue",
                    title=task.title,
                    message="This task is overdue",
                    is_read=False
                )
                db.add(notification)
                task.last_overdue_notification_sent = now

            await db.commit()

    scheduler.start()
    return scheduler
```

### 2.5 Update Main App (`app/main.py`)

```python
from contextlib import asynccontextmanager
from app.scheduler import init_scheduler, scheduler
from app.database import DATABASE_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_scheduler(DATABASE_URL)
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# Include new routes
from app.routes import notifications, calendar_export

app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])
app.include_router(calendar_export.router, prefix="/api/v1", tags=["calendar"])
```

### 2.6 Create Notification Routes (`app/routes/notifications.py`)

```python
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
# See contracts/notifications-api.md for complete implementation

router = APIRouter()

@router.get("/notifications")
async def get_notifications(...):
    ...

@router.patch("/notifications/{notification_id}")
async def mark_as_read(...):
    ...

# ... other endpoints
```

### 2.7 Create Calendar Export Route (`app/routes/calendar_export.py`)

```python
from fastapi import APIRouter, Response
from icalendar import Calendar, Event
# See contracts/calendar-export-api.md for complete implementation

router = APIRouter()

@router.get("/calendar/export")
async def export_calendar(...):
    ...
```

---

## Step 3: Frontend Implementation

### 3.1 Install Dependencies

Add to `frontend/package.json`:
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

Install:
```bash
cd frontend
npm install
```

### 3.2 Update Types (`lib/types.ts`)

```typescript
export interface Task {
  // ... existing fields ...

  // NEW fields
  due_date?: string;
  reminder_offset?: "1h" | "1d" | "3d" | "5d" | "1w" | null;
  reminder_time?: string;
}

export interface Notification {
  id: number;
  user_id: number;
  task_id: number;
  type: "reminder" | "overdue";
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}
```

### 3.3 Extend TaskForm (`components/TaskForm.tsx`)

Add due date picker and reminder offset dropdown:

```tsx
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

export default function TaskForm({ ... }) {
  const [dueDate, setDueDate] = useState<Date | null>(null);
  const [reminderOffset, setReminderOffset] = useState<string>('never');

  return (
    <form>
      {/* Existing fields... */}

      {/* Due Date Picker */}
      <div>
        <label>Due Date</label>
        <DatePicker
          selected={dueDate}
          onChange={(date) => setDueDate(date)}
          showTimeSelect
          timeIntervals={15}
          dateFormat="MMM d, yyyy h:mm aa"
          minDate={new Date()}
          placeholderText="Select due date"
        />
      </div>

      {/* Reminder Offset (only shown if due date set) */}
      {dueDate && (
        <div>
          <label>Remind Me</label>
          <select value={reminderOffset} onChange={(e) => setReminderOffset(e.target.value)}>
            <option value="never">Never</option>
            <option value="1h">1 hour before</option>
            <option value="1d">1 day before</option>
            <option value="3d">3 days before</option>
            <option value="5d">5 days before</option>
            <option value="1w">1 week before</option>
          </select>
        </div>
      )}
    </form>
  );
}
```

### 3.4 Create Notification Dropdown (`components/NotificationDropdown.tsx`)

```tsx
import { useNotifications } from '@/hooks/useNotifications';

export function NotificationDropdown() {
  const { notifications, unreadCount, markAsRead, markAllRead } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      {/* Bell Icon with Badge */}
      <button onClick={() => setIsOpen(!isOpen)} className="relative">
        🔔
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 text-xs">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white shadow-lg rounded-lg">
          <div className="p-4 border-b flex justify-between">
            <h3>Notifications</h3>
            <button onClick={() => markAllRead.mutate()}>Mark all read</button>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.map(notification => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onRead={() => markAsRead.mutate(notification.id)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

### 3.5 Create useNotifications Hook (`hooks/useNotifications.ts`)

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchNotifications, markNotificationRead, markAllNotificationsRead } from '@/lib/api';

export function useNotifications() {
  const queryClient = useQueryClient();

  const { data: notifications } = useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: () => fetchNotifications({ isRead: false }),
    refetchInterval: 60000, // Poll every 60 seconds
  });

  const { data: unreadCount } = useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: fetchUnreadCount,
    refetchInterval: 60000,
  });

  const markAsRead = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      queryClient.invalidateQueries(['notifications', 'unread-count']);
    },
  });

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

### 3.6 Add API Functions (`lib/api.ts`)

```typescript
export async function fetchNotifications(filters: { isRead?: boolean }) {
  const params = new URLSearchParams();
  if (filters.isRead !== undefined) params.append('is_read', String(filters.isRead));

  const response = await fetch(`${API_BASE_URL}/notifications?${params}`, {
    headers: { 'Authorization': `Bearer ${getToken()}` },
  });
  return response.json();
}

export async function fetchUnreadCount() {
  const response = await fetch(`${API_BASE_URL}/notifications/unread-count`, {
    headers: { 'Authorization': `Bearer ${getToken()}` },
  });
  return response.json();
}

export async function markNotificationRead(id: number) {
  await fetch(`${API_BASE_URL}/notifications/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ is_read: true }),
  });
}

export async function downloadCalendar() {
  const response = await fetch(`${API_BASE_URL}/calendar/export`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Accept': 'text/calendar',
    },
  });
  return response.blob();
}
```

### 3.7 Update Dashboard (`app/dashboard/page.tsx`)

Add notification icon to top nav:

```tsx
import { NotificationDropdown } from '@/components/NotificationDropdown';

export default function DashboardPage() {
  return (
    <div>
      {/* Top Navigation */}
      <nav className="flex justify-between items-center">
        <h1>My Tasks</h1>
        <div className="flex items-center gap-4">
          <NotificationDropdown />
          {/* Other nav items */}
        </div>
      </nav>

      {/* Rest of dashboard */}
    </div>
  );
}
```

---

## Step 4: Testing

### 4.1 Backend Tests

Create `backend/tests/test_reminders.py`:
```python
import pytest
from app.utils.reminder_calculator import calculate_reminder_time
from datetime import datetime, timedelta

def test_calculate_reminder_time_1h():
    due_date = datetime.now() + timedelta(hours=2)
    reminder = calculate_reminder_time(due_date, "1h")
    assert reminder == due_date - timedelta(hours=1)

def test_reminder_in_past_raises_error():
    due_date = datetime.now() + timedelta(minutes=30)
    with pytest.raises(ValueError, match="would be in the past"):
        calculate_reminder_time(due_date, "1d")
```

Run tests:
```bash
cd backend
pytest tests/test_reminders.py -v
```

### 4.2 Frontend Tests

Create `frontend/components/__tests__/NotificationDropdown.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import { NotificationDropdown } from '../NotificationDropdown';

test('displays unread count badge', () => {
  render(<NotificationDropdown />);
  expect(screen.getByText('3')).toBeInTheDocument();
});
```

Run tests:
```bash
cd frontend
npm test
```

---

## Step 5: Manual Testing

### 5.1 Test Reminder Creation

1. Open frontend: `http://localhost:3000/dashboard`
2. Click "New Task"
3. Set title: "Test reminder"
4. Set due date: Tomorrow at 2 PM
5. Select reminder: "1 day before"
6. Submit
7. **Verify**: Task shows due date badge

### 5.2 Test Notification Trigger

1. Update test task's `reminder_time` to 1 minute from now (via database)
2. Wait 60 seconds (scheduler runs)
3. **Verify**: Bell icon shows unread count "1"
4. Click bell icon
5. **Verify**: Notification appears in dropdown
6. Click notification
7. **Verify**: Navigates to task, notification marked as read

### 5.3 Test Calendar Export

1. Create 3 tasks with different due dates
2. Click "Export to Calendar" button
3. **Verify**: .ics file downloads
4. Import file into Google Calendar
5. **Verify**: 3 events appear at correct dates/times

---

## Step 6: Deployment

### 6.1 Backend Deployment

```bash
# Push to git
git add backend/
git commit -m "feat(reminders): Add task reminders and notifications backend"
git push origin 006-task-reminders

# Deploy to DigitalOcean
kubectl apply -f kubernetes/production/deployments/backend.yaml

# Run migrations
kubectl exec -it backend-pod -- alembic upgrade head
```

### 6.2 Frontend Deployment

```bash
# Build frontend
cd frontend
npm run build

# Push to git
git add frontend/
git commit -m "feat(reminders): Add task reminders and notifications UI"
git push origin 006-task-reminders

# Deploy frontend
kubectl apply -f kubernetes/production/deployments/frontend.yaml
```

---

## Troubleshooting

### Issue: Scheduler not running

**Check logs**:
```bash
kubectl logs backend-pod | grep scheduler
```

**Solution**: Ensure lifespan context manager is working:
```python
# In main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_scheduler(DATABASE_URL)
    print("✓ Scheduler started")  # Should see this in logs
    yield
```

### Issue: Notifications not appearing

**Check database**:
```sql
SELECT * FROM notification WHERE user_id = <your_id>;
```

**Check frontend polling**:
- Open DevTools → Network tab
- Should see requests to `/notifications/unread-count` every 60 seconds

### Issue: .ics file doesn't import

**Validate .ics format**:
- Open file in text editor
- Ensure it starts with `BEGIN:VCALENDAR`
- Ensure each event has `UID`, `DTSTART`, `DTEND`, `SUMMARY`

---

## Next Steps

After completing implementation:

1. ✅ Run `/sp.implement` to generate all code
2. ✅ Test locally (backend + frontend)
3. ✅ Deploy to staging environment
4. ✅ User acceptance testing
5. ✅ Deploy to production
6. ✅ Create PHR documenting the implementation

**Ready to start implementation!**
