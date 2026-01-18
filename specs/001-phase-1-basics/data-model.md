# Data Model: Phase I Basic CRUD Operations

**Feature**: 001-phase-1-basics
**Date**: 2025-12-04
**Storage**: In-Memory (Python list of dict)

## Overview

Phase I uses a simple in-memory data model with a single entity (Task) stored as Python dictionaries in a list. This model is designed for forward compatibility with Phase II's database schema.

## Entities

### Task

**Description**: Represents a single todo item with title, description, completion status, and metadata.

**Storage Format**: Python dictionary in a list

**Schema**:
```python
Task = {
    "id": int,            # Unique identifier
    "title": str,         # Task title
    "description": str,   # Optional details
    "completed": bool,    # Completion status
    "created_at": str     # ISO 8601 timestamp
}
```

**Field Specifications**:

| Field | Type | Required | Constraints | Default | Notes |
|-------|------|----------|-------------|---------|-------|
| `id` | `int` | Yes | Unique, sequential, starts at 1 | Auto-generated | Never reused after deletion |
| `title` | `str` | Yes | 1-200 characters, non-empty after strip | N/A | Primary display text |
| `description` | `str` | No | Max 2000 characters | `""` (empty string) | Detailed information |
| `completed` | `bool` | Yes | Boolean | `False` | Task status |
| `created_at` | `str` | Yes | ISO 8601 format | `datetime.now().isoformat()` | Creation timestamp |

**Example Instance**:
```python
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, and coffee",
    "completed": False,
    "created_at": "2025-12-04T19:30:15.123456"
}
```

## Validation Rules

### Title Validation

**Rules**:
1. Required (cannot be `None` or empty string)
2. After `strip()`, must have at least 1 character
3. Maximum 200 characters
4. No additional sanitization (Python 3 handles Unicode)

**Error Messages**:
- Empty/None: `"Error: Title is required"`
- Too long: `"Error: Title must be 200 characters or less (current: {len} characters)"`
- Whitespace only: `"Error: Title cannot be only whitespace"`

**Implementation**:
```python
def validate_title(title: str) -> Optional[str]:
    """Validate task title. Returns error message or None."""
    if not title:
        return "Title is required"
    if not title.strip():
        return "Title cannot be only whitespace"
    if len(title) > 200:
        return f"Title must be 200 characters or less (current: {len(title)} characters)"
    return None
```

### Description Validation

**Rules**:
1. Optional (can be empty string or None)
2. Maximum 2000 characters
3. Empty string stored as `""`, not `None`

**Error Messages**:
- Too long: `"Error: Description must be 2000 characters or less (current: {len} characters)"`

**Implementation**:
```python
def validate_description(description: str) -> Optional[str]:
    """Validate task description. Returns error message or None."""
    if description and len(description) > 2000:
        return f"Description must be 2000 characters or less (current: {len(description)} characters)"
    return None
```

### ID Validation

**Rules**:
1. Must be an integer
2. Must exist in the task list
3. Must be positive (> 0)

**Error Messages**:
- Not an integer: `"Error: Task ID must be an integer"`
- Not found: `"Error: Task with ID {id} not found"`
- Invalid (≤ 0): `"Error: Task ID must be greater than 0"`

**Implementation**:
```python
def validate_task_id(task_id: Any, tasks: List[Dict]) -> Optional[str]:
    """Validate task ID exists. Returns error message or None."""
    try:
        task_id = int(task_id)
    except (ValueError, TypeError):
        return "Task ID must be an integer"

    if task_id <= 0:
        return "Task ID must be greater than 0"

    if not any(task["id"] == task_id for task in tasks):
        return f"Task with ID {task_id} not found"

    return None
```

## Storage Implementation

### Global Storage

**Structure**:
```python
# Module-level storage (src/todo/storage.py)
_tasks: List[Dict[str, Any]] = []
_next_id: int = 1
```

**Rationale**:
- Simple, sufficient for Phase I single-user scenario
- No concurrency concerns (single-threaded CLI)
- Easy to test (can reset between tests)
- Will be replaced with database in Phase II

### ID Generation Strategy

**Algorithm**: Sequential counter with gap preservation

**Implementation**:
```python
def generate_id() -> int:
    """Generate next available task ID."""
    global _next_id
    current_id = _next_id
    _next_id += 1
    return current_id
```

**Characteristics**:
- Always increments (never reuses deleted IDs)
- Predictable, user-friendly for CLI
- Compatible with database auto-increment in Phase II
- Gaps in sequence after deletions (expected behavior)

**Example Sequence**:
```
Add task 1 → ID: 1
Add task 2 → ID: 2
Add task 3 → ID: 3
Delete task 2
Add task 4 → ID: 4  (not 2!)
```

## State Transitions

### Task Lifecycle

```
         create
┌─────────────────────────┐
│                         │
│       Created           │
│    (completed=False)    │
│                         │
└────────┬────────────────┘
         │
         │ mark_complete
         ▼
┌─────────────────────────┐
│                         │
│       Completed         │
│    (completed=True)     │
│                         │
└────────┬────────────────┘
         │
         │ mark_incomplete
         ▼
┌─────────────────────────┐
│                         │
│       Created           │
│    (completed=False)    │
│                         │
└─────────────────────────┘

      Any state
         │
         │ delete
         ▼
     [Removed]
```

**Valid Transitions**:
1. **Create** → `completed=False` (default state)
2. **Mark Complete** → `completed=True`
3. **Mark Incomplete** → `completed=False`
4. **Update** → Same state, fields changed
5. **Delete** → Removed from list

**Notes**:
- Completion status can toggle unlimited times
- Update operation preserves completion status
- Deletion is permanent (no undo in Phase I)

## Indexes and Performance

### Phase I: No Indexing

**Rationale**:
- Linear search sufficient for < 100 tasks (specification target)
- Python list operations are O(n), acceptable for small n
- No external dependencies allowed (no specialized data structures)

**Operations Complexity**:
- `add_task()`: O(1) - append to list
- `list_tasks()`: O(n) - iterate all tasks
- `find_by_id()`: O(n) - linear search
- `update_task()`: O(n) - find then update
- `delete_task()`: O(n) - find then remove

### Phase II: Database Indexes

**Future Optimization** (Phase II migration):
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

## Evolution to Phase II

### Schema Migration Plan

**Phase II Additions**:
```python
Task = {
    # Phase I fields (unchanged)
    "id": int,
    "title": str,
    "description": str,
    "completed": bool,
    "created_at": str,

    # Phase II additions
    "priority": str,        # "high", "medium", "low"
    "tags": str,            # JSON array as string: '["work","urgent"]'
    "updated_at": str,      # ISO 8601 timestamp
    "user_id": str          # Foreign key to users table
}
```

**Migration Strategy**:
1. Phase I → Phase II: Add new fields with defaults
   - `priority`: Default `"medium"`
   - `tags`: Default `"[]"`
   - `updated_at`: Default to `created_at`
   - `user_id`: Assign to single migration user
2. Existing Phase I data structure remains valid
3. All Phase I operations continue working unchanged

**Backward Compatibility**:
- ✅ Phase I `Task` is a subset of Phase II `Task`
- ✅ No breaking changes to existing fields
- ✅ CLI commands remain functional (ignore new fields)

## Data Integrity Rules

### Invariants

**Must Always Be True**:
1. All task IDs are unique and positive integers
2. All tasks have non-empty titles after strip
3. All tasks have a creation timestamp
4. Completed field is always boolean (never None)
5. Description is always a string (empty string, never None)
6. ID sequence only increases (no reuse)

**Enforcement**:
- Validation functions enforce rules before mutations
- Storage layer guarantees ID uniqueness
- Default values ensure required fields are never missing

### Error Recovery

**Scenarios**:
1. **Invalid input**: Reject with error message, storage unchanged
2. **Missing task ID**: Return error, no side effects
3. **Validation failure**: Storage operation aborted, clear error message
4. **Exception during operation**: Storage remains consistent (Python exceptions don't corrupt in-memory data)

## Testing Considerations

### Test Data Fixtures

**Standard Fixture** (for test suites):
```python
FIXTURE_TASKS = [
    {
        "id": 1,
        "title": "Task 1",
        "description": "Description 1",
        "completed": False,
        "created_at": "2025-12-04T10:00:00"
    },
    {
        "id": 2,
        "title": "Task 2",
        "description": "",
        "completed": True,
        "created_at": "2025-12-04T11:00:00"
    },
    {
        "id": 3,
        "title": "Task 3 with a much longer title to test display",
        "description": "Very long description " * 50,  # Test length limits
        "completed": False,
        "created_at": "2025-12-04T12:00:00"
    }
]
```

### Edge Cases to Test

1. **Boundary Values**:
   - Title exactly 200 characters
   - Title 201 characters (should fail)
   - Description exactly 2000 characters
   - Description 2001 characters (should fail)

2. **Special Characters**:
   - Unicode/emoji in titles: "🎯 Buy groceries"
   - Newlines in descriptions: "Line 1\nLine 2"
   - Special chars: `!@#$%^&*()`

3. **Empty States**:
   - Empty task list (list_tasks)
   - Empty description (should default to "")
   - Whitespace-only title (should fail validation)

4. **ID Edge Cases**:
   - Non-existent ID
   - Negative ID
   - String ID ("abc")
   - Float ID (1.5)
   - Very large ID (999999)

## Summary

**Data Model Characteristics**:
- ✅ Single entity (Task)
- ✅ In-memory storage (list of dicts)
- ✅ Simple validation rules
- ✅ Sequential ID generation
- ✅ Phase II compatible
- ✅ No external dependencies

**Ready for**: Contract definition and quickstart guide (Phase 1 continuation)
