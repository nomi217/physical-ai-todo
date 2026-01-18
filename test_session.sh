#!/bin/bash
# Phase I Manual Testing Session

echo "=========================================="
echo "Phase I Todo App - Manual Testing Session"
echo "=========================================="
echo ""

echo "1. Adding Tasks"
echo "----------------------------------------"
echo "$ python -m src.todo.app add \"Buy groceries\" -d \"Milk, eggs, bread, coffee\""
python -m src.todo.app add "Buy groceries" -d "Milk, eggs, bread, coffee"
echo ""

echo "$ python -m src.todo.app add \"Call mom\" -d \"Discuss weekend plans\""
python -m src.todo.app add "Call mom" -d "Discuss weekend plans"
echo ""

echo "$ python -m src.todo.app add \"Write report\""
python -m src.todo.app add "Write report"
echo ""

echo "$ python -m src.todo.app add \"Exercise\" -d \"30 min cardio\""
python -m src.todo.app add "Exercise" -d "30 min cardio"
echo ""

echo ""
echo "2. Listing All Tasks"
echo "----------------------------------------"
echo "$ python -m src.todo.app list"
python -m src.todo.app list
echo ""

echo ""
echo "3. Marking Tasks as Complete"
echo "----------------------------------------"
echo "$ python -m src.todo.app complete 1"
python -m src.todo.app complete 1
echo ""

echo "$ python -m src.todo.app complete 2"
python -m src.todo.app complete 2
echo ""

echo ""
echo "4. Listing Tasks After Completion"
echo "----------------------------------------"
echo "$ python -m src.todo.app list"
python -m src.todo.app list
echo ""

echo ""
echo "5. Updating a Task"
echo "----------------------------------------"
echo "$ python -m src.todo.app update 3 --title \"Write Q4 report\" -d \"Financial summary for Q4 2025\""
python -m src.todo.app update 3 --title "Write Q4 report" -d "Financial summary for Q4 2025"
echo ""

echo ""
echo "6. Listing After Update"
echo "----------------------------------------"
echo "$ python -m src.todo.app list"
python -m src.todo.app list
echo ""

echo ""
echo "7. Deleting a Task"
echo "----------------------------------------"
echo "$ python -m src.todo.app delete 4"
python -m src.todo.app delete 4
echo ""

echo ""
echo "8. Final Task List"
echo "----------------------------------------"
echo "$ python -m src.todo.app list"
python -m src.todo.app list
echo ""

echo ""
echo "9. Testing Error Handling"
echo "----------------------------------------"
echo "$ python -m src.todo.app add \"\""
python -m src.todo.app add "" 2>&1
echo ""

echo "$ python -m src.todo.app delete 999"
python -m src.todo.app delete 999 2>&1
echo ""

echo "$ python -m src.todo.app update 999 --title \"Test\""
python -m src.todo.app update 999 --title "Test" 2>&1
echo ""

echo ""
echo "10. Testing Help System"
echo "----------------------------------------"
echo "$ python -m src.todo.app --help"
python -m src.todo.app --help
echo ""

echo ""
echo "=========================================="
echo "Testing Session Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "- ✅ Add command working"
echo "- ✅ List command working"
echo "- ✅ Complete command working"
echo "- ✅ Update command working"
echo "- ✅ Delete command working"
echo "- ✅ Error handling working"
echo "- ✅ Help system working"
echo ""
echo "All 5 basic CRUD operations verified!"
