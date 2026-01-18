# Phase Migration Helper

Guide migration from Phase I (console app) to Phase II (web app) while maintaining backward compatibility.

## What This Skill Does

Analyzes current Phase I implementation and provides step-by-step migration plan to Phase II, ensuring:
- Data model compatibility
- Backward compatibility for existing CLI
- Smooth transition path
- No breaking changes

## Usage

```
/migrate-phase [check|plan|verify]
```

- **check** - Analyze Phase I readiness for migration
- **plan** - Generate detailed migration plan
- **verify** - Verify Phase II maintains Phase I compatibility

## Phase I → Phase II Changes

### New Features (Phase II)
- ✅ Priorities (high, medium, low)
- ✅ Tags (multiple per task)
- ✅ Search & Filter
- ✅ Sort tasks
- ✅ Database persistence (Neon Postgres)
- ✅ Web interface (Next.js)
- ✅ REST API (FastAPI)
- ✅ User authentication (Better Auth)

### Technical Changes
- In-memory list → SQLModel + Postgres
- CLI only → CLI + API + Web UI
- Single user → Multi-user
- Zero dependencies → Modern stack

## Execution Steps

### Mode: check

**Purpose**: Verify Phase I is ready for migration

1. **Check data model**:
   - Read `src/todo/storage.py`
   - Verify task structure matches Phase I spec
   - Ensure ID gaps are preserved (migration-safe)

2. **Check CLI implementation**:
   - Verify all 5 commands work
   - Run test suite
   - Confirm 80%+ coverage

3. **Check for Phase II leaks**:
   - Search for premature Phase II features
   - Flag any priorities, tags, search, database code

4. **Generate readiness report**:
```
Phase Migration Readiness Report
=================================

Phase I Status: COMPLETE ✅

Data Model: COMPATIBLE ✅
- Task structure matches specification
- ID gaps preserved (1, 2, 4, 7...)
- created_at uses ISO 8601 format

CLI Implementation: READY ✅
- All 5 commands functional
- Tests passing (25/25)
- Coverage: 85%

Phase II Leaks: NONE ✅
- No premature features detected
- Clean Phase I implementation

Migration Safety: HIGH ✅

Recommendations:
1. Create Phase II branch
2. Review migration plan with /migrate-phase plan
3. Begin with data model extension
```

### Mode: plan

**Purpose**: Generate detailed migration plan

1. **Read Phase I implementation**:
   - Current data model
   - Storage layer interface
   - CLI commands

2. **Generate migration tasks**:

```markdown
Phase I → Phase II Migration Plan
===================================

## Step 1: Data Model Extension

**File**: Create `src/models/task.py` (new SQLModel)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    # Phase I fields (unchanged)
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    # Phase II additions
    priority: str = Field(default="medium")  # high, medium, low
    tags: str = Field(default="[]")  # JSON array as string
    updated_at: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = Field(default=None, foreign_key="users.id")
```

**Backward Compatibility**: Phase I CLI can ignore new fields

## Step 2: Database Setup

- Install: sqlmodel, psycopg2-binary
- Configure: Neon Postgres connection
- Migrations: Alembic setup
- Seed: Migrate Phase I test data

## Step 3: Storage Layer Replacement

**Keep**: `src/todo/storage.py` (Phase I compatibility layer)
**Add**: `src/api/db.py` (SQLModel database layer)

Phase I storage.py becomes a wrapper:
```python
# Forward to database
def add_task(title, description=""):
    from api.db import create_task
    return create_task(title, description)
```

## Step 4: API Layer

**Add**: `src/api/` directory
- `main.py` - FastAPI app
- `routes/tasks.py` - Task endpoints
- `routes/auth.py` - Authentication
- `models/` - Pydantic schemas
- `db.py` - Database session

## Step 5: Frontend

**Add**: `frontend/` directory (Next.js)
- Connect to FastAPI backend
- Implement task CRUD UI
- Add priority, tags, search, filter
- Authentication flow

## Step 6: Testing

- Migrate Phase I tests to database
- Add API integration tests
- Add E2E tests for web UI
- Maintain 80%+ coverage

## Step 7: Deployment

- Deploy database (Neon)
- Deploy API (Railway/Vercel)
- Deploy frontend (Vercel)
- Keep CLI functional
```

3. **Generate compatibility checklist**:

```
Phase II Compatibility Checklist
=================================

✅ Phase I CLI continues to work
✅ Phase I data model is subset of Phase II
✅ Existing task IDs preserved
✅ ID gaps maintained
✅ created_at format unchanged (ISO 8601)
✅ Validation rules unchanged
✅ Phase I tests still pass
✅ No breaking changes to Phase I interface
```

### Mode: verify

**Purpose**: After Phase II implementation, verify compatibility

1. **Run Phase I tests**:
```bash
python -m unittest discover tests
```
All should pass (Phase I functionality preserved)

2. **Test Phase I CLI against Phase II database**:
```bash
python -m todo.app add "Test task"
python -m todo.app list
```
Should work identically to Phase I

3. **Verify data model**:
- Check Phase II database
- Confirm Phase I fields unchanged
- Verify new fields have correct defaults

4. **Generate compatibility report**:

```
Phase II Compatibility Verification
====================================

Phase I Tests: 25/25 PASS ✅
Phase I CLI: ALL COMMANDS WORKING ✅

Data Model Compatibility:
- Phase I fields: UNCHANGED ✅
- New fields: DEFAULTS CORRECT ✅
- ID sequence: PRESERVED ✅

Breaking Changes: NONE ✅

Phase II Features Working:
- Priorities: ✅
- Tags: ✅
- Search: ✅
- Web UI: ✅
- Multi-user: ✅

Migration: SUCCESSFUL ✅
```

## Output Format

Choose output based on mode:

**check mode**: Readiness report with pass/fail status
**plan mode**: Detailed step-by-step migration guide
**verify mode**: Compatibility verification report

## Notes

- Phase I must be complete before migration
- Migration is non-destructive (Phase I continues working)
- Data model is additive (no removals)
- CLI becomes wrapper around new database layer
- All Phase I tests must continue passing
- Constitution principles still apply (no over-engineering)

## Related Commands

- `/check-constitution` - Verify Phase I compliance before migration
- `/test-python` - Run Phase I tests
- `/sp.plan` - Generate Phase II implementation plan
