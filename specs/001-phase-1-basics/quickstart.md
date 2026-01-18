# Quickstart Implementation Guide: Phase I

**Feature**: 001-phase-1-basics
**Date**: 2025-12-04
**Target**: Developers implementing the Phase I console app

## Overview

This guide provides step-by-step instructions for implementing the 5 basic CRUD operations for the Phase I console todo application. Follow this guide to ensure consistent implementation aligned with the specification and architecture.

## Prerequisites

- Python 3.13+ installed
- Git repository cloned
- Familiarity with Python standard library (argparse, unittest, datetime)

## Project Structure

```
physical-ai-todo/
├── src/
│   └── todo/
│       ├── __init__.py      # Package initialization
│       ├── app.py           # CLI entry point (argparse)
│       ├── storage.py       # CRUD operations
│       └── models.py        # Validation logic
├── tests/
│   ├── __init__.py
│   ├── test_storage.py      # Unit tests for storage layer
│   └── test_cli.py          # Integration tests for CLI
├── specs/
│   └── 001-phase-1-basics/  # This feature's documentation
├── requirements.txt         # Empty (no external dependencies)
└── README.md                # User documentation
```

## Implementation Order

Implement in this sequence to minimize integration issues:

1. **models.py** - Validation functions (no dependencies)
2. **storage.py** - CRUD operations (depends on models)
3. **app.py** - CLI interface (depends on storage)
4. **test_storage.py** - Unit tests
5. **test_cli.py** - Integration tests

---

## Step 1: Implement models.py

**Purpose**: Validation logic and data type definitions

**File**: `src/todo/models.py`

**Functions to Implement**:

### 1.1 validate_title()

```python
from typing import Optional

def validate_title(title: str) -> Optional[str]:
    """
    Validate task title.

    Args:
        title: The title string to validate

    Returns:
        None if valid, error message string if invalid

    Rules:
        - Required (not None or empty)
        - After strip(), must have at least 1 character
        - Maximum 200 characters
    """
    if not title:
        return "Title is required"

    if not title.strip():
        return "Title cannot be only whitespace"

    if len(title) > 200:
        return f"Title must be 200 characters or less (current: {len(title)} characters)"

    return None
```

### 1.2 validate_description()

```python
def validate_description(description: str) -> Optional[str]:
    """
    Validate task description.

    Args:
        description: The description string to validate

    Returns:
        None if valid, error message string if invalid

    Rules:
        - Optional (can be empty)
        - Maximum 2000 characters
    """
    if description and len(description) > 2000:
        return f"Description must be 2000 characters or less (current: {len(description)} characters)"

    return None
```

### 1.3 validate_task_data()

```python
from typing import Dict, List

def validate_task_data(title: str, description: str = "") -> List[str]:
    """
    Validate complete task data.

    Args:
        title: Task title
        description: Task description (optional)

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    title_error = validate_title(title)
    if title_error:
        errors.append(title_error)

    desc_error = validate_description(description)
    if desc_error:
        errors.append(desc_error)

    return errors
```

---

## Step 2: Implement storage.py

**Purpose**: CRUD operations and in-memory storage

**File**: `src/todo/storage.py`

**Module-Level Storage**:

```python
from datetime import datetime
from typing import Dict, List, Any, Optional
from . import models

# In-memory storage
_tasks: List[Dict[str, Any]] = []
_next_id: int = 1
```

**Functions to Implement**:

### 2.1 add_task()

```python
def add_task(title: str, description: str = "") -> Dict[str, Any]:
    """
    Create a new task.

    Args:
        title: Task title (required, 1-200 chars)
        description: Task description (optional, max 2000 chars)

    Returns:
        Created task dictionary

    Raises:
        ValueError: If validation fails
    """
    global _next_id

    # Validate input
    errors = models.validate_task_data(title, description)
    if errors:
        raise ValueError("; ".join(errors))

    # Create task
    task = {
        "id": _next_id,
        "title": title.strip(),
        "description": description.strip() if description else "",
        "completed": False,
        "created_at": datetime.now().isoformat()
    }

    # Store task
    _tasks.append(task)
    _next_id += 1

    return task
```

### 2.2 list_tasks()

```python
def list_tasks() -> List[Dict[str, Any]]:
    """
    Get all tasks.

    Returns:
        List of task dictionaries (may be empty)
    """
    return _tasks.copy()  # Return copy to prevent external modification
```

### 2.3 get_task()

```python
def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Find task by ID.

    Args:
        task_id: Task ID to find

    Returns:
        Task dictionary if found, None otherwise
    """
    for task in _tasks:
        if task["id"] == task_id:
            return task.copy()  # Return copy
    return None
```

### 2.4 update_task()

```python
def update_task(task_id: int, title: Optional[str] = None,
                description: Optional[str] = None) -> Dict[str, Any]:
    """
    Update task fields.

    Args:
        task_id: Task ID to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Updated task dictionary

    Raises:
        ValueError: If task not found or validation fails
    """
    # Find task
    task = None
    for t in _tasks:
        if t["id"] == task_id:
            task = t
            break

    if task is None:
        raise ValueError(f"Task with ID {task_id} not found")

    # Validate new values
    if title is not None:
        error = models.validate_title(title)
        if error:
            raise ValueError(error)
        task["title"] = title.strip()

    if description is not None:
        error = models.validate_description(description)
        if error:
            raise ValueError(error)
        task["description"] = description.strip() if description else ""

    return task.copy()
```

### 2.5 delete_task()

```python
def delete_task(task_id: int) -> Dict[str, Any]:
    """
    Delete task by ID.

    Args:
        task_id: Task ID to delete

    Returns:
        Deleted task dictionary

    Raises:
        ValueError: If task not found
    """
    global _tasks

    for i, task in enumerate(_tasks):
        if task["id"] == task_id:
            deleted_task = _tasks.pop(i)
            return deleted_task

    raise ValueError(f"Task with ID {task_id} not found")
```

### 2.6 mark_complete()

```python
def mark_complete(task_id: int, completed: bool = True) -> Dict[str, Any]:
    """
    Mark task as complete or incomplete.

    Args:
        task_id: Task ID to update
        completed: True to mark complete, False for incomplete

    Returns:
        Updated task dictionary

    Raises:
        ValueError: If task not found
    """
    for task in _tasks:
        if task["id"] == task_id:
            task["completed"] = completed
            return task.copy()

    raise ValueError(f"Task with ID {task_id} not found")
```

### 2.7 reset_storage() (for testing)

```python
def reset_storage():
    """Reset storage to empty state. For testing only."""
    global _tasks, _next_id
    _tasks = []
    _next_id = 1
```

---

## Step 3: Implement app.py

**Purpose**: CLI interface using argparse

**File**: `src/todo/app.py`

### 3.1 Main Structure

```python
import argparse
import sys
from . import storage


def format_task(task):
    """Format task for display."""
    status = "[✓]" if task["completed"] else "[ ]"
    return f"ID: {task['id']}\n" \
           f"Status: {status}\n" \
           f"Title: {task['title']}\n" \
           f"Description: {task['description']}\n" \
           f"Created: {task['created_at']}"


def format_task_table(tasks):
    """Format tasks as a table."""
    if not tasks:
        return "No tasks yet. Use 'add' to create one."

    lines = []
    lines.append(f"{'ID':<4} {'Status':<8} {'Title':<40} {'Description':<50}")
    lines.append(f"{'──':<4} {'──────':<8} {'────────────────────────────────────────':<40} {'──────────────────────────────────────────────────':<50}")

    for task in tasks:
        status = "[✓]" if task["completed"] else "[ ]"
        title = task["title"][:37] + "..." if len(task["title"]) > 40 else task["title"]
        desc = task["description"][:47] + "..." if len(task["description"]) > 50 else task["description"]
        lines.append(f"{task['id']:<4} {status:<8} {title:<40} {desc:<50}")

    return "\n".join(lines)


def cmd_add(args):
    """Handle add command."""
    try:
        task = storage.add_task(args.title, args.description or "")
        print("Task created successfully!")
        print(format_task(task))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args):
    """Handle list command."""
    tasks = storage.list_tasks()
    print(format_task_table(tasks))
    return 0


def cmd_update(args):
    """Handle update command."""
    if args.title is None and args.description is None:
        print("Error: Must provide at least --title or --description", file=sys.stderr)
        return 1

    try:
        task = storage.update_task(args.id, args.title, args.description)
        print("Task updated successfully!")
        print(format_task(task))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_delete(args):
    """Handle delete command."""
    try:
        task = storage.delete_task(args.id)
        print("Task deleted successfully!")
        print(f"ID: {task['id']}")
        print(f"Title: {task['title']}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_complete(args):
    """Handle complete command."""
    try:
        completed = not args.incomplete
        task = storage.mark_complete(args.id, completed)
        status_text = "complete" if completed else "incomplete"
        status_icon = "[✓]" if completed else "[ ]"
        print(f"Task marked as {status_text}!")
        print(f"ID: {task['id']}")
        print(f"Title: {task['title']}")
        print(f"Status: {status_text.capitalize()} {status_icon}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog='todo.app',
        description='Phase I Todo Application - Basic CRUD Operations'
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Add command
    add_parser = subparsers.add_parser('add', help='Create a new task')
    add_parser.add_argument('title', help='Task title (1-200 characters)')
    add_parser.add_argument('--description', '-d', default='',
                           help='Task description (max 2000 characters)')
    add_parser.set_defaults(func=cmd_add)

    # List command
    list_parser = subparsers.add_parser('list', help='Display all tasks')
    list_parser.set_defaults(func=cmd_list)

    # Update command
    update_parser = subparsers.add_parser('update', help='Modify task details')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('--title', '-t', help='New task title')
    update_parser.add_argument('--description', '-d', help='New task description')
    update_parser.set_defaults(func=cmd_update)

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Remove a task')
    delete_parser.add_argument('id', type=int, help='Task ID')
    delete_parser.set_defaults(func=cmd_delete)

    # Complete command
    complete_parser = subparsers.add_parser('complete',
                                           help='Mark task as complete/incomplete')
    complete_parser.add_argument('id', type=int, help='Task ID')
    complete_parser.add_argument('--incomplete', action='store_true',
                                help='Mark as incomplete')
    complete_parser.set_defaults(func=cmd_complete)

    # Parse and execute
    args = parser.parse_args()
    exit_code = args.func(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
```

### 3.2 Package Initialization

**File**: `src/todo/__init__.py`

```python
"""Phase I Todo Application - Basic CRUD Operations"""

__version__ = "1.0.0"
```

---

## Step 4: Implement Tests

### 4.1 Unit Tests (test_storage.py)

**File**: `tests/test_storage.py`

```python
import unittest
from src.todo import storage


class TestStorage(unittest.TestCase):
    """Unit tests for storage layer."""

    def setUp(self):
        """Reset storage before each test."""
        storage.reset_storage()

    def test_add_task_success(self):
        """Test adding a valid task."""
        task = storage.add_task("Test Task", "Test Description")
        self.assertEqual(task["id"], 1)
        self.assertEqual(task["title"], "Test Task")
        self.assertEqual(task["description"], "Test Description")
        self.assertFalse(task["completed"])
        self.assertIn("created_at", task)

    def test_add_task_empty_title_fails(self):
        """Test that empty title raises error."""
        with self.assertRaises(ValueError):
            storage.add_task("")

    def test_add_task_long_title_fails(self):
        """Test that title > 200 chars raises error."""
        long_title = "a" * 201
        with self.assertRaises(ValueError):
            storage.add_task(long_title)

    def test_list_tasks_empty(self):
        """Test listing tasks when empty."""
        tasks = storage.list_tasks()
        self.assertEqual(tasks, [])

    def test_list_tasks_with_data(self):
        """Test listing tasks with data."""
        storage.add_task("Task 1")
        storage.add_task("Task 2")
        tasks = storage.list_tasks()
        self.assertEqual(len(tasks), 2)

    def test_update_task_success(self):
        """Test updating a task."""
        task = storage.add_task("Original Title")
        updated = storage.update_task(task["id"], title="New Title")
        self.assertEqual(updated["title"], "New Title")

    def test_update_nonexistent_task_fails(self):
        """Test updating non-existent task raises error."""
        with self.assertRaises(ValueError):
            storage.update_task(999, title="New Title")

    def test_delete_task_success(self):
        """Test deleting a task."""
        task = storage.add_task("Task to Delete")
        deleted = storage.delete_task(task["id"])
        self.assertEqual(deleted["id"], task["id"])
        self.assertEqual(len(storage.list_tasks()), 0)

    def test_delete_nonexistent_task_fails(self):
        """Test deleting non-existent task raises error."""
        with self.assertRaises(ValueError):
            storage.delete_task(999)

    def test_mark_complete_success(self):
        """Test marking task as complete."""
        task = storage.add_task("Task to Complete")
        updated = storage.mark_complete(task["id"], True)
        self.assertTrue(updated["completed"])

    def test_mark_incomplete_success(self):
        """Test marking task as incomplete."""
        task = storage.add_task("Task")
        storage.mark_complete(task["id"], True)
        updated = storage.mark_complete(task["id"], False)
        self.assertFalse(updated["completed"])

    def test_id_not_reused_after_delete(self):
        """Test that deleted IDs are not reused."""
        task1 = storage.add_task("Task 1")
        task2 = storage.add_task("Task 2")
        storage.delete_task(task1["id"])
        task3 = storage.add_task("Task 3")
        self.assertEqual(task3["id"], 3)  # Not 1!


if __name__ == '__main__':
    unittest.main()
```

### 4.2 Integration Tests (test_cli.py)

**File**: `tests/test_cli.py`

```python
import unittest
import subprocess
import sys
from src.todo import storage


class TestCLI(unittest.TestCase):
    """Integration tests for CLI."""

    def setUp(self):
        """Reset storage before each test."""
        storage.reset_storage()

    def run_cli(self, *args):
        """Helper to run CLI command."""
        result = subprocess.run(
            [sys.executable, '-m', 'todo.app'] + list(args),
            capture_output=True,
            text=True
        )
        return result

    def test_add_command_success(self):
        """Test add command with valid input."""
        result = self.run_cli('add', 'Test Task', '-d', 'Test Description')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Task created successfully!', result.stdout)
        self.assertIn('ID: 1', result.stdout)

    def test_add_command_empty_title_fails(self):
        """Test add command with empty title."""
        result = self.run_cli('add', '')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Error:', result.stderr)

    def test_list_command_empty(self):
        """Test list command with no tasks."""
        result = self.run_cli('list')
        self.assertEqual(result.returncode, 0)
        self.assertIn('No tasks yet', result.stdout)

    def test_list_command_with_tasks(self):
        """Test list command with tasks."""
        self.run_cli('add', 'Task 1')
        self.run_cli('add', 'Task 2')
        result = self.run_cli('list')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Task 1', result.stdout)
        self.assertIn('Task 2', result.stdout)

    def test_complete_command_success(self):
        """Test complete command."""
        self.run_cli('add', 'Task to Complete')
        result = self.run_cli('complete', '1')
        self.assertEqual(result.returncode, 0)
        self.assertIn('marked as complete', result.stdout)

    def test_update_command_success(self):
        """Test update command."""
        self.run_cli('add', 'Original Title')
        result = self.run_cli('update', '1', '--title', 'New Title')
        self.assertEqual(result.returncode, 0)
        self.assertIn('updated successfully', result.stdout)

    def test_delete_command_success(self):
        """Test delete command."""
        self.run_cli('add', 'Task to Delete')
        result = self.run_cli('delete', '1')
        self.assertEqual(result.returncode, 0)
        self.assertIn('deleted successfully', result.stdout)


if __name__ == '__main__':
    unittest.main()
```

---

## Step 5: Run Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_storage
python -m unittest tests.test_cli

# Run with coverage (if coverage.py installed - Phase II)
# coverage run -m unittest discover tests
# coverage report
```

---

## Step 6: Manual Testing

```bash
# Add tasks
python -m todo.app add "Buy groceries" -d "Milk, eggs, bread"
python -m todo.app add "Call mom"
python -m todo.app add "Write report" --description "Q4 summary"

# List tasks
python -m todo.app list

# Mark complete
python -m todo.app complete 1

# Update task
python -m todo.app update 2 --title "Call mom tonight"

# Delete task
python -m todo.app delete 3

# List again to verify
python -m todo.app list

# Test help
python -m todo.app --help
python -m todo.app add --help
```

---

## Common Issues & Solutions

### Issue: ModuleNotFoundError

**Solution**: Ensure you're running from the project root and using `-m` flag:
```bash
# From project root
python -m todo.app list
```

### Issue: Tests not found

**Solution**: Ensure `__init__.py` exists in tests directory:
```bash
touch tests/__init__.py
```

### Issue: Import errors in tests

**Solution**: Run tests as module from project root:
```bash
python -m unittest discover tests
```

---

## Checklist

Before moving to `/sp.tasks`:

- [ ] All 3 source files implemented (models.py, storage.py, app.py)
- [ ] All 5 commands working (add, list, update, delete, complete)
- [ ] Both test files implemented
- [ ] All tests passing
- [ ] Manual testing completed
- [ ] 80%+ test coverage achieved
- [ ] No external dependencies used
- [ ] Code follows PEP 8 style
- [ ] Docstrings added to all functions

---

## Next Steps

After implementation is complete:
1. Run `/sp.tasks` to break down implementation into specific tasks
2. Run `/sp.implement` to execute tasks
3. Create git commit after all tests pass
4. Update README.md with usage instructions

## Summary

This quickstart provides everything needed to implement Phase I:
- ✅ Complete code structure
- ✅ All function signatures and implementations
- ✅ Comprehensive test suite
- ✅ Testing commands and workflows
- ✅ Troubleshooting guide

**Ready for**: Task breakdown (`/sp.tasks`) and implementation (`/sp.implement`)
