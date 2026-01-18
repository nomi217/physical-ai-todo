# Fix Common Issues

Diagnose and fix common Python development issues quickly.

## What This Skill Does

Identifies and fixes frequent issues in Python projects:
- Import errors
- Test failures
- Validation bugs
- CLI argument parsing
- Path issues

## Usage

```
/fix-common [category]
```

Categories:
- **imports** - Fix ModuleNotFoundError, import issues
- **tests** - Fix test failures, assertion errors
- **validation** - Fix validation logic bugs
- **cli** - Fix argparse issues
- **auto** - Auto-detect and fix (default)

## Common Issues & Fixes

### 1. ModuleNotFoundError

**Symptom**:
```
ModuleNotFoundError: No module named 'todo'
```

**Diagnosis**:
- Check if running from correct directory
- Check if `__init__.py` files exist
- Check if using `-m` flag

**Fix**:
```bash
# Ensure __init__.py files exist
touch src/todo/__init__.py
touch tests/__init__.py

# Run from project root with -m flag
cd /path/to/project
python -m todo.app list
```

### 2. Test Import Errors

**Symptom**:
```
ImportError: cannot import name 'storage' from 'todo'
```

**Diagnosis**:
- Check import paths in test files
- Verify relative vs absolute imports

**Fix**:
```python
# In tests/test_storage.py
# Wrong:
from todo import storage

# Right:
from src.todo import storage
```

### 3. Validation Not Raising ValueError

**Symptom**:
```
AssertionError: ValueError not raised
```

**Diagnosis**:
- Check if validation function is called
- Check if errors are raised vs returned

**Fix**:
```python
# In storage.py
# Wrong:
errors = models.validate_task_data(title, description)
# Continues even if errors exist

# Right:
errors = models.validate_task_data(title, description)
if errors:
    raise ValueError("; ".join(errors))
```

### 4. CLI Subprocess Tests Failing

**Symptom**:
```
AssertionError: 0 != 1 (exit code mismatch)
```

**Diagnosis**:
- Check if storage.reset_storage() called in setUp
- Check if tests are isolated
- Check subprocess command syntax

**Fix**:
```python
# In tests/test_cli.py
class TestCLI(unittest.TestCase):
    def setUp(self):
        """Reset storage before each test."""
        storage.reset_storage()  # CRITICAL!

    def run_cli(self, *args):
        result = subprocess.run(
            [sys.executable, '-m', 'todo.app'] + list(args),
            capture_output=True,
            text=True
        )
        return result
```

### 5. Unicode/Encoding Issues

**Symptom**:
```
UnicodeDecodeError: 'charmap' codec can't decode byte
```

**Diagnosis**:
- Windows console encoding issues
- Missing UTF-8 encoding specification

**Fix**:
```python
# In subprocess calls, add encoding
result = subprocess.run(
    [...],
    capture_output=True,
    text=True,
    encoding='utf-8'  # Add this
)
```

### 6. Empty requirements.txt Concerns

**Symptom**:
Developer worried about empty requirements.txt

**Diagnosis**:
- This is CORRECT for Phase I (constitution requirement)
- Phase I uses only standard library

**Fix**:
```txt
# requirements.txt
# Phase I: No external dependencies (standard library only)
# argparse, unittest, datetime are built-in

# Phase II will add:
# sqlmodel
# fastapi
# psycopg2-binary
# etc.
```

### 7. ID Reuse After Deletion

**Symptom**:
```
AssertionError: expected ID 3, got 2
```

**Diagnosis**:
- ID counter being reset
- Using max(ids) instead of counter

**Fix**:
```python
# Wrong:
_next_id = max([t["id"] for t in _tasks], default=0) + 1

# Right:
_next_id = 1  # Module level, never resets
def add_task(...):
    global _next_id
    task = {"id": _next_id, ...}
    _next_id += 1  # Always increment, never reuse
```

### 8. Argparse Not Capturing Description

**Symptom**:
Description is always empty string

**Diagnosis**:
- Check if `args.description` might be None
- Check default value handling

**Fix**:
```python
# In app.py cmd_add
# Wrong:
task = storage.add_task(args.title, args.description)

# Right (handle None):
description = args.description if args.description else ""
task = storage.add_task(args.title, description)

# Or set default in argparse:
add_parser.add_argument('--description', '-d', default='')
```

## Execution Steps

1. **Auto-detect issue**:
   - Run tests: `python -m unittest discover tests`
   - Capture error output
   - Parse error type and message

2. **Classify issue**:
   - ModuleNotFoundError → imports
   - AssertionError → tests
   - ValueError not raised → validation
   - Exit code mismatch → cli
   - UnicodeError → encoding

3. **Read relevant files**:
   - For imports: Check __init__.py, import statements
   - For tests: Read failing test function
   - For validation: Read models.py, storage.py
   - For CLI: Read app.py, test_cli.py

4. **Apply fix**:
   - Generate exact code change
   - Show before/after
   - Explain why fix works

5. **Verify fix**:
   - Re-run tests
   - Confirm issue resolved

## Output Format

```
Common Issue Detected: ModuleNotFoundError
==========================================

Error:
  ModuleNotFoundError: No module named 'todo'
  File: tests/test_storage.py, line 3

Diagnosis:
  Missing __init__.py file in src/todo/ directory

Fix:
  Create src/todo/__init__.py

  $ touch src/todo/__init__.py

Explanation:
  Python requires __init__.py to treat directories as packages.
  Without it, imports like "from todo import storage" fail.

Verification:
  $ python -m unittest tests.test_storage
  ✅ All tests passing

Status: FIXED ✅
```

## Related Commands

- `/test-python` - Run tests after fixing
- `/check-constitution` - Verify fix maintains compliance
- `/gen-cli-test` - Add tests for fixed functionality
