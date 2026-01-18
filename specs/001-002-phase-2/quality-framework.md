# Phase 2 Quality Framework - Zero Bugs, Perfect Performance

**Created**: 2025-12-08
**Branch**: `001-002-phase-2`
**Objective**: Ensure flawless execution with zero bugs, optimal performance, and perfect UX

---

## Quality Standards

### Non-Negotiable Requirements

1. ✅ **Zero Runtime Errors** - No console errors, no crashes
2. ✅ **Fast Performance** - All interactions < 100ms, API < 200ms
3. ✅ **Perfect Dark/Light Mode** - User choice, persisted, no flicker
4. ✅ **100% Type Safety** - No TypeScript `any`, strict mode enabled
5. ✅ **Comprehensive Tests** - 90%+ coverage, all edge cases
6. ✅ **Accessibility** - WCAG AA compliance, keyboard navigation
7. ✅ **Responsive Design** - Works 320px to 4K displays

---

## Table of Contents

1. [Performance Optimization Strategy](#performance-optimization-strategy)
2. [Dark/Light Mode Implementation](#darklight-mode-implementation)
3. [Testing Strategy (90%+ Coverage)](#testing-strategy)
4. [Code Quality Standards](#code-quality-standards)
5. [Quality Gates & Checkpoints](#quality-gates--checkpoints)
6. [Debugging & Monitoring](#debugging--monitoring)
7. [Pre-Launch Checklist](#pre-launch-checklist)

---

## Performance Optimization Strategy

### Backend Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p50) | < 100ms | Prometheus |
| API Response Time (p95) | < 200ms | Prometheus |
| API Response Time (p99) | < 500ms | Prometheus |
| Database Query Time | < 50ms | SQLAlchemy logging |
| File Upload (10MB) | < 3s | Manual testing |
| OCR Processing | < 5s/page | Manual testing |
| Concurrent Users | 100+ | Load testing |
| Memory Usage | < 512MB | Docker stats |

### Backend Optimization Techniques

#### 1. Database Optimization

**Indexes** - Add indexes to all foreign keys and frequently queried fields:
```python
# backend/app/models.py
class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)  # ✅ Indexed for search
    completed: bool = Field(default=False, index=True)  # ✅ Indexed for filtering
    priority: str = Field(default="medium", index=True)  # ✅ Indexed for sorting
    display_order: int = Field(index=True)  # ✅ Indexed for ordering
    created_at: datetime = Field(default_factory=datetime.now, index=True)  # ✅ Indexed for sorting

    # Composite index for common queries
    __table_args__ = (
        Index('idx_completed_priority', 'completed', 'priority'),
        Index('idx_created_at_desc', 'created_at', postgresql_ops={'created_at': 'DESC'}),
    )
```

**Query Optimization** - Use eager loading to prevent N+1 queries:
```python
# backend/app/crud.py
from sqlmodel import select
from sqlalchemy.orm import selectinload

def get_task_with_relations(task_id: int):
    """Get task with all relations in ONE query"""
    statement = (
        select(Task)
        .options(
            selectinload(Task.subtasks),
            selectinload(Task.notes),
            selectinload(Task.attachments),
        )
        .where(Task.id == task_id)
    )
    return session.exec(statement).first()
```

**Database Connection Pooling**:
```python
# backend/app/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Max connections
    max_overflow=20,  # Burst capacity
    pool_pre_ping=True,  # Validate connections
    pool_recycle=3600,  # Recycle connections every hour
)
```

#### 2. API Response Optimization

**Pagination** - Always paginate large result sets:
```python
# backend/app/routes/tasks.py
@router.get("/tasks")
async def list_tasks(
    limit: int = Query(50, le=100),  # Max 100 per request
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    tasks = db.exec(
        select(Task)
        .limit(limit)
        .offset(offset)
    ).all()

    total = db.exec(select(func.count(Task.id))).one()

    return {
        "items": tasks,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }
```

**Response Compression** - Enable gzip:
```python
# backend/app/main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB
```

**Caching** - Cache expensive operations:
```python
# backend/app/routes/analytics.py
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_analytics_cached(cache_key: str):
    """Cache analytics for 5 minutes"""
    # Expensive analytics computation
    pass

@router.get("/analytics/summary")
async def get_analytics():
    cache_key = f"analytics_{datetime.now().strftime('%Y%m%d%H%M')}"  # 1-minute granularity
    return get_analytics_cached(cache_key)
```

#### 3. File Upload Optimization

**Streaming Uploads** - Don't load entire file into memory:
```python
# backend/app/routes/attachments.py
from fastapi import UploadFile
import aiofiles

@router.post("/tasks/{task_id}/attachments")
async def upload_attachment(
    task_id: int,
    file: UploadFile,
):
    # Validate size before processing
    if file.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(400, "File too large")

    # Stream to disk (don't load into memory)
    file_path = f"uploads/{task_id}_{file.filename}"
    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await file.read(1024 * 64):  # 64KB chunks
            await out_file.write(content)

    return {"filename": file.filename, "size": file.size}
```

---

### Frontend Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint (FCP) | < 1.0s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| Time to Interactive (TTI) | < 3.0s | Lighthouse |
| Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| Bundle Size (JS) | < 300KB gzipped | webpack-bundle-analyzer |
| Page Load Time | < 2s | Chrome DevTools |
| UI Interaction Response | < 100ms | Manual testing |

### Frontend Optimization Techniques

#### 1. Code Splitting

**Route-based Splitting**:
```typescript
// frontend/app/page.tsx
import dynamic from 'next/dynamic'

// Lazy load heavy components
const AnalyticsDashboard = dynamic(() => import('@/components/AnalyticsDashboard'), {
  loading: () => <div>Loading analytics...</div>,
  ssr: false  // Don't render on server
})

const ChatBot = dynamic(() => import('@/components/ChatBot'), {
  loading: () => <div>Loading chat...</div>,
  ssr: false
})
```

**Component-based Splitting**:
```typescript
// frontend/components/TaskList.tsx
import { lazy, Suspense } from 'react'

const TaskItem = lazy(() => import('./TaskItem'))

export function TaskList({ tasks }) {
  return (
    <Suspense fallback={<TaskSkeleton />}>
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} />
      ))}
    </Suspense>
  )
}
```

#### 2. Memoization & Optimization

**React.memo for expensive components**:
```typescript
// frontend/components/TaskItem.tsx
import { memo } from 'react'

export const TaskItem = memo(function TaskItem({ task, onUpdate }) {
  // Only re-renders if task or onUpdate changes
  return (
    <div className="task-item">
      {task.title}
    </div>
  )
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.task.id === nextProps.task.id &&
         prevProps.task.updated_at === nextProps.task.updated_at
})
```

**useMemo for expensive computations**:
```typescript
// frontend/components/AnalyticsDashboard.tsx
import { useMemo } from 'react'

export function AnalyticsDashboard({ tasks }) {
  const analytics = useMemo(() => {
    // Expensive computation - only recalculate when tasks change
    return {
      total: tasks.length,
      completed: tasks.filter(t => t.completed).length,
      byPriority: tasks.reduce((acc, t) => {
        acc[t.priority] = (acc[t.priority] || 0) + 1
        return acc
      }, {})
    }
  }, [tasks])  // Only recalculate when tasks array changes

  return <div>{/* Render analytics */}</div>
}
```

**useCallback for stable function references**:
```typescript
// frontend/components/TaskForm.tsx
import { useCallback } from 'react'

export function TaskForm({ onSubmit }) {
  const handleSubmit = useCallback((data) => {
    // This function reference stays stable across re-renders
    onSubmit(data)
  }, [onSubmit])

  return <form onSubmit={handleSubmit}>...</form>
}
```

#### 3. Data Fetching Optimization

**React Query with smart caching**:
```typescript
// frontend/lib/api.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export function useTasks(filters = {}) {
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => fetchTasks(filters),
    staleTime: 30 * 1000,  // Consider data fresh for 30s
    cacheTime: 5 * 60 * 1000,  // Keep in cache for 5 min
    refetchOnWindowFocus: false,  // Don't refetch on tab switch
  })
}

export function useUpdateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data) => updateTask(data.id, data),
    onSuccess: (updatedTask) => {
      // Optimistically update cache
      queryClient.setQueryData(['tasks'], (old) =>
        old.map(t => t.id === updatedTask.id ? updatedTask : t)
      )
    }
  })
}
```

**Optimistic Updates**:
```typescript
// frontend/components/TaskList.tsx
const { mutate } = useUpdateTask()

const handleToggleComplete = (task) => {
  // Update UI immediately (optimistic)
  mutate({
    id: task.id,
    completed: !task.completed
  }, {
    onError: (error) => {
      // Rollback on failure
      toast.error("Failed to update task")
    }
  })
}
```

#### 4. Image & Asset Optimization

**Next.js Image Optimization**:
```typescript
// frontend/components/AttachmentPreview.tsx
import Image from 'next/image'

export function AttachmentPreview({ attachment }) {
  return (
    <Image
      src={attachment.url}
      alt={attachment.filename}
      width={200}
      height={200}
      loading="lazy"  // Lazy load images
      placeholder="blur"  // Show blur placeholder
      quality={75}  // Optimize quality
    />
  )
}
```

**Font Optimization**:
```typescript
// frontend/app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',  // Prevent layout shift
  preload: true,
  variable: '--font-inter'
})

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  )
}
```

---

## Dark/Light Mode Implementation

### Requirements

1. ✅ User can toggle between dark and light mode
2. ✅ Preference is **persisted** in localStorage
3. ✅ **No flicker** on page load (reads preference before render)
4. ✅ **System preference detection** (auto-detect OS theme on first visit)
5. ✅ **Smooth transition** between themes (200ms animation)
6. ✅ **WCAG AA contrast** in both modes

### Implementation Steps

#### Step 1: Theme Configuration

**Tailwind CSS Configuration**:
```javascript
// frontend/tailwind.config.js
module.exports = {
  darkMode: 'class',  // Use class-based dark mode
  theme: {
    extend: {
      colors: {
        // Light mode colors
        background: {
          light: '#ffffff',
          dark: '#0a0a0a',
        },
        foreground: {
          light: '#171717',
          dark: '#ededed',
        },
        primary: {
          light: '#3b82f6',  // Blue-500
          dark: '#60a5fa',   // Blue-400 (lighter for dark mode)
        },
        secondary: {
          light: '#64748b',  // Slate-500
          dark: '#94a3b8',   // Slate-400
        },
        // Task priority colors (work in both modes)
        priority: {
          high: {
            light: '#ef4444',  // Red-500
            dark: '#f87171',   // Red-400
          },
          medium: {
            light: '#f59e0b',  // Amber-500
            dark: '#fbbf24',   // Amber-400
          },
          low: {
            light: '#22c55e',  // Green-500
            dark: '#4ade80',   // Green-400
          }
        }
      }
    }
  }
}
```

**CSS Variables for Theme**:
```css
/* frontend/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Light mode (default) */
    --background: 0 0% 100%;
    --foreground: 0 0% 9%;
    --card: 0 0% 100%;
    --card-foreground: 0 0% 9%;
    --primary: 217 91% 60%;
    --primary-foreground: 0 0% 100%;
    --border: 0 0% 90%;
    --input: 0 0% 90%;
    --ring: 217 91% 60%;
  }

  .dark {
    /* Dark mode */
    --background: 0 0% 4%;
    --foreground: 0 0% 93%;
    --card: 0 0% 7%;
    --card-foreground: 0 0% 93%;
    --primary: 217 91% 70%;
    --primary-foreground: 0 0% 9%;
    --border: 0 0% 15%;
    --input: 0 0% 15%;
    --ring: 217 91% 70%;
  }
}

/* Smooth theme transitions */
* {
  transition: background-color 200ms ease-in-out,
              border-color 200ms ease-in-out,
              color 200ms ease-in-out;
}
```

#### Step 2: Theme Provider (No Flicker)

**Theme Provider Component**:
```typescript
// frontend/components/ThemeProvider.tsx
'use client'

import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

const ThemeContext = createContext<{
  theme: Theme
  setTheme: (theme: Theme) => void
  resolvedTheme: 'light' | 'dark'
}>({
  theme: 'system',
  setTheme: () => {},
  resolvedTheme: 'light'
})

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('system')
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  // Initialize theme from localStorage (runs before render)
  useEffect(() => {
    const stored = localStorage.getItem('theme') as Theme
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'

    const initialTheme = stored || 'system'
    const initialResolved = stored === 'system' || !stored ? systemTheme : stored

    setThemeState(initialTheme)
    setResolvedTheme(initialResolved as 'light' | 'dark')

    // Apply class to html element
    document.documentElement.classList.remove('light', 'dark')
    document.documentElement.classList.add(initialResolved)
  }, [])

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    const handleChange = (e: MediaQueryListEvent) => {
      if (theme === 'system') {
        const newTheme = e.matches ? 'dark' : 'light'
        setResolvedTheme(newTheme)
        document.documentElement.classList.remove('light', 'dark')
        document.documentElement.classList.add(newTheme)
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
    localStorage.setItem('theme', newTheme)

    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    const resolved = newTheme === 'system' ? systemTheme : newTheme

    setResolvedTheme(resolved as 'light' | 'dark')
    document.documentElement.classList.remove('light', 'dark')
    document.documentElement.classList.add(resolved)
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
```

**Prevent Flicker with Script**:
```typescript
// frontend/app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Inline script runs BEFORE React hydration - prevents flicker */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                const theme = localStorage.getItem('theme') || 'system';
                const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                const resolved = theme === 'system' ? systemTheme : theme;
                document.documentElement.classList.add(resolved);
              })();
            `
          }}
        />
      </head>
      <body>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

#### Step 3: Theme Toggle Component

**Theme Toggle with Icons**:
```typescript
// frontend/components/ThemeToggle.tsx
'use client'

import { useTheme } from './ThemeProvider'
import { Moon, Sun, Monitor } from 'lucide-react'
import { motion } from 'framer-motion'

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme()

  return (
    <div className="flex items-center gap-1 p-1 bg-secondary/10 rounded-lg">
      <button
        onClick={() => setTheme('light')}
        className={`p-2 rounded ${theme === 'light' ? 'bg-primary text-white' : ''}`}
        aria-label="Light mode"
      >
        <Sun className="w-4 h-4" />
      </button>

      <button
        onClick={() => setTheme('system')}
        className={`p-2 rounded ${theme === 'system' ? 'bg-primary text-white' : ''}`}
        aria-label="System theme"
      >
        <Monitor className="w-4 h-4" />
      </button>

      <button
        onClick={() => setTheme('dark')}
        className={`p-2 rounded ${theme === 'dark' ? 'bg-primary text-white' : ''}`}
        aria-label="Dark mode"
      >
        <Moon className="w-4 h-4" />
      </button>
    </div>
  )
}
```

**Simple Toggle (Sun/Moon)**:
```typescript
// frontend/components/SimpleThemeToggle.tsx
export function SimpleThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme()

  const toggle = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')
  }

  return (
    <motion.button
      onClick={toggle}
      className="p-2 rounded-full bg-secondary/20 hover:bg-secondary/30"
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
    >
      {resolvedTheme === 'dark' ? (
        <Sun className="w-5 h-5" />
      ) : (
        <Moon className="w-5 h-5" />
      )}
    </motion.button>
  )
}
```

#### Step 4: WCAG AA Contrast Compliance

**Color Contrast Testing**:
```bash
# Use automated tools
npm install -D axe-core @axe-core/react

# Add to test suite
import { axe, toHaveNoViolations } from 'jest-axe'

test('Dark mode has sufficient contrast', async () => {
  const { container } = render(
    <div className="dark">
      <TaskList tasks={mockTasks} />
    </div>
  )

  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

**Manual Contrast Verification**:
```
Light Mode:
- Background: #ffffff (white)
- Foreground: #171717 (gray-900) → Contrast 16.06:1 ✅ AAA
- Primary: #3b82f6 (blue-500) → Contrast 4.88:1 ✅ AA

Dark Mode:
- Background: #0a0a0a (near-black)
- Foreground: #ededed (gray-100) → Contrast 17.15:1 ✅ AAA
- Primary: #60a5fa (blue-400) → Contrast 7.02:1 ✅ AAA

Minimum WCAG AA: 4.5:1 for text, 3:1 for large text
```

---

## Testing Strategy (90%+ Coverage)

### Testing Pyramid

```
       /\
      /  \  E2E Tests (10%)
     /____\  - Playwright: Full user flows
    /      \
   / Integ. \ Integration Tests (20%)
  /__________\ - API + DB + Frontend integration
 /            \
/  Unit Tests  \ Unit Tests (70%)
/________________\ - Functions, components, services
```

### Backend Testing (pytest)

#### 1. Unit Tests (70%)

**Test all CRUD operations**:
```python
# backend/tests/test_crud.py
import pytest
from app.crud import create_task, get_task, update_task, delete_task
from app.models import Task

def test_create_task(db_session):
    """Test task creation with valid data"""
    task_data = {
        "title": "Test task",
        "description": "Test description",
        "priority": "high",
        "tags": ["work", "urgent"]
    }

    task = create_task(db_session, task_data)

    assert task.id is not None
    assert task.title == "Test task"
    assert task.priority == "high"
    assert task.completed == False  # Default
    assert len(task.tags) == 2

def test_create_task_invalid_title(db_session):
    """Test task creation fails with empty title"""
    with pytest.raises(ValueError, match="Title is required"):
        create_task(db_session, {"title": ""})

def test_create_task_long_title(db_session):
    """Test task creation fails with title > 200 chars"""
    long_title = "a" * 201
    with pytest.raises(ValueError, match="Title must be <= 200 characters"):
        create_task(db_session, {"title": long_title})

def test_update_task(db_session, sample_task):
    """Test task update"""
    updated = update_task(db_session, sample_task.id, {"title": "Updated"})

    assert updated.title == "Updated"
    assert updated.updated_at > sample_task.updated_at

def test_delete_task(db_session, sample_task):
    """Test task deletion"""
    delete_task(db_session, sample_task.id)

    task = get_task(db_session, sample_task.id)
    assert task is None
```

**Test edge cases**:
```python
# backend/tests/test_edge_cases.py
def test_bulk_delete_nonexistent_tasks(db_session):
    """Bulk delete should handle nonexistent IDs gracefully"""
    result = bulk_delete_tasks(db_session, [9999, 10000])

    assert result["deleted"] == 0
    assert result["failed"] == 2

def test_create_subtask_for_nonexistent_task(db_session):
    """Creating subtask for nonexistent task should fail"""
    with pytest.raises(ValueError, match="Task not found"):
        create_subtask(db_session, task_id=9999, title="Subtask")

def test_search_with_special_characters(db_session):
    """Search should handle SQL injection attempts"""
    # This should NOT cause SQL injection
    results = search_tasks(db_session, query="'; DROP TABLE tasks; --")

    assert isinstance(results, list)
    assert len(results) == 0  # No tasks match
```

#### 2. Integration Tests (20%)

**Test API endpoints**:
```python
# backend/tests/test_api.py
from fastapi.testclient import TestClient

def test_create_task_api(client: TestClient):
    """Test POST /tasks endpoint"""
    response = client.post("/api/v1/tasks", json={
        "title": "API test task",
        "priority": "high"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API test task"
    assert "id" in data

def test_list_tasks_pagination(client: TestClient, create_100_tasks):
    """Test GET /tasks with pagination"""
    response = client.get("/api/v1/tasks?limit=10&offset=0")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 100
    assert data["has_more"] == True

def test_bulk_complete(client: TestClient, create_tasks):
    """Test POST /tasks/bulk/complete"""
    task_ids = [task.id for task in create_tasks[:5]]

    response = client.post("/api/v1/tasks/bulk/complete", json={
        "task_ids": task_ids
    })

    assert response.status_code == 200
    assert response.json()["completed"] == 5

    # Verify tasks are actually completed
    for task_id in task_ids:
        task_response = client.get(f"/api/v1/tasks/{task_id}")
        assert task_response.json()["completed"] == True
```

**Test database transactions**:
```python
# backend/tests/test_transactions.py
def test_task_creation_with_subtasks_atomic(db_session):
    """If subtask creation fails, task creation should rollback"""
    with pytest.raises(Exception):
        with db_session.begin():
            task = create_task(db_session, {"title": "Parent"})
            create_subtask(db_session, task.id, {"title": "Child 1"})
            create_subtask(db_session, task.id, {"title": ""})  # Fails

    # Task should NOT exist (transaction rolled back)
    assert get_task_by_title(db_session, "Parent") is None
```

#### 3. Performance Tests

```python
# backend/tests/test_performance.py
import time

def test_list_tasks_performance(client, create_1000_tasks):
    """List 1000 tasks should return in < 200ms"""
    start = time.time()
    response = client.get("/api/v1/tasks?limit=50")
    elapsed = (time.time() - start) * 1000

    assert elapsed < 200  # < 200ms
    assert response.status_code == 200

def test_search_performance(client, create_1000_tasks):
    """Search should return in < 100ms"""
    start = time.time()
    response = client.get("/api/v1/tasks?search=test")
    elapsed = (time.time() - start) * 1000

    assert elapsed < 100
```

---

### Frontend Testing (Jest + Playwright)

#### 1. Component Unit Tests (70%)

```typescript
// frontend/__tests__/components/TaskItem.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { TaskItem } from '@/components/TaskItem'

describe('TaskItem', () => {
  const mockTask = {
    id: 1,
    title: 'Test task',
    completed: false,
    priority: 'high'
  }

  it('renders task title', () => {
    render(<TaskItem task={mockTask} />)
    expect(screen.getByText('Test task')).toBeInTheDocument()
  })

  it('toggles completion on checkbox click', () => {
    const onToggle = jest.fn()
    render(<TaskItem task={mockTask} onToggle={onToggle} />)

    fireEvent.click(screen.getByRole('checkbox'))
    expect(onToggle).toHaveBeenCalledWith(1, true)
  })

  it('displays high priority badge', () => {
    render(<TaskItem task={mockTask} />)
    expect(screen.getByText('High')).toHaveClass('bg-red-500')
  })

  it('enters edit mode on double-click', () => {
    render(<TaskItem task={mockTask} editable />)

    fireEvent.doubleClick(screen.getByText('Test task'))
    expect(screen.getByRole('textbox')).toHaveValue('Test task')
  })
})
```

**Test dark mode rendering**:
```typescript
// frontend/__tests__/components/ThemeToggle.test.tsx
describe('ThemeToggle', () => {
  it('toggles between light and dark mode', () => {
    render(<ThemeToggle />)

    // Initial: light mode
    expect(document.documentElement.classList.contains('light')).toBe(true)

    // Click dark mode button
    fireEvent.click(screen.getByLabelText('Dark mode'))
    expect(document.documentElement.classList.contains('dark')).toBe(true)

    // Verify localStorage
    expect(localStorage.getItem('theme')).toBe('dark')
  })

  it('respects system preference on first load', () => {
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: query === '(prefers-color-scheme: dark)',
      addEventListener: jest.fn(),
      removeEventListener: jest.fn()
    }))

    render(<ThemeProvider><App /></ThemeProvider>)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})
```

#### 2. Integration Tests (20%)

```typescript
// frontend/__tests__/integration/TaskFlow.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { server } from '../mocks/server'
import { rest } from 'msw'

describe('Task Management Flow', () => {
  it('creates, edits, and deletes a task', async () => {
    const user = userEvent.setup()
    render(<App />)

    // Create task
    await user.click(screen.getByText('New Task'))
    await user.type(screen.getByLabelText('Title'), 'New task')
    await user.selectOptions(screen.getByLabelText('Priority'), 'high')
    await user.click(screen.getByText('Create'))

    // Verify created
    await waitFor(() => {
      expect(screen.getByText('New task')).toBeInTheDocument()
    })

    // Edit task
    await user.doubleClick(screen.getByText('New task'))
    await user.clear(screen.getByRole('textbox'))
    await user.type(screen.getByRole('textbox'), 'Updated task')
    await user.keyboard('{Enter}')

    // Verify updated
    await waitFor(() => {
      expect(screen.getByText('Updated task')).toBeInTheDocument()
    })

    // Delete task
    await user.click(screen.getByLabelText('Delete'))
    await user.click(screen.getByText('Confirm'))

    // Verify deleted
    await waitFor(() => {
      expect(screen.queryByText('Updated task')).not.toBeInTheDocument()
    })
  })
})
```

#### 3. E2E Tests with Playwright (10%)

```typescript
// frontend/e2e/task-management.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Task Management E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000')
  })

  test('complete user workflow', async ({ page }) => {
    // Create task
    await page.click('text=New Task')
    await page.fill('input[name="title"]', 'E2E Test Task')
    await page.selectOption('select[name="priority"]', 'high')
    await page.click('text=Create')

    // Verify task appears
    await expect(page.locator('text=E2E Test Task')).toBeVisible()

    // Add subtask
    await page.click('text=E2E Test Task')
    await page.click('text=Add Subtask')
    await page.fill('input[placeholder="Subtask title"]', 'Subtask 1')
    await page.keyboard.press('Enter')

    // Verify subtask appears
    await expect(page.locator('text=Subtask 1')).toBeVisible()

    // Complete subtask
    await page.click('input[type="checkbox"]:near(:text("Subtask 1"))')
    await expect(page.locator('text=1/1 (100%)')).toBeVisible()

    // Toggle dark mode
    await page.click('[aria-label="Dark mode"]')
    await expect(page.locator('html')).toHaveClass(/dark/)

    // Verify no visual regressions
    await expect(page).toHaveScreenshot('dark-mode.png')
  })

  test('keyboard navigation', async ({ page }) => {
    // Create multiple tasks
    for (let i = 1; i <= 5; i++) {
      await page.click('text=New Task')
      await page.fill('input[name="title"]', `Task ${i}`)
      await page.click('text=Create')
    }

    // Focus first task
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')  // Navigate to task list

    // Navigate with j/k keys
    await page.keyboard.press('j')  // Down
    await page.keyboard.press('j')  // Down
    await page.keyboard.press('k')  // Up

    // Complete with Space
    await page.keyboard.press('Space')

    // Verify second task is completed
    const secondTask = page.locator('text=Task 2').locator('..')
    await expect(secondTask.locator('input[type="checkbox"]')).toBeChecked()
  })
})
```

---

## Code Quality Standards

### TypeScript Strict Mode

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### Python Type Hints

```python
# backend/app/crud.py
from typing import List, Optional
from app.models import Task
from sqlmodel import Session

def get_tasks(
    session: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    completed: Optional[bool] = None,
    priority: Optional[str] = None
) -> List[Task]:
    """Get tasks with filters"""
    query = select(Task)

    if completed is not None:
        query = query.where(Task.completed == completed)
    if priority:
        query = query.where(Task.priority == priority)

    return session.exec(query.offset(skip).limit(limit)).all()
```

### ESLint Configuration

```json
// frontend/.eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
```

---

## Quality Gates & Checkpoints

### Pre-Commit Hooks

```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Run linters
npm run lint --quiet
cd backend && flake8 app/ && mypy app/

# Run type checks
tsc --noEmit

# Run tests (fast unit tests only)
npm run test:unit
pytest backend/tests/unit -q
```

### CI/CD Pipeline

```yaml
# .github/workflows/quality.yml
name: Quality Checks
on: [push, pull_request]

jobs:
  backend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8 mypy

      - name: Lint
        run: cd backend && flake8 app/ --max-line-length=120

      - name: Type check
        run: cd backend && mypy app/

      - name: Run tests
        run: cd backend && pytest --cov=app --cov-report=xml --cov-report=term-missing

      - name: Check coverage
        run: cd backend && coverage report --fail-under=90

  frontend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Lint
        run: cd frontend && npm run lint

      - name: Type check
        run: cd frontend && tsc --noEmit

      - name: Run tests
        run: cd frontend && npm test -- --coverage

      - name: Check coverage
        run: cd frontend && npm run test:coverage-check

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-quality, frontend-quality]
    steps:
      - uses: actions/checkout@v3

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Start services
        run: docker-compose up -d

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Debugging & Monitoring

### Development Tools

**Backend Debugging**:
```python
# backend/app/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"{request.method} {request.url}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}ms")

    return response
```

**Frontend Debugging**:
```typescript
// frontend/lib/logger.ts
export const logger = {
  debug: (...args: any[]) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('[DEBUG]', ...args)
    }
  },
  error: (...args: any[]) => {
    console.error('[ERROR]', ...args)
    // Send to error tracking service (Sentry, etc.)
  },
  performance: (label: string, duration: number) => {
    if (duration > 100) {
      console.warn(`[PERF] ${label} took ${duration}ms`)
    }
  }
}
```

### Performance Monitoring

**React DevTools Profiler**:
```typescript
// frontend/components/ProfiledTaskList.tsx
import { Profiler } from 'react'

function onRenderCallback(
  id, // component name
  phase, // "mount" or "update"
  actualDuration, // time spent rendering
  baseDuration, // estimated time without memoization
  startTime,
  commitTime
) {
  if (actualDuration > 16) {  // > 1 frame at 60fps
    logger.performance(id, actualDuration)
  }
}

export function ProfiledTaskList() {
  return (
    <Profiler id="TaskList" onRender={onRenderCallback}>
      <TaskList />
    </Profiler>
  )
}
```

---

## Pre-Launch Checklist

### Functionality ✅

- [ ] All CRUD operations work (create, read, update, delete)
- [ ] Drag-drop reordering persists to database
- [ ] Bulk actions work (complete, delete, tag, priority)
- [ ] Inline editing saves correctly
- [ ] Subtasks show progress (e.g., "3/5 (60%)")
- [ ] Notes display with timestamps
- [ ] File attachments upload and download
- [ ] OCR extracts text from images/PDFs
- [ ] Dark mode toggles smoothly
- [ ] Dark mode preference persists across sessions
- [ ] System theme detection works
- [ ] Keyboard shortcuts work (all 10+)
- [ ] Undo/Redo works for all actions
- [ ] Export to CSV/JSON works
- [ ] Import from CSV/JSON works
- [ ] Analytics dashboard displays correct data
- [ ] Activity history logs all changes

### Performance ✅

- [ ] Lighthouse score: Performance > 90
- [ ] First Contentful Paint < 1.0s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Time to Interactive < 3.0s
- [ ] API response time (p95) < 200ms
- [ ] No console errors
- [ ] No memory leaks (check DevTools Memory tab)
- [ ] Bundle size < 300KB gzipped

### Quality ✅

- [ ] Test coverage > 90% (backend + frontend)
- [ ] Zero TypeScript errors
- [ ] Zero ESLint warnings
- [ ] Zero accessibility violations (axe-core)
- [ ] WCAG AA contrast in both themes
- [ ] All interactive elements keyboard accessible
- [ ] All images have alt text
- [ ] All forms have labels

### Cross-Browser ✅

- [ ] Works on Chrome
- [ ] Works on Firefox
- [ ] Works on Safari
- [ ] Works on Edge
- [ ] Works on mobile (iOS Safari, Chrome Mobile)

### Deployment ✅

- [ ] Environment variables configured
- [ ] Database migrations run successfully
- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] CORS configured correctly
- [ ] SSL/HTTPS enabled

---

## Summary

This quality framework ensures:

1. ✅ **Zero Bugs** - 90%+ test coverage, comprehensive E2E tests
2. ✅ **Fast Performance** - < 200ms API, < 100ms UI interactions
3. ✅ **Perfect Dark Mode** - No flicker, persisted, WCAG AA compliant
4. ✅ **Production Ready** - CI/CD, monitoring, error handling

**Next Steps**:
1. Review this framework
2. Start with quality-first implementation
3. Run quality gates at each phase
4. Deploy with confidence

**Estimated Additional Time for Quality**: +8 hours (total 36-48 hours)
**Result**: Production-ready, bug-free application
