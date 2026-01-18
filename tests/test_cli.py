"""Integration tests for CLI."""

import unittest
import io
import sys
from unittest.mock import patch
from src.todo import storage
from src.todo import app


class TestCLI(unittest.TestCase):
    """Integration tests for CLI."""

    def setUp(self):
        """Reset storage before each test."""
        storage.reset_storage()

    def test_add_command_success(self):
        """Test add command with valid input."""
        # Create mock args
        args = type('Args', (), {
            'title': 'Test Task',
            'description': 'Test Description'
        })()

        result = app.cmd_add(args)
        self.assertEqual(result, 0)

    def test_add_command_empty_title_fails(self):
        """Test add command with empty title."""
        args = type('Args', (), {
            'title': '',
            'description': ''
        })()

        result = app.cmd_add(args)
        self.assertEqual(result, 1)

    def test_list_command_empty(self):
        """Test list command with no tasks."""
        args = type('Args', (), {})()

        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = app.cmd_list(args)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('No tasks yet', output)

    def test_list_command_with_tasks(self):
        """Test list command with tasks."""
        # Add tasks first
        storage.add_task('Task 1')
        storage.add_task('Task 2')

        args = type('Args', (), {})()

        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = app.cmd_list(args)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('Task 1', output)
        self.assertIn('Task 2', output)

    def test_complete_command_success(self):
        """Test complete command."""
        task = storage.add_task('Task to Complete')

        args = type('Args', (), {
            'id': task['id'],
            'incomplete': False
        })()

        result = app.cmd_complete(args)
        self.assertEqual(result, 0)

    def test_update_command_success(self):
        """Test update command."""
        task = storage.add_task('Original Title')

        args = type('Args', (), {
            'id': task['id'],
            'title': 'New Title',
            'description': None
        })()

        result = app.cmd_update(args)
        self.assertEqual(result, 0)

    def test_delete_command_success(self):
        """Test delete command."""
        task = storage.add_task('Task to Delete')

        args = type('Args', (), {
            'id': task['id']
        })()

        result = app.cmd_delete(args)
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
