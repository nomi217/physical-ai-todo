# Implementation Plan: Phase I Basic CRUD Operations

**Branch**: `001-phase-1-basics` | **Date**: 2025-12-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-1-basics/spec.md`

## Summary

Implement 5 basic CRUD operations (Add, View, Update, Delete, Mark Complete) for a Python console-based todo application with in-memory storage. This establishes the foundation for Phase II (web app + database) and Phase III (AI chatbot).

**Technical Approach**:
- Python 3.13+ with standard library only (argparse, unittest, datetime)
- Three-layer architecture: app.py (CLI), storage.py (CRUD), models.py (validation)
- In-memory storage using list of dictionaries
- Sequential integer IDs with no reuse after deletion
- 80%+ test coverage using unittest

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (standard library only: argparse, unittest, datetime)
**Storage**: In-memory (Python list of dict)
**Testing**: unittest (standard library)
**Target Platform**: Cross-platform (Windows, Linux, macOS)
**Project Type**: Single console application
**Performance Goals**: <1 second response time for all operations
**Constraints**: Zero external dependencies, 80%+ test coverage, <200 chars title, <2000 chars description
**Scale/Scope**: 5 CRUD operations, designed for <100 tasks in single session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Compliance**:

| Requirement | Status | Evidence |
|-------------|--------|----------|
| **5 Basic Features** | ✅ PASS | Add, View, Update, Delete, Mark Complete all specified |
| **Python 3.13+** | ✅ PASS | Language version confirmed |
| **argparse CLI** | ✅ PASS | Specified in technical context |
| **In-memory storage** | ✅ PASS | List of dict implementation planned |
| **unittest testing** | ✅ PASS | Testing framework specified |
| **Zero external dependencies** | ✅ PASS | Standard library only |
| **Data model** | ✅ PASS | Matches constitution exactly (id, title, description, completed, created_at) |
| **Architecture** | ✅ PASS | app.py, storage.py, models.py as specified |
| **80%+ test coverage** | ✅ PASS | Target confirmed in testing strategy |
| **No Phase II features** | ✅ PASS | No priorities, tags, search, database, web UI, auth |

**Phase II Exclusions Verified**:
- ❌ Priorities & Tags (not in scope)
- ❌ Search & Filter (not in scope)
- ❌ Sort Tasks (not in scope)
- ❌ Database persistence (not in scope)
- ❌ Web interface (not in scope)
- ❌ User authentication (not in scope)

**Result**: ✅ **ALL GATES PASSED** - No constitution violations

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-1-basics/
├── spec.md                  # Feature specification
├── plan.md                  # This file - implementation plan
├── research.md              # Phase 0 research & design decisions
├── data-model.md            # Phase 1 data model specification
├── quickstart.md            # Phase 1 implementation guide
├── contracts/               # Phase 1 CLI command contracts
│   └── cli-commands.md
├── checklists/
│   └── requirements.md      # Specification quality checklist
└── tasks.md                 # Phase 2 task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
src/
└── todo/
    ├── __init__.py          # Package initialization
    ├── app.py               # CLI entry point (argparse parser, command handlers)
    ├── storage.py           # In-memory CRUD operations (add, list, update, delete, mark_complete)
    └── models.py            # Validation logic (validate_title, validate_description)

tests/
├── __init__.py
├── test_storage.py          # Unit tests for storage layer (80%+ coverage)
└── test_cli.py              # Integration tests for CLI commands

requirements.txt             # Empty (no external dependencies)
README.md                    # User documentation (installation, usage)
```

**Structure Decision**: Single console application using Option 1 (single project). The three-layer architecture (app/storage/models) provides clear separation of concerns while maintaining simplicity appropriate for Phase I scope. This structure will evolve smoothly to Phase II by replacing storage.py with database ORM while keeping app.py and models.py largely unchanged.

## Complexity Tracking

*No violations - this section intentionally left empty*

All design decisions comply with constitution requirements. No premature abstractions, design patterns, or additional complexity beyond the specified architecture.

## Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────┐
│           User (Terminal)               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           app.py (CLI Layer)            │
│  - argparse command parser              │
│  - Command handlers (cmd_add, cmd_list) │
│  - Output formatting (tables, messages) │
│  - Error handling and exit codes        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        storage.py (Business Logic)      │
│  - add_task(), list_tasks()             │
│  - update_task(), delete_task()         │
│  - mark_complete()                      │
│  - In-memory task list management       │
│  - ID generation                        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       models.py (Validation Layer)      │
│  - validate_title()                     │
│  - validate_description()               │
│  - validate_task_data()                 │
│  - Data type definitions                │
└─────────────────────────────────────────┘
```

**Layer Responsibilities**:

1. **app.py (CLI Layer)**:
   - Parse command-line arguments using argparse
   - Route commands to appropriate handlers
   - Format output for console display
   - Handle user input/output
   - Return appropriate exit codes (0 = success, 1 = error)

2. **storage.py (Business Logic)**:
   - Implement all CRUD operations
   - Manage in-memory task list
   - Generate sequential task IDs
   - Enforce business rules
   - Raise ValueError on validation failures

3. **models.py (Validation Layer)**:
   - Validate title length (1-200 chars)
   - Validate description length (max 2000 chars)
   - Check for empty/whitespace inputs
   - Return error messages for invalid data

### Data Flow

**Example: Adding a Task**

```
User: python -m todo.app add "Buy milk" -d "From store"
  │
  ▼
app.py: Parse arguments → Call storage.add_task("Buy milk", "From store")
  │
  ▼
storage.py: Call models.validate_task_data("Buy milk", "From store")
  │
  ▼
models.py: Check title length, check description length → Return None (valid)
  │
  ▼
storage.py: Create task dict → Append to _tasks list → Increment _next_id
  │
  ▼
app.py: Format output → Print "Task created successfully!" + details
  │
  ▼
User: Sees formatted output in terminal
```

## Key Design Decisions

### 1. CLI Framework: argparse

**Rationale**: See [research.md](./research.md#1-cli-framework-argparse-python-standard-library)
- Part of Python standard library (zero dependencies)
- Automatic --help generation
- Subcommand support
- Type validation built-in

**Alternative rejected**: click, typer (require external dependencies)

### 2. Storage: In-Memory List of Dicts

**Rationale**: See [research.md](./research.md#2-storage-strategy-in-memory-list-of-dictionaries)
- Simplest implementation
- Direct mapping to Phase II database
- Fast for <100 tasks
- No serialization overhead

**Data structure**:
```python
_tasks: List[Dict[str, Any]] = []
```

**Alternative rejected**: SQLite in-memory (overkill), JSON file (not required)

### 3. ID Generation: Sequential Integer

**Rationale**: See [research.md](./research.md#4-id-generation-sequential-integer-counter)
- User-friendly for CLI
- Matches database auto-increment (Phase II)
- Never reuses deleted IDs (migration-safe)

**Implementation**:
```python
_next_id: int = 1  # Module-level counter
```

**Alternative rejected**: UUID (overkill), timestamp-based (collisions)

### 4. No Premature Abstractions

**Rationale**: Constitution requires "smallest viable change"
- No repository pattern
- No dependency injection
- No abstract base classes
- Direct function calls

**What we're NOT doing**:
- ❌ Repository pattern (direct storage access)
- ❌ Singleton pattern (module-level storage)
- ❌ Factory pattern (direct dict creation)
- ❌ Strategy pattern (no polymorphism needed)

### 5. Validation Strategy: Explicit Errors

**Rationale**: Better UX, preserves user intent
- Reject oversized input (don't truncate)
- Clear error messages
- No silent failures

**Example**:
```python
if len(title) > 200:
    raise ValueError(f"Title must be 200 characters or less (current: {len(title)} characters)")
```

## Implementation Strategy

### Phase 0: Research (COMPLETED)

**Output**: [research.md](./research.md)

**Key Decisions Made**:
- Technology choices (argparse, unittest, in-memory)
- Architecture patterns (three-layer, no abstractions)
- Validation strategy (reject vs truncate)
- ID generation (sequential, no reuse)
- Console output format (table with status icons)

### Phase 1: Design & Contracts (COMPLETED)

**Outputs**:
- [data-model.md](./data-model.md) - Task entity specification
- [contracts/cli-commands.md](./contracts/cli-commands.md) - CLI command specifications
- [quickstart.md](./quickstart.md) - Implementation guide

**Artifacts Created**:
1. **Data Model**: Task schema, validation rules, state transitions
2. **CLI Contracts**: 5 commands with syntax, parameters, output formats, error conditions
3. **Quickstart Guide**: Step-by-step implementation instructions with code examples

### Phase 2: Task Breakdown (NEXT STEP)

**Action**: Run `/sp.tasks` to generate `tasks.md`

**Expected Tasks**:
1. Implement models.py (validation functions)
2. Implement storage.py (CRUD operations)
3. Implement app.py (CLI interface)
4. Implement test_storage.py (unit tests)
5. Implement test_cli.py (integration tests)
6. Verify 80%+ test coverage
7. Manual testing
8. Update README.md with usage instructions

### Phase 3: Implementation (AFTER TASKS)

**Action**: Run `/sp.implement` to execute tasks

**Workflow**:
1. Generate code for each task
2. Run tests
3. Fix failures (refine spec if needed)
4. Commit when all tests pass

## Testing Strategy

### Test Organization

```
tests/
├── test_storage.py          # Unit tests (business logic)
│   ├── test_add_task_success
│   ├── test_add_task_validation_errors
│   ├── test_list_tasks_empty
│   ├── test_list_tasks_with_data
│   ├── test_update_task_success
│   ├── test_delete_task_success
│   ├── test_mark_complete_toggle
│   └── test_id_not_reused
│
└── test_cli.py              # Integration tests (end-to-end)
    ├── test_add_command_success
    ├── test_list_command_output
    ├── test_update_command_success
    ├── test_delete_command_success
    ├── test_complete_command_success
    └── test_error_handling
```

### Coverage Target

**Requirement**: 80%+ line coverage (constitution mandate)

**Measurement**:
```bash
python -m unittest discover tests
# Manual coverage check: All functions in app.py, storage.py, models.py tested
```

**Coverage Strategy**:
- Unit tests: 100% of storage.py and models.py functions
- Integration tests: All CLI commands with success and error paths
- Edge cases: Boundary values, special characters, empty states

### Test Data Fixtures

**Standard Fixture** (see [data-model.md](./data-model.md#testing-considerations)):
```python
FIXTURE_TASKS = [
    {"id": 1, "title": "Task 1", "description": "Desc 1",
     "completed": False, "created_at": "2025-12-04T10:00:00"},
    {"id": 2, "title": "Task 2", "description": "",
     "completed": True, "created_at": "2025-12-04T11:00:00"}
]
```

## Evolution to Phase II

### Migration Plan

**Phase II Changes**:
1. Replace `storage.py` with SQLModel + Postgres ORM
2. Add FastAPI REST API alongside CLI
3. Add Next.js web frontend
4. Add user authentication (Better Auth)
5. Extend data model: priority, tags, updated_at, user_id

**Backward Compatibility**:
- ✅ Existing CLI commands remain functional
- ✅ Data model is subset of Phase II model
- ✅ Task IDs persist (gaps preserved for migration)
- ✅ app.py requires minimal changes

**Data Model Evolution**:
```python
# Phase I
Task = {
    "id": int,
    "title": str,
    "description": str,
    "completed": bool,
    "created_at": str
}

# Phase II (adds new fields, keeps existing)
Task = {
    # Phase I fields (unchanged)
    "id": int,
    "title": str,
    "description": str,
    "completed": bool,
    "created_at": str,
    # New fields
    "priority": str,
    "tags": str,
    "updated_at": str,
    "user_id": str
}
```

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Unicode display issues (Windows console) | Medium | Low | Handle gracefully, fallback to ASCII |
| ID collision after 2^31 tasks | Very Low | Low | Not a concern for Phase I scope |
| Test coverage < 80% | Low | High | Comprehensive test plan included in quickstart |
| Manual coding instead of /sp.implement | Medium | High | Constitution enforcement, clear warnings |

### Project Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep (adding Phase II features) | Medium | High | Strict constitution compliance checks |
| Premature optimization | Low | Medium | "No over-engineering" principle enforced |
| Skipping tests | Low | High | 80%+ coverage is gate for completion |

## Success Criteria

**Phase I is complete when**:
- ✅ All 5 basic features working (add, view, update, delete, mark complete)
- ✅ All CLI commands functional with correct output format
- ✅ 80%+ test coverage achieved
- ✅ All tests passing (unittest)
- ✅ Zero external dependencies (verified)
- ✅ README.md with installation and usage instructions
- ✅ Manual testing completed successfully
- ✅ Constitution compliance verified
- ✅ PHR created for planning session

## Artifacts Summary

**Generated by /sp.plan**:
1. ✅ `plan.md` (this file) - Complete architectural plan
2. ✅ `research.md` - Technology decisions and design rationale
3. ✅ `data-model.md` - Task entity specification
4. ✅ `contracts/cli-commands.md` - CLI command contracts
5. ✅ `quickstart.md` - Implementation guide with code examples

**Next Step**: Run `/sp.tasks` to generate task breakdown (`tasks.md`)

## References

- **Constitution**: `.specify/memory/constitution.md` (Phase I requirements)
- **Specification**: `specs/001-phase-1-basics/spec.md` (Feature requirements)
- **Research**: `specs/001-phase-1-basics/research.md` (Design decisions)
- **Data Model**: `specs/001-phase-1-basics/data-model.md` (Entity schema)
- **CLI Contracts**: `specs/001-phase-1-basics/contracts/cli-commands.md` (Command specifications)
- **Quickstart**: `specs/001-phase-1-basics/quickstart.md` (Implementation guide)

---

**Plan Status**: ✅ **COMPLETE** - Ready for task breakdown (`/sp.tasks`)

**Constitution Compliance**: ✅ **VERIFIED** - All Phase I requirements met, no Phase II features included

**Next Command**: `/sp.tasks` to generate task breakdown for implementation
