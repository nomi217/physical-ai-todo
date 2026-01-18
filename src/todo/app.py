"""CLI interface for Phase I Todo Application.

This module provides the command-line interface using argparse
for all 5 basic CRUD operations.
"""

import argparse
import sys
from . import storage


def format_task(task):
    """Format task for display."""
    status = "[X]" if task["completed"] else "[ ]"
    return f"ID: {task['id']}\n" \
           f"Status: {status}\n" \
           f"Title: {task['title']}\n" \
           f"Description: {task['description']}\n" \
           f"Created: {task['created_at']}"


def format_task_table(tasks):
    """Format tasks as a table."""
    if not tasks:
        return "No tasks yet. Use 'add' to create one."

    lines = []
    lines.append(f"{'ID':<4} {'Status':<8} {'Title':<40} {'Description':<50}")
    lines.append(f"{'──':<4} {'──────':<8} {'────────────────────────────────────────':<40} {'──────────────────────────────────────────────────':<50}")

    for task in tasks:
        status = "[X]" if task["completed"] else "[ ]"
        title = task["title"][:37] + "..." if len(task["title"]) > 40 else task["title"]
        desc = task["description"][:47] + "..." if len(task["description"]) > 50 else task["description"]
        lines.append(f"{task['id']:<4} {status:<8} {title:<40} {desc:<50}")

    return "\n".join(lines)


def cmd_add(args):
    """Handle add command."""
    try:
        description = args.description if args.description else ""
        task = storage.add_task(args.title, description)
        print("Task created successfully!")
        print(format_task(task))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args):
    """Handle list command."""
    tasks = storage.list_tasks()
    print(format_task_table(tasks))
    return 0


def cmd_update(args):
    """Handle update command."""
    if args.title is None and args.description is None:
        print("Error: Must provide at least --title or --description", file=sys.stderr)
        return 1

    try:
        task = storage.update_task(args.id, args.title, args.description)
        print("Task updated successfully!")
        print(format_task(task))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_delete(args):
    """Handle delete command."""
    try:
        task = storage.delete_task(args.id)
        print("Task deleted successfully!")
        print(f"ID: {task['id']}")
        print(f"Title: {task['title']}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_complete(args):
    """Handle complete command."""
    try:
        completed = not args.incomplete
        task = storage.mark_complete(args.id, completed)
        status_text = "complete" if completed else "incomplete"
        status_icon = "[X]" if completed else "[ ]"
        print(f"Task marked as {status_text}!")
        print(f"ID: {task['id']}")
        print(f"Title: {task['title']}")
        print(f"Status: {status_text.capitalize()} {status_icon}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog='todo.app',
        description='Phase I Todo Application - Basic CRUD Operations'
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Add command
    add_parser = subparsers.add_parser('add', help='Create a new task')
    add_parser.add_argument('title', help='Task title (1-200 characters)')
    add_parser.add_argument('--description', '-d', default='',
                           help='Task description (max 2000 characters)')
    add_parser.set_defaults(func=cmd_add)

    # List command
    list_parser = subparsers.add_parser('list', help='Display all tasks')
    list_parser.set_defaults(func=cmd_list)

    # Update command
    update_parser = subparsers.add_parser('update', help='Modify task details')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('--title', '-t', help='New task title')
    update_parser.add_argument('--description', '-d', help='New task description')
    update_parser.set_defaults(func=cmd_update)

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Remove a task')
    delete_parser.add_argument('id', type=int, help='Task ID')
    delete_parser.set_defaults(func=cmd_delete)

    # Complete command
    complete_parser = subparsers.add_parser('complete',
                                           help='Mark task as complete/incomplete')
    complete_parser.add_argument('id', type=int, help='Task ID')
    complete_parser.add_argument('--incomplete', action='store_true',
                                help='Mark as incomplete')
    complete_parser.set_defaults(func=cmd_complete)

    # Parse and execute
    args = parser.parse_args()
    exit_code = args.func(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
