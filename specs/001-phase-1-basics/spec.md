# Feature: Phase I Basic CRUD Operations

**Feature Branch**: `001-phase-1-basics`
**Created**: 2025-12-04
**Status**: Draft
**Phase**: I - In-Memory Python Console App

## Purpose
Implement the 5 basic task management operations in a Python console application with in-memory storage. This establishes the foundation for evolution to web app (Phase II) and AI chatbot (Phase III).

## User Stories

- As a user, I can create a new task with title and optional description
- As a user, I can view all my tasks in the console
- As a user, I can update a task's title or description
- As a user, I can delete a task
- As a user, I can mark a task as complete or incomplete

## Acceptance Criteria

### Create Task
- Title is required (1-200 characters)
- Description is optional (max 2000 characters)
- System auto-assigns unique sequential ID starting from 1
- System auto-records creation timestamp (ISO 8601 format)
- Task defaults to incomplete status (completed = false)
- Empty or whitespace-only titles are rejected with error message
- Command: `python -m todo.app add "title" --description "desc"`

### View Tasks
- Display all tasks in readable console format
- Show: ID, title, description, completion status, created timestamp
- Completed tasks visually distinguished from incomplete (e.g., [✓] vs [ ])
- Empty list shows helpful message: "No tasks yet. Use 'add' to create one."
- Command: `python -m todo.app list`

### Update Task
- Can update title, description, or both
- Requires valid task ID
- Cannot set title to empty string
- Non-existent task ID returns error message
- Updated fields are changed; other fields remain unchanged
- Command: `python -m todo.app update <id> --title "new" --description "new"`

### Delete Task
- Permanently removes task from storage
- Requires valid task ID
- Non-existent task ID returns error message
- Deleted task IDs are not reused (gaps remain in sequence)
- Command: `python -m todo.app delete <id>`

### Mark Complete
- Toggles task completion status (true/false)
- Requires valid task ID
- Non-existent task ID returns error message
- Can mark complete or incomplete multiple times
- Command: `python -m todo.app complete <id> [--incomplete]`

## Technical Constraints

### Data Model
```python
{
    "id": int,            # Auto-generated, sequential (1, 2, 3, ...)
    "title": str,         # Required, max 200 chars
    "description": str,   # Optional, max 2000 chars
    "completed": bool,    # Default False
    "created_at": str     # ISO 8601 timestamp (datetime.now().isoformat())
}
```

### Technology Stack
- **Language**: Python 3.13+
- **CLI Framework**: `argparse` (standard library)
- **Storage**: In-memory (Python `list` of `dict`)
- **Testing**: `unittest` (standard library)
- **Dependencies**: ZERO external packages for core logic

### Architecture
```
src/
├── todo/
│   ├── __init__.py
│   ├── app.py          # CLI entry point (argparse)
│   ├── storage.py      # In-memory CRUD operations
│   └── models.py       # Task validation and business logic
└── tests/
    ├── test_storage.py # Unit tests for storage
    └── test_cli.py     # Integration tests for CLI
```

## Out of Scope (Phase I)

Phase I explicitly excludes:
- ❌ Priorities & Tags (Phase II)
- ❌ Search & Filter (Phase II)
- ❌ Sort Tasks (Phase II)
- ❌ Due Dates & Reminders (Phase III)
- ❌ Recurring Tasks (Phase III)
- ❌ Web interface (Phase II)
- ❌ Database persistence (Phase II)
- ❌ User authentication (Phase II)
- ❌ AI chatbot (Phase III)
- ❌ Multi-user support (Phase II+)

## Success Criteria

- ✅ All 5 basic features working in console
- ✅ Command execution response time < 1 second
- ✅ All operations provide clear success/error feedback
- ✅ Handles at least 100 tasks without errors
- ✅ 80%+ test coverage (unittest)
- ✅ Zero external dependencies for core logic
- ✅ All inputs validated with clear error messages
- ✅ Task data preserved accurately throughout session
- ✅ README.md with installation and usage instructions

## Edge Cases

- Task title exceeding 200 characters → Reject with error
- Description exceeding 2000 characters → Reject with error
- Empty or whitespace-only title → Reject with error
- Invalid task ID (non-existent, non-integer) → Reject with error
- Special characters and Unicode in title/description → Handle gracefully
- System restart → Data loss expected (in-memory only, warn user)
- Large task lists (1000+ tasks) → Display remains functional
- Newlines in descriptions → Preserve formatting where possible

## Assumptions

- Single-user, single-session usage (no concurrent access)
- Users have Python 3.13+ installed
- Users are familiar with command-line interfaces
- Data loss on restart is acceptable for Phase I
- Terminal/console supports standard input/output
- No data persistence required (in-memory only)

## Evolution Path to Phase II

This Phase I implementation is designed to evolve smoothly:
- Data model matches Phase II base structure (id, title, description, completed, created_at)
- Phase II will add: priority, tags, updated_at fields
- Task IDs persist (not reused) to support database migration
- Architecture separates concerns (app, storage, models) for easy refactoring
- In-memory storage will be replaced with SQLModel + Postgres
- CLI will be supplemented with FastAPI REST API + Next.js frontend
