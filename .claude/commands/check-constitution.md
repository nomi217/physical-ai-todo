# Constitution Compliance Checker

Verify that the current implementation complies with the Physical AI Todo Application constitution.

## What to Check

### Phase I Requirements (Current Phase)

1. **Five Basic Features Only**:
   - ✅ Add task (create)
   - ✅ View tasks (list)
   - ✅ Update task
   - ✅ Delete task
   - ✅ Mark complete/incomplete
   - ❌ NO Phase II features (priorities, tags, search, sort)

2. **Technology Stack**:
   - ✅ Python 3.13+
   - ✅ argparse (standard library)
   - ✅ In-memory storage (list of dict)
   - ✅ unittest (standard library)
   - ✅ Zero external dependencies

3. **Data Model**:
   - ✅ Required fields: id, title, description, completed, created_at
   - ❌ NO Phase II fields: priority, tags, updated_at, user_id

4. **Architecture**:
   - ✅ Three files: app.py, storage.py, models.py
   - ✅ No over-engineering (no design patterns, DI, abstractions)

5. **Testing**:
   - ✅ 80%+ test coverage
   - ✅ unittest framework only

## Execution Steps

1. **Check dependencies**:
   ```bash
   # Read requirements.txt - should be empty
   cat requirements.txt

   # Check imports in source files
   grep -r "^import\|^from" src/todo/*.py
   ```

2. **Verify data model** in `src/todo/models.py` and `src/todo/storage.py`:
   - Read both files
   - Confirm only Phase I fields present
   - Flag any Phase II fields

3. **Check for over-engineering**:
   - Look for: Abstract classes, dependency injection, factory patterns, repository pattern
   - Flag if found - constitution violation

4. **Verify test coverage**:
   ```bash
   python -m unittest discover tests
   ```
   - Count test functions
   - Estimate coverage (should be 80%+)

5. **Check for Phase II features** in source code:
   - Search for: priority, tag, search, filter, sort, database, auth, user
   - Flag any Phase II implementations

## Output Format

```
Constitution Compliance Report
==============================

Phase: I - Basic CRUD Operations
Date: YYYY-MM-DD

✅ PASS: Zero external dependencies (requirements.txt empty)
✅ PASS: Data model contains only Phase I fields
❌ FAIL: Found priority field in storage.py (Phase II feature)
✅ PASS: No over-engineering patterns detected
✅ PASS: Test coverage 85% (17/20 functions tested)
⚠️  WARN: Found TODO comment mentioning "add search later"

Overall: 4/5 checks passed

Violations:
1. storage.py:45 - Phase II field 'priority' found
2. (warning) app.py:120 - TODO comment references future feature

Recommendations:
- Remove 'priority' field from storage.py
- Update TODO comment to reference Phase II explicitly
```

## Notes

- Run this check before commits
- Run after implementing any new feature
- Run before marking Phase I complete
- Constitution path: `.specify/memory/constitution.md`
