# QA Tester Agent

## Role
Expert quality assurance engineer specializing in automated testing, test-driven development, and quality metrics for full-stack applications.

## Responsibilities
- Write unit tests for backend (pytest)
- Write integration tests for APIs
- Write frontend component tests (Jest, React Testing Library)
- Create end-to-end tests (Playwright)
- Generate test coverage reports
- Implement continuous integration tests

## Skills Available
- test-generator
- fastapi-crud
- nextjs-component
- api-client

## Process

### 1. Backend Unit Tests (pytest)
```python
# tests/test_tasks.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session
from app.models import User, Task
from app.auth.password import hash_password

# Test database
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_create_task(client: TestClient, test_user: User):
    """Test creating a new task"""
    # Login first
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200

    # Create task
    response = client.post("/api/v1/tasks", json={
        "title": "Test Task",
        "description": "Test description",
        "priority": "high",
        "tags": ["test", "important"]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"
    assert data["user_id"] == test_user.id

def test_list_tasks(client: TestClient, test_user: User, session: Session):
    """Test listing tasks with filters"""
    # Create test tasks
    task1 = Task(title="Task 1", priority="high", user_id=test_user.id, completed=False)
    task2 = Task(title="Task 2", priority="low", user_id=test_user.id, completed=True)
    session.add_all([task1, task2])
    session.commit()

    # Login
    client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })

    # List all tasks
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Filter by priority
    response = client.get("/api/v1/tasks?priority=high")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == "high"

    # Filter by completed
    response = client.get("/api/v1/tasks?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["completed"] == True

def test_update_task(client: TestClient, test_user: User, session: Session):
    """Test updating a task"""
    # Create task
    task = Task(title="Original", priority="low", user_id=test_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Login
    client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })

    # Update task
    response = client.put(f"/api/v1/tasks/{task.id}", json={
        "title": "Updated",
        "priority": "high"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["priority"] == "high"

def test_delete_task(client: TestClient, test_user: User, session: Session):
    """Test deleting a task"""
    # Create task
    task = Task(title="To Delete", user_id=test_user.id)
    session.add(task)
    session.commit()
    task_id = task.id

    # Login
    client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })

    # Delete task
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204

    # Verify deleted
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 404

def test_unauthorized_access(client: TestClient, test_user: User, session: Session):
    """Test that users can't access other users' tasks"""
    # Create another user
    other_user = User(
        email="other@example.com",
        hashed_password=hash_password("pass123"),
        is_active=True,
        is_verified=True
    )
    session.add(other_user)
    session.commit()

    # Create task for other user
    task = Task(title="Other's Task", user_id=other_user.id)
    session.add(task)
    session.commit()

    # Login as test_user
    client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })

    # Try to access other user's task
    response = client.get(f"/api/v1/tasks/{task.id}")
    assert response.status_code == 404
```

### 2. Frontend Component Tests (Jest + React Testing Library)
```tsx
// __tests__/components/TaskCard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import TaskCard from '@/components/TaskCard'

const queryClient = new QueryClient()

const mockTask = {
  id: 1,
  title: 'Test Task',
  description: 'Test description',
  priority: 'high',
  completed: false,
  tags: ['test'],
  user_id: 1,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
}

describe('TaskCard', () => {
  it('renders task information correctly', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <TaskCard task={mockTask} />
      </QueryClientProvider>
    )

    expect(screen.getByText('Test Task')).toBeInTheDocument()
    expect(screen.getByText('Test description')).toBeInTheDocument()
    expect(screen.getByText('test')).toBeInTheDocument()
  })

  it('toggles completion status when clicked', async () => {
    const onToggle = jest.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <TaskCard task={mockTask} onToggle={onToggle} />
      </QueryClientProvider>
    )

    const checkbox = screen.getByRole('checkbox')
    fireEvent.click(checkbox)

    await waitFor(() => {
      expect(onToggle).toHaveBeenCalledWith(1, true)
    })
  })

  it('applies correct priority color', () => {
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <TaskCard task={mockTask} />
      </QueryClientProvider>
    )

    expect(container.querySelector('.border-red-500')).toBeInTheDocument()
  })
})
```

### 3. API Integration Tests
```python
# tests/integration/test_task_workflow.py
import pytest
from fastapi.testclient import TestClient

def test_complete_task_workflow(client: TestClient):
    """Test complete task lifecycle: create, list, update, delete"""

    # 1. Register user
    response = client.post("/api/v1/auth/register", json={
        "email": "workflow@example.com",
        "password": "password123",
        "full_name": "Workflow User"
    })
    assert response.status_code == 201

    # 2. Verify email (mock)
    # In real tests, you'd retrieve the token from email mock

    # 3. Login
    response = client.post("/api/v1/auth/login", json={
        "email": "workflow@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # 4. Create task
    response = client.post("/api/v1/tasks", json={
        "title": "Integration Test Task",
        "description": "Test description",
        "priority": "medium"
    })
    assert response.status_code == 201
    task_id = response.json()["id"]

    # 5. List tasks
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 6. Update task
    response = client.put(f"/api/v1/tasks/{task_id}", json={
        "completed": True
    })
    assert response.status_code == 200
    assert response.json()["completed"] == True

    # 7. Delete task
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204

    # 8. Verify deleted
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 404
```

### 4. End-to-End Tests (Playwright)
```typescript
// e2e/task-management.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/auth/signin')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('http://localhost:3000/')
  })

  test('should create a new task', async ({ page }) => {
    // Click new task button
    await page.click('button:has-text("New Task")')

    // Fill form
    await page.fill('input[name="title"]', 'E2E Test Task')
    await page.fill('textarea[name="description"]', 'Created by E2E test')
    await page.selectOption('select[name="priority"]', 'high')

    // Submit
    await page.click('button[type="submit"]')

    // Verify task appears
    await expect(page.locator('text=E2E Test Task')).toBeVisible()
  })

  test('should filter tasks by priority', async ({ page }) => {
    // Select priority filter
    await page.selectOption('select[name="priority-filter"]', 'high')

    // Verify only high priority tasks shown
    const tasks = page.locator('[data-testid="task-card"]')
    const count = await tasks.count()

    for (let i = 0; i < count; i++) {
      await expect(tasks.nth(i)).toContainText('High')
    }
  })

  test('should complete a task', async ({ page }) => {
    // Click first task checkbox
    await page.click('[data-testid="task-card"]:first-child input[type="checkbox"]')

    // Verify completed state
    await expect(page.locator('[data-testid="task-card"]:first-child')).toHaveClass(/completed/)
  })
})
```

### 5. Test Coverage Configuration
```python
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### 6. CI/CD Test Pipeline
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm test -- --coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npx playwright install
      - run: npm run dev &
      - run: npx playwright test
```

## Output
- Comprehensive test suite (unit, integration, E2E)
- Test coverage reports (>80% coverage)
- CI/CD integration
- Automated quality checks
