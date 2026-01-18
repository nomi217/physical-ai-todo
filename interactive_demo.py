"""
Interactive Todo App Demo - Phase I
Run this to test all 5 CRUD operations interactively!
Usage: python interactive_demo.py
"""

from src.todo import storage
import sys

def print_header():
    """Print the application header"""
    print("\n" + "=" * 70)
    print("  PHYSICAL AI TODO APP - INTERACTIVE DEMO")
    print("=" * 70)
    print()

def print_menu():
    """Print the main menu"""
    print("\n" + "-" * 70)
    print("  MAIN MENU")
    print("-" * 70)
    print("  1. Add a new task")
    print("  2. List all tasks")
    print("  3. Mark task as complete/incomplete")
    print("  4. Update a task")
    print("  5. Delete a task")
    print("  6. Exit")
    print("-" * 70)

def display_tasks(tasks):
    """Display tasks in a nice format"""
    if not tasks:
        print("\n  No tasks found. Add some tasks to get started!")
        return

    print(f"\n  Total tasks: {len(tasks)}")
    print("  " + "-" * 66)
    for task in tasks:
        status = "[X]" if task['completed'] else "[ ]"
        desc = f"\n      Description: {task['description']}" if task['description'] else ""
        print(f"  {status} [{task['id']}] {task['title']}{desc}")
    print("  " + "-" * 66)

def add_task_interactive():
    """Interactive task addition"""
    print("\n" + "=" * 70)
    print("  ADD NEW TASK")
    print("=" * 70)

    title = input("\n  Enter task title: ").strip()
    if not title:
        print("  [ERROR] Error: Title cannot be empty!")
        return

    description = input("  Enter description (optional, press Enter to skip): ").strip()

    try:
        task = storage.add_task(title, description)
        print(f"\n  [OK] Task created successfully!")
        print(f"  ID: {task['id']}")
        print(f"  Title: {task['title']}")
        if task['description']:
            print(f"  Description: {task['description']}")
    except ValueError as e:
        print(f"  [ERROR] Error: {e}")

def list_tasks_interactive():
    """Interactive task listing"""
    print("\n" + "=" * 70)
    print("  ALL TASKS")
    print("=" * 70)

    tasks = storage.list_tasks()
    display_tasks(tasks)

    if tasks:
        completed = sum(1 for t in tasks if t['completed'])
        print(f"\n  Progress: {completed}/{len(tasks)} completed ({int(completed/len(tasks)*100)}%)")

def mark_complete_interactive():
    """Interactive task completion toggle"""
    print("\n" + "=" * 70)
    print("  MARK TASK AS COMPLETE/INCOMPLETE")
    print("=" * 70)

    # Show current tasks
    tasks = storage.list_tasks()
    if not tasks:
        print("\n  No tasks to mark. Add some tasks first!")
        return

    display_tasks(tasks)

    try:
        task_id = int(input("\n  Enter task ID to toggle completion: "))
        task = storage.get_task(task_id)

        if task:
            new_status = not task['completed']
            storage.mark_complete(task_id, new_status)
            status_text = "complete" if new_status else "incomplete"
            print(f"\n  [OK] Task [{task_id}] marked as {status_text}!")
        else:
            print(f"\n  [ERROR] Error: Task with ID {task_id} not found!")
    except ValueError:
        print("\n  [ERROR] Error: Please enter a valid task ID (number)!")

def update_task_interactive():
    """Interactive task update"""
    print("\n" + "=" * 70)
    print("  UPDATE TASK")
    print("=" * 70)

    # Show current tasks
    tasks = storage.list_tasks()
    if not tasks:
        print("\n  No tasks to update. Add some tasks first!")
        return

    display_tasks(tasks)

    try:
        task_id = int(input("\n  Enter task ID to update: "))
        task = storage.get_task(task_id)

        if not task:
            print(f"\n  [ERROR] Error: Task with ID {task_id} not found!")
            return

        print(f"\n  Current task:")
        print(f"    Title: {task['title']}")
        print(f"    Description: {task['description']}")

        print("\n  Enter new values (press Enter to keep current value):")
        new_title = input(f"  New title [{task['title']}]: ").strip()
        new_desc = input(f"  New description [{task['description']}]: ").strip()

        # Use current values if input is empty
        final_title = new_title if new_title else task['title']
        final_desc = new_desc if new_desc else task['description']

        updated_task = storage.update_task(task_id, title=final_title, description=final_desc)
        print(f"\n  [OK] Task updated successfully!")
        print(f"  Title: {updated_task['title']}")
        print(f"  Description: {updated_task['description']}")

    except ValueError as e:
        if "not found" in str(e):
            print(f"\n  [ERROR] Error: Task not found!")
        elif "Task ID must be a number" in str(e):
            print("\n  [ERROR] Error: Please enter a valid task ID (number)!")
        else:
            print(f"\n  [ERROR] Error: {e}")

def delete_task_interactive():
    """Interactive task deletion"""
    print("\n" + "=" * 70)
    print("  DELETE TASK")
    print("=" * 70)

    # Show current tasks
    tasks = storage.list_tasks()
    if not tasks:
        print("\n  No tasks to delete. Add some tasks first!")
        return

    display_tasks(tasks)

    try:
        task_id = int(input("\n  Enter task ID to delete: "))
        task = storage.get_task(task_id)

        if not task:
            print(f"\n  [ERROR] Error: Task with ID {task_id} not found!")
            return

        # Confirm deletion
        confirm = input(f"\n  Are you sure you want to delete '{task['title']}'? (yes/no): ").strip().lower()

        if confirm in ['yes', 'y']:
            deleted_task = storage.delete_task(task_id)
            print(f"\n  [OK] Task deleted successfully!")
            print(f"  Deleted: [{deleted_task['id']}] {deleted_task['title']}")
        else:
            print("\n  [ERROR] Deletion cancelled.")

    except ValueError:
        print("\n  [ERROR] Error: Please enter a valid task ID (number)!")

def main():
    """Main interactive loop"""
    print_header()
    print("  Welcome to the Interactive Todo App Demo!")
    print("  You can test all 5 CRUD operations in this session.")
    print("  Data persists within this session (in-memory storage).")

    while True:
        print_menu()
        choice = input("\n  Enter your choice (1-6): ").strip()

        if choice == '1':
            add_task_interactive()
        elif choice == '2':
            list_tasks_interactive()
        elif choice == '3':
            mark_complete_interactive()
        elif choice == '4':
            update_task_interactive()
        elif choice == '5':
            delete_task_interactive()
        elif choice == '6':
            print("\n" + "=" * 70)
            print("  Thank you for using the Todo App!")
            print("  Phase I Demo Complete!")
            print("=" * 70)
            print()
            sys.exit(0)
        else:
            print("\n  [ERROR] Invalid choice! Please enter a number between 1 and 6.")

        # Pause before showing menu again
        input("\n  Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("  Demo interrupted. Goodbye!")
        print("=" * 70)
        print()
        sys.exit(0)
