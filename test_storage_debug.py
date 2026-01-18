"""Quick test to verify storage is working correctly"""
from src.todo import storage

# Reset storage to start fresh
storage.reset_storage()

# Add first task
print("Adding first task...")
task1 = storage.add_task("First Task", "First description")
print(f"  Added: [{task1['id']}] {task1['title']}")

# Add second task
print("\nAdding second task...")
task2 = storage.add_task("Second Task", "Second description")
print(f"  Added: [{task2['id']}] {task2['title']}")

# List all tasks
print("\n" + "=" * 60)
print("Listing all tasks:")
print("=" * 60)
tasks = storage.list_tasks()
print(f"Total tasks in storage: {len(tasks)}")
print()

for task in tasks:
    print(f"  [{task['id']}] {task['title']}")
    if task['description']:
        print(f"      Description: {task['description']}")
    print(f"      Completed: {task['completed']}")
    print()

print("=" * 60)
print(f"Test result: {'PASS' if len(tasks) == 2 else 'FAIL'}")
print(f"Expected 2 tasks, got {len(tasks)}")
