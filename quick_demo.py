"""
Quick Demo - Run this to test the todo app!
Usage: python quick_demo.py
"""

from src.todo import storage

print("=" * 70)
print("  PHYSICAL AI TODO APP - QUICK DEMO")
print("=" * 70)
print()

# Step 1: Add tasks
print("STEP 1: Adding 5 tasks...")
print("-" * 70)
tasks_to_add = [
    ("Buy groceries", "Milk, eggs, bread, coffee"),
    ("Call mom", "Discuss weekend plans"),
    ("Write report", "Q4 financial summary"),
    ("Book dentist appointment", ""),
    ("Exercise", "30 min morning jog")
]

for i, (title, desc) in enumerate(tasks_to_add, 1):
    task = storage.add_task(title, desc)
    desc_text = f" - {desc}" if desc else ""
    print(f"  {i}. Created: [{task['id']}] {title}{desc_text}")
print()

# Step 2: List all tasks
print("STEP 2: Listing all tasks...")
print("-" * 70)
tasks = storage.list_tasks()
print(f"Total tasks: {len(tasks)}\n")
for task in tasks:
    status = "[X]" if task['completed'] else "[ ]"
    desc = f" - {task['description']}" if task['description'] else ""
    print(f"  {status} [{task['id']}] {task['title']}{desc}")
print()

# Step 3: Mark some complete
print("STEP 3: Marking tasks 1 and 3 as complete...")
print("-" * 70)
storage.mark_complete(1, True)
print("  [OK] Task 1 completed")
storage.mark_complete(3, True)
print("  [OK] Task 3 completed")
print()

# Step 4: Show updated list
print("STEP 4: Updated task list...")
print("-" * 70)
tasks = storage.list_tasks()
completed = sum(1 for t in tasks if t['completed'])
print(f"Progress: {completed}/{len(tasks)} tasks completed\n")
for task in tasks:
    status = "[X]" if task['completed'] else "[ ]"
    print(f"  {status} [{task['id']}] {task['title']}")
print()

# Step 5: Update a task
print("STEP 5: Updating task 4...")
print("-" * 70)
old_task = storage.get_task(4)
print(f"  Before: {old_task['title']}")
updated = storage.update_task(4, title="Complete Q4 Report", 
                              description="Financial summary with charts")
print(f"  After:  {updated['title']}")
print(f"  Desc:   {updated['description']}")
print()

# Step 6: Delete a task
print("STEP 6: Deleting task 5...")
print("-" * 70)
deleted = storage.delete_task(5)
print(f"  [DELETED] [{deleted['id']}] {deleted['title']}")
print()

# Step 7: Final state
print("STEP 7: Final task list...")
print("-" * 70)
tasks = storage.list_tasks()
print(f"Remaining tasks: {len(tasks)}\n")
for task in tasks:
    status = "[X]" if task['completed'] else "[ ]"
    desc = f" - {task['description']}" if task['description'] else ""
    print(f"  {status} [{task['id']}] {task['title']}{desc}")
print()

# Step 8: Test ID preservation
print("STEP 8: Testing ID preservation (gaps after deletion)...")
print("-" * 70)
new_task = storage.add_task("New task after deletion", "This should be ID 6, not 5!")
print(f"  [NEW] Task ID: {new_task['id']}")
print(f"  Expected: 6 (not 5, because 5 was deleted)")
print(f"  Result: {'PASS' if new_task['id'] == 6 else 'FAIL'}")
print()

# Summary
print("=" * 70)
print("  DEMO COMPLETE!")
print("=" * 70)
print()
print("Summary:")
print("  - Created 5 tasks")
print("  - Marked 2 complete")
print("  - Updated 1 task")
print("  - Deleted 1 task")
print("  - Verified ID preservation")
print()
final_tasks = storage.list_tasks()
completed = sum(1 for t in final_tasks if t['completed'])
print(f"Final State: {len(final_tasks)} tasks, {completed} completed")
print()
print("Try it yourself:")
print("  1. Open Python: python")
print("  2. Run: from src.todo import storage")
print("  3. Try: storage.add_task('My task', 'My description')")
print("  4. See: storage.list_tasks()")
print()
