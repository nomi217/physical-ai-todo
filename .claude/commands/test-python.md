# Python Test Runner & Coverage

Run Python unittest suite with coverage analysis and smart failure diagnosis.

## What This Skill Does

1. Runs all tests in the `tests/` directory
2. Analyzes coverage (target: 80%+)
3. Diagnoses test failures
4. Suggests fixes for common issues
5. Reports constitution compliance (80%+ coverage requirement)

## Execution Steps

### 1. Run All Tests

```bash
python -m unittest discover tests -v
```

Capture output and analyze:
- Total tests run
- Passed vs failed
- Error messages
- Execution time

### 2. Analyze Coverage

Manual coverage check (no external tools in Phase I):
- List all functions in `src/todo/*.py`
- Check which have corresponding tests
- Calculate coverage percentage

```bash
# Count functions in source
grep -c "^def " src/todo/*.py

# Count test functions
grep -c "def test_" tests/*.py
```

### 3. Diagnose Failures

For each failed test:
- Read the test code
- Read the implementation
- Identify the issue:
  - Logic error
  - Missing validation
  - Incorrect assertion
  - Test data problem

### 4. Suggest Fixes

Provide specific fixes:
```python
# Example fix suggestion
# File: src/todo/storage.py:42
# Issue: Missing validation before update
# Fix: Add validation call before modifying task

# Before:
task["title"] = title

# After:
error = models.validate_title(title)
if error:
    raise ValueError(error)
task["title"] = title
```

## Output Format

```
Python Test Report
==================

Tests Run: 25
Passed: 23 ✅
Failed: 2 ❌
Skipped: 0

Execution Time: 0.42s

Coverage Analysis:
------------------
Total functions: 20
Tested functions: 17
Coverage: 85% ✅ (Target: 80%)

Untested functions:
- src/todo/models.py:validate_task_id (line 45)
- src/todo/storage.py:_internal_helper (line 89)
- src/todo/app.py:format_timestamp (line 156)

Failed Tests:
-------------

1. test_update_task_validation (tests/test_storage.py:87)
   Error: ValueError not raised for empty title

   Issue: Missing validation in update_task()
   Location: src/todo/storage.py:42

   Fix:
   error = models.validate_title(title)
   if error:
       raise ValueError(error)

2. test_list_command_formatting (tests/test_cli.py:123)
   Error: AssertionError: '[✓]' not found in output

   Issue: Wrong status icon character
   Location: src/todo/app.py:67

   Fix: Change '[x]' to '[✓]'

Recommendations:
----------------
1. Add tests for 3 untested functions to reach 100% coverage
2. Fix 2 failing tests
3. Consider edge case: What happens with very long descriptions?

Constitution: ✅ PASS (85% > 80% requirement)
```

## Quick Commands

After reviewing the report, you can:
- `/fix` - Apply suggested fixes automatically
- `/add-test` - Generate missing test cases
- `/check-constitution` - Verify Phase I compliance
