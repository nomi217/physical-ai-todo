"""Unit tests for storage layer."""

import unittest
from src.todo import storage


class TestStorage(unittest.TestCase):
    """Unit tests for CRUD operations."""

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
