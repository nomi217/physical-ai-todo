# CLI Test Generator

Generate unittest test cases for argparse CLI commands.

## What This Skill Does

Automatically generates test boilerplate for CLI commands, saving time and ensuring consistent test coverage.

## Usage

```
/gen-cli-test <command-name> [test-type]
```

**Examples**:
- `/gen-cli-test add` - Generate all tests for 'add' command
- `/gen-cli-test update success` - Generate only success test for 'update'
- `/gen-cli-test complete error` - Generate only error tests for 'complete'

## Test Types

1. **success** - Happy path test
2. **error** - Error condition tests
3. **validation** - Input validation tests
4. **edge** - Edge case tests
5. **all** - All of the above (default)

## Execution Steps

### 1. Read CLI Contract

Read the command specification from:
- `specs/001-phase-1-basics/contracts/cli-commands.md`

Extract:
- Command syntax
- Parameters
- Success output format
- Error conditions
- Examples

### 2. Read Existing Tests

Check `tests/test_cli.py` to see:
- What tests already exist
- Test helper functions available
- Naming conventions

### 3. Generate Test Code

Create test functions following this pattern:

```python
def test_<command>_<scenario>(self):
    """Test <command> command with <scenario>."""
    # Arrange
    <setup code if needed>

    # Act
    result = self.run_cli('<command>', <args>)

    # Assert
    self.assertEqual(result.returncode, <expected>)
    self.assertIn('<expected output>', result.stdout)
```

### 4. Generate Test Cases

Based on CLI contract, generate:

#### Success Tests:
```python
def test_add_command_success(self):
    """Test add command with valid title and description."""
    result = self.run_cli('add', 'Test Task', '-d', 'Test Description')
    self.assertEqual(result.returncode, 0)
    self.assertIn('Task created successfully!', result.stdout)
    self.assertIn('ID: 1', result.stdout)
```

#### Error Tests:
```python
def test_add_command_empty_title_fails(self):
    """Test add command rejects empty title."""
    result = self.run_cli('add', '')
    self.assertEqual(result.returncode, 1)
    self.assertIn('Error: Title is required', result.stderr)

def test_add_command_long_title_fails(self):
    """Test add command rejects title over 200 chars."""
    long_title = 'a' * 201
    result = self.run_cli('add', long_title)
    self.assertEqual(result.returncode, 1)
    self.assertIn('Title must be 200 characters or less', result.stderr)
```

#### Edge Case Tests:
```python
def test_add_command_unicode_title(self):
    """Test add command handles unicode characters."""
    result = self.run_cli('add', '🎯 Buy groceries 日本語')
    self.assertEqual(result.returncode, 0)
    self.assertIn('Task created successfully!', result.stdout)

def test_add_command_special_characters(self):
    """Test add command handles special characters."""
    result = self.run_cli('add', "Task with 'quotes' and \"double quotes\"")
    self.assertEqual(result.returncode, 0)
```

### 5. Output Generated Code

Display the generated test code with:
- File location: `tests/test_cli.py`
- Insert location (after existing tests)
- Instructions to run tests

## Output Format

```python
# =============================================================================
# Generated CLI Tests for: add command
# Location: tests/test_cli.py
# Insert after: test_delete_command_success (line 85)
# =============================================================================

def test_add_command_success(self):
    """Test add command with valid title and description."""
    result = self.run_cli('add', 'Test Task', '-d', 'Test Description')
    self.assertEqual(result.returncode, 0)
    self.assertIn('Task created successfully!', result.stdout)
    self.assertIn('ID: 1', result.stdout)

def test_add_command_empty_title_fails(self):
    """Test add command rejects empty title."""
    result = self.run_cli('add', '')
    self.assertEqual(result.returncode, 1)
    self.assertIn('Error: Title is required', result.stderr)

# ... (more tests)

# =============================================================================
# To add these tests:
# 1. Open tests/test_cli.py
# 2. Insert code above after test_delete_command_success
# 3. Run: python -m unittest tests.test_cli
# =============================================================================
```

## Notes

- Tests follow unittest conventions
- Uses subprocess for true integration testing
- Checks both stdout and stderr
- Verifies exit codes
- Includes docstrings
- Ready to copy-paste into test file

## Related Commands

- `/test-python` - Run all tests after adding new ones
- `/check-constitution` - Verify coverage still meets 80%+
