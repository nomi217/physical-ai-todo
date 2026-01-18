# CLI Command Contracts: Phase I

**Feature**: 001-phase-1-basics
**Date**: 2025-12-04
**Interface**: Command-line (argparse)

## Overview

This document specifies the command-line interface contracts for all 5 basic CRUD operations. Each command definition includes syntax, parameters, output format, and error conditions.

## General Command Structure

```bash
python -m todo.app <command> [arguments] [options]
```

**Common Options** (all commands):
- `--help`, `-h`: Display help message

**Exit Codes**:
- `0`: Success
- `1`: Error (validation failure, task not found, etc.)

**Error Output Format**:
```
Error: <descriptive error message>
```

---

## Command: add

**Purpose**: Create a new task

**Syntax**:
```bash
python -m todo.app add <title> [--description <text>]
python -m todo.app add "<title>" [-d "<text>"]
```

**Parameters**:

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `title` | string | Yes | 1-200 chars, non-empty | Task title |
| `--description`, `-d` | string | No | Max 2000 chars | Task description |

**Success Output**:
```
Task created successfully!
ID: 1
Title: Buy groceries
Description: Milk, eggs, bread
Status: Incomplete
Created: 2025-12-04T19:30:15
```

**Error Conditions**:

| Condition | Error Message | Exit Code |
|-----------|---------------|-----------|
| Missing title | `Error: Title is required` | 1 |
| Empty/whitespace title | `Error: Title cannot be only whitespace` | 1 |
| Title > 200 chars | `Error: Title must be 200 characters or less (current: N characters)` | 1 |
| Description > 2000 chars | `Error: Description must be 2000 characters or less (current: N characters)` | 1 |

**Examples**:
```bash
# Basic task
python -m todo.app add "Buy groceries"

# Task with description
python -m todo.app add "Write report" --description "Q4 financial summary"

# Short option
python -m todo.app add "Call mom" -d "Discuss weekend plans"

# Title with quotes and special characters
python -m todo.app add "Finish 'Project Alpha' documentation"
```

---

## Command: list

**Purpose**: Display all tasks

**Syntax**:
```bash
python -m todo.app list
```

**Parameters**: None

**Success Output (with tasks)**:
```
ID  Status  Title                Description
──  ──────  ───────────────────  ─────────────────
1   [ ]     Buy groceries        Milk, eggs, bread
2   [✓]     Call mom
3   [ ]     Write report         Q4 financial summary
```

**Success Output (empty list)**:
```
No tasks yet. Use 'add' to create one.
```

**Column Specifications**:
- **ID**: Integer, right-aligned
- **Status**: `[✓]` (completed) or `[ ]` (incomplete)
- **Title**: Left-aligned, truncate if > 40 chars with "..."
- **Description**: Left-aligned, truncate if > 50 chars with "..."

**Error Conditions**: None (always succeeds)

**Examples**:
```bash
# List all tasks
python -m todo.app list
```

---

## Command: update

**Purpose**: Modify task title and/or description

**Syntax**:
```bash
python -m todo.app update <id> [--title <text>] [--description <text>]
python -m todo.app update <id> [-t <text>] [-d <text>]
```

**Parameters**:

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `id` | integer | Yes | Must exist | Task ID to update |
| `--title`, `-t` | string | No* | 1-200 chars | New title |
| `--description`, `-d` | string | No* | Max 2000 chars | New description |

*At least one of `--title` or `--description` must be provided

**Success Output**:
```
Task updated successfully!
ID: 1
Title: Buy groceries and fruits
Description: Milk, eggs, bread, apples, oranges
Status: Incomplete
Created: 2025-12-04T19:30:15
```

**Error Conditions**:

| Condition | Error Message | Exit Code |
|-----------|---------------|-----------|
| Missing ID | `Error: Task ID is required` | 1 |
| Invalid ID (non-integer) | `Error: Task ID must be an integer` | 1 |
| ID not found | `Error: Task with ID N not found` | 1 |
| No fields provided | `Error: Must provide at least --title or --description` | 1 |
| Title > 200 chars | `Error: Title must be 200 characters or less (current: N characters)` | 1 |
| Description > 2000 chars | `Error: Description must be 2000 characters or less (current: N characters)` | 1 |
| Empty title | `Error: Title cannot be empty` | 1 |

**Examples**:
```bash
# Update title only
python -m todo.app update 1 --title "Buy groceries and fruits"

# Update description only
python -m todo.app update 1 --description "New detailed description"

# Update both
python -m todo.app update 1 -t "New title" -d "New description"
```

---

## Command: delete

**Purpose**: Permanently remove a task

**Syntax**:
```bash
python -m todo.app delete <id>
```

**Parameters**:

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `id` | integer | Yes | Must exist | Task ID to delete |

**Success Output**:
```
Task deleted successfully!
ID: 1
Title: Buy groceries
```

**Error Conditions**:

| Condition | Error Message | Exit Code |
|-----------|---------------|-----------|
| Missing ID | `Error: Task ID is required` | 1 |
| Invalid ID (non-integer) | `Error: Task ID must be an integer` | 1 |
| ID not found | `Error: Task with ID N not found` | 1 |

**Notes**:
- Deletion is permanent (no undo)
- Deleted IDs are never reused
- Deleted task no longer appears in `list` output

**Examples**:
```bash
# Delete task by ID
python -m todo.app delete 5
```

---

## Command: complete

**Purpose**: Mark task as complete or incomplete

**Syntax**:
```bash
python -m todo.app complete <id> [--incomplete]
```

**Parameters**:

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `id` | integer | Yes | Must exist | Task ID to mark |
| `--incomplete` | flag | No | - | Mark as incomplete instead |

**Success Output (marking complete)**:
```
Task marked as complete!
ID: 1
Title: Buy groceries
Status: Complete [✓]
```

**Success Output (marking incomplete)**:
```
Task marked as incomplete!
ID: 1
Title: Buy groceries
Status: Incomplete [ ]
```

**Error Conditions**:

| Condition | Error Message | Exit Code |
|-----------|---------------|-----------|
| Missing ID | `Error: Task ID is required` | 1 |
| Invalid ID (non-integer) | `Error: Task ID must be an integer` | 1 |
| ID not found | `Error: Task with ID N not found` | 1 |

**Notes**:
- Can toggle completion status multiple times
- Default action (no --incomplete flag): mark as complete
- With --incomplete flag: mark as incomplete

**Examples**:
```bash
# Mark task as complete
python -m todo.app complete 1

# Mark task as incomplete
python -m todo.app complete 1 --incomplete
```

---

## Help Command

**Purpose**: Display usage information

**Syntax**:
```bash
python -m todo.app --help
python -m todo.app <command> --help
```

**Output (main help)**:
```
usage: todo.app [-h] {add,list,update,delete,complete} ...

Phase I Todo Application - Basic CRUD Operations

positional arguments:
  {add,list,update,delete,complete}
    add                 Create a new task
    list                Display all tasks
    update              Modify task details
    delete              Remove a task
    complete            Mark task as complete/incomplete

options:
  -h, --help            show this help message and exit
```

**Output (command help, e.g., `add --help`)**:
```
usage: todo.app add [-h] [--description DESCRIPTION] title

positional arguments:
  title                 Task title (1-200 characters)

options:
  -h, --help            show this help message and exit
  --description DESCRIPTION, -d DESCRIPTION
                        Task description (max 2000 characters)
```

---

## Implementation Notes

### Argparse Configuration

**Parser Structure**:
```python
parser = argparse.ArgumentParser(
    prog='todo.app',
    description='Phase I Todo Application - Basic CRUD Operations'
)
subparsers = parser.add_subparsers(dest='command', required=True)

# Add command
add_parser = subparsers.add_parser('add', help='Create a new task')
add_parser.add_argument('title', help='Task title (1-200 characters)')
add_parser.add_argument('--description', '-d', help='Task description (max 2000 characters)')

# List command
list_parser = subparsers.add_parser('list', help='Display all tasks')

# Update command
update_parser = subparsers.add_parser('update', help='Modify task details')
update_parser.add_argument('id', type=int, help='Task ID')
update_parser.add_argument('--title', '-t', help='New task title')
update_parser.add_argument('--description', '-d', help='New task description')

# Delete command
delete_parser = subparsers.add_parser('delete', help='Remove a task')
delete_parser.add_argument('id', type=int, help='Task ID')

# Complete command
complete_parser = subparsers.add_parser('complete', help='Mark task as complete/incomplete')
complete_parser.add_argument('id', type=int, help='Task ID')
complete_parser.add_argument('--incomplete', action='store_true', help='Mark as incomplete')
```

### Output Formatting

**Table Display**:
- Use Python's built-in string formatting
- Fixed-width columns with padding
- Separator line using Unicode box-drawing characters (─)
- Truncate long text with ellipsis (...)

**Color/Styling**: None (avoid external dependencies, cross-platform issues)

### Error Handling

**Pattern**:
```python
try:
    result = storage.add_task(title, description)
    print("Task created successfully!")
    print(f"ID: {result['id']}")
    # ... more output
    sys.exit(0)
except ValueError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

## Testing Contract Compliance

**Test Cases** (for each command):
1. **Happy path**: Valid input, verify output format matches specification
2. **Error cases**: Each error condition, verify correct error message and exit code
3. **Boundary values**: Max length inputs, empty inputs
4. **Edge cases**: Special characters, Unicode, whitespace

**Example Test**:
```python
def test_add_command_success(self):
    """Test add command with valid input."""
    result = subprocess.run(
        ['python', '-m', 'todo.app', 'add', 'Test Task', '-d', 'Test Description'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert 'Task created successfully!' in result.stdout
    assert 'ID: 1' in result.stdout
```

## Summary

**CLI Contract Characteristics**:
- ✅ 5 commands (add, list, update, delete, complete)
- ✅ Clear syntax and parameter specifications
- ✅ Consistent output formatting
- ✅ Descriptive error messages
- ✅ Standard exit codes
- ✅ Built-in help system
- ✅ No external dependencies

**Ready for**: Quickstart guide and implementation (Phase 1 continuation)
