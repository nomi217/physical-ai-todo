# Research & Design Decisions: Phase I Basic CRUD Operations

**Feature**: 001-phase-1-basics
**Date**: 2025-12-04
**Phase**: I - In-Memory Python Console App

## Overview

Phase I implements a console-based todo application with in-memory storage. This research document captures all architectural decisions, technology choices, and design patterns for the 5 basic CRUD operations.

## Technology Decisions

### 1. CLI Framework: argparse (Python Standard Library)

**Decision**: Use `argparse` for command-line argument parsing

**Rationale**:
- Part of Python standard library (zero external dependencies per constitution)
- Mature, well-documented, production-ready
- Automatic `--help` generation
- Supports subcommands (add, list, update, delete, complete)
- Type validation and error handling built-in
- Widely used pattern in Python CLI applications

**Alternatives Considered**:
- **click**: More modern, better UX, but requires external dependency (violates Phase I constraint)
- **typer**: Type-hint based, excellent DX, but requires external dependency
- **sys.argv**: Too low-level, manual parsing error-prone
- **getopt**: Older standard library option, less feature-rich than argparse

**References**:
- Python argparse docs: https://docs.python.org/3/library/argparse.html
- PEP 389: argparse - New Command Line Parsing Module

### 2. Storage Strategy: In-Memory List of Dictionaries

**Decision**: Use Python `list` containing `dict` objects for task storage

**Rationale**:
- Simplest possible implementation (constitution requires "smallest viable change")
- Direct mapping to Phase II database structure (smooth migration path)
- Fast for Phase I scale (< 100 tasks)
- No serialization overhead
- Easy to test and debug
- Data structure exactly matches constitution specification

**Data Structure**:
```python
tasks: List[Dict[str, Any]] = []

# Each task dict:
{
    "id": int,
    "title": str,
    "description": str,
    "completed": bool,
    "created_at": str  # ISO 8601
}
```

**Alternatives Considered**:
- **Named tuples**: Immutable, harder to update
- **dataclasses**: Requires Python 3.7+, adds complexity for Phase I
- **SQLite in-memory**: Overkill for Phase I, complicates testing
- **JSON file**: Adds I/O overhead, not required for Phase I

### 3. Testing Framework: unittest

**Decision**: Use `unittest` (Python standard library)

**Rationale**:
- Part of standard library (constitution requires zero external dependencies)
- Sufficient for Phase I testing needs
- XUnit-style familiar to most developers
- Built-in test discovery
- Coverage integration available
- Will migrate to pytest in Phase II (when external deps allowed)

**Test Strategy**:
- Unit tests: `test_storage.py` (CRUD operations, validation)
- Integration tests: `test_cli.py` (end-to-end CLI commands)
- Target: 80%+ coverage (constitution requirement)

**Alternatives Considered**:
- **pytest**: Superior to unittest (fixtures, parametrization), but external dependency
- **nose2**: Less maintained, adds complexity
- **doctest**: Good for examples, insufficient for comprehensive testing

### 4. ID Generation: Sequential Integer Counter

**Decision**: Auto-increment integer IDs starting from 1

**Rationale**:
- Simple, predictable, user-friendly for CLI
- Matches database auto-increment pattern (Phase II compatibility)
- No external dependencies (no UUID library needed)
- IDs never reused (constitution requirement for Phase II migration)

**Implementation**:
```python
next_id = max([task["id"] for task in tasks], default=0) + 1
```

**Alternatives Considered**:
- **UUID**: Overkill for single-user in-memory app, less user-friendly in CLI
- **Timestamp-based**: Non-sequential, collision risk
- **Hash-based**: Complex, unnecessary for Phase I

### 5. Timestamp Format: ISO 8601

**Decision**: Use `datetime.now().isoformat()` for timestamps

**Rationale**:
- Constitution explicitly specifies ISO 8601 format
- Human-readable and machine-parseable
- Sorts lexicographically
- Cross-platform consistent
- Python standard library support

**Format Example**: `2025-12-04T19:30:15.123456`

**Alternatives Considered**:
- **Unix timestamp**: Less readable, no advantage for Phase I
- **Custom format**: Adds complexity, non-standard

## Architecture Patterns

### 1. Three-Layer Architecture

**Decision**: Separate concerns into app.py, storage.py, models.py

**Rationale**:
- Follows constitution's specified architecture
- Testability: Each layer can be tested independently
- Maintainability: Clear separation of concerns
- Evolution: Easy to replace storage layer in Phase II
- Simplicity: No complex patterns (repository, service layer, etc.)

**Layers**:
```
┌─────────────┐
│   app.py    │  ← CLI interface (argparse)
└──────┬──────┘
       │
┌──────▼──────┐
│  storage.py │  ← CRUD operations (business logic)
└──────┬──────┘
       │
┌──────▼──────┐
│  models.py  │  ← Validation, data types
└─────────────┘
```

**Responsibilities**:
- **app.py**: Argument parsing, user input/output, command routing
- **storage.py**: Task CRUD operations, ID generation, in-memory list management
- **models.py**: Task validation (title length, description length, field types)

### 2. No Premature Abstractions

**Decision**: Direct implementation without design patterns

**Rationale**:
- Constitution principle: "No over-engineering, only changes directly requested"
- Phase I scope is small (5 operations, <100 tasks)
- Patterns like Repository, Factory, Strategy add complexity without benefit
- Easy to refactor in Phase II when database is added

**What We're NOT Using**:
- ❌ Repository pattern (direct storage access is fine)
- ❌ Dependency injection (simple imports sufficient)
- ❌ Abstract base classes (no polymorphism needed)
- ❌ Singleton pattern (module-level storage is adequate)

## Input Validation Strategy

### 1. Validation Location: models.py

**Decision**: Centralize validation logic in models.py

**Validation Rules** (from specification):
- Title: Required, 1-200 characters, non-empty after strip
- Description: Optional, max 2000 characters
- Task ID: Integer, must exist in storage
- All inputs: Sanitize for console output

**Implementation Approach**:
```python
def validate_task(title: str, description: str = "") -> Dict[str, str]:
    errors = {}
    if not title or not title.strip():
        errors["title"] = "Title is required"
    if len(title) > 200:
        errors["title"] = "Title must be 200 characters or less"
    if len(description) > 2000:
        errors["description"] = "Description must be 2000 characters or less"
    return errors
```

### 2. Error Handling: Explicit Error Messages

**Decision**: Return clear, actionable error messages

**Examples**:
- "Error: Title is required"
- "Error: Task ID 5 not found"
- "Error: Description exceeds 2000 character limit"

**Rationale**:
- Specification requires "clear error messages"
- User experience: Help users fix mistakes
- No silent failures or cryptic errors

## Testing Strategy

### 1. Test Coverage: 80%+ Required

**Test Organization**:
```
tests/
├── test_storage.py   # Unit tests for CRUD operations
│   ├── test_add_task
│   ├── test_list_tasks
│   ├── test_update_task
│   ├── test_delete_task
│   ├── test_mark_complete
│   └── test_validation
└── test_cli.py       # Integration tests for CLI
    ├── test_add_command
    ├── test_list_command
    ├── test_update_command
    ├── test_delete_command
    └── test_complete_command
```

### 2. Test Data Fixtures

**Approach**: Create sample tasks in setUp() for each test class

**Example Fixture**:
```python
def setUp(self):
    self.sample_tasks = [
        {"id": 1, "title": "Task 1", "description": "",
         "completed": False, "created_at": "2025-12-04T10:00:00"},
        {"id": 2, "title": "Task 2", "description": "Details",
         "completed": True, "created_at": "2025-12-04T11:00:00"}
    ]
```

## Console Output Format

### 1. Task Display Format

**Decision**: Readable table-like format with status indicators

**Example Output**:
```
ID  Status  Title                Description
──  ──────  ───────────────────  ─────────────
1   [ ]     Buy groceries        Milk, eggs
2   [✓]     Call mom
3   [ ]     Write report         Q4 summary
```

**Rationale**:
- Specification requires "readable console format"
- Visual distinction between complete/incomplete (✓ vs empty)
- Handles long descriptions gracefully (truncate if needed)

### 2. Empty List Handling

**Decision**: Show helpful message when no tasks

**Output**: `"No tasks yet. Use 'add' to create one."`

**Rationale**: Specification explicitly requires helpful empty state message

## Phase II Evolution Path

### 1. Data Model Compatibility

**Phase I → Phase II Migration**:
- Phase I: `{"id": int, "title": str, "description": str, "completed": bool, "created_at": str}`
- Phase II adds: `"priority": str, "tags": str, "updated_at": datetime`
- Existing fields remain unchanged → smooth migration

### 2. Storage Layer Replacement

**Plan**:
- Phase I: `storage.py` uses in-memory list
- Phase II: Replace with SQLModel + Postgres
- Interface remains same: `add_task()`, `list_tasks()`, etc.
- CLI code (app.py) unchanged

### 3. Technology Additions (Phase II)

**New in Phase II**:
- FastAPI (REST API alongside CLI)
- SQLModel (ORM)
- Neon Postgres (database)
- pytest (better testing, external deps now allowed)
- Next.js (web frontend)

## Open Questions Resolved

**Q1: Should we validate input lengths or truncate?**
- **Answer**: Validate and reject (better UX, preserves user intent)

**Q2: Should deleted task IDs be reused?**
- **Answer**: No (constitution requires gaps for Phase II database migration)

**Q3: Should we handle Unicode/emojis in task titles?**
- **Answer**: Yes, handle gracefully (Python 3 supports Unicode natively)

**Q4: Should we colorize output?**
- **Answer**: No (adds dependency or complexity, not in specification)

**Q5: Should we persist data to file?**
- **Answer**: No (Phase I explicitly in-memory only, persistence is Phase II)

## Summary

This research phase has resolved all technical uncertainties for Phase I implementation:

✅ **Technology Stack**: Python 3.13+, argparse, unittest (all standard library)
✅ **Architecture**: Three-layer (app/storage/models)
✅ **Storage**: In-memory list of dicts
✅ **Validation**: Centralized in models.py, reject invalid input
✅ **Testing**: unittest with 80%+ coverage
✅ **Evolution**: Phase II-compatible data model and interfaces

**No NEEDS CLARIFICATION items remain** - ready for data model design (Phase 1).
