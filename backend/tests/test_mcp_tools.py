"""
Test MCP Tools for Phase III AI Chatbot

Tests individual MCP tool functions to ensure they work correctly
with the database and return proper responses.
"""

import pytest
from sqlmodel import Session, create_engine, select
from sqlalchemy.pool import StaticPool

from app.models import User, Task
from app.mcp.schemas import (
    AddTaskSchema,
    ListTasksSchema,
    CompleteTaskSchema,
    DeleteTaskSchema,
    UpdateTaskSchema
)
from app.mcp.tools import (
    add_task,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Create a test user
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
            is_active=True,
            is_verified=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        yield session


class TestMCPTools:
    """Test all MCP tool functions."""

    def test_add_task_success(self, session: Session):
        """Test add_task tool creates task successfully."""
        user = session.execute(select(User)).scalar_one()

        params = AddTaskSchema(
            user_id=user.id,
            title="Buy groceries",
            description="Milk, eggs, bread",
            priority="high"
        )

        result = add_task(params, session)

        assert result["success"] is True
        assert "task_id" in result
        assert result["title"] == "Buy groceries"
        assert result["priority"] == "high"
        assert "created successfully" in result["message"]

        # Verify task was actually created in database
        task = session.execute(
            select(Task).where(Task.id == result["task_id"])
        ).scalar_one()
        assert task.title == "Buy groceries"
        assert task.user_id == user.id

    def test_add_task_minimal(self, session: Session):
        """Test add_task with only required fields."""
        user = session.execute(select(User)).scalar_one()

        params = AddTaskSchema(
            user_id=user.id,
            title="Simple task"
        )

        result = add_task(params, session)

        assert result["success"] is True
        assert result["title"] == "Simple task"
        assert result["priority"] == "medium"  # Default priority
        assert result["description"] == ""  # Empty description

    def test_list_tasks_all(self, session: Session):
        """Test list_tasks tool returns all tasks."""
        user = session.execute(select(User)).scalar_one()

        # Create some tasks
        for i in range(3):
            add_task(
                AddTaskSchema(user_id=user.id, title=f"Task {i}"),
                session
            )

        params = ListTasksSchema(user_id=user.id, status="all")
        result = list_tasks_tool(params, session)

        assert result["success"] is True
        assert result["count"] == 3
        assert len(result["tasks"]) == 3

    def test_list_tasks_pending_only(self, session: Session):
        """Test list_tasks filters pending tasks."""
        user = session.execute(select(User)).scalar_one()

        # Create tasks
        task1 = add_task(AddTaskSchema(user_id=user.id, title="Task 1"), session)
        task2 = add_task(AddTaskSchema(user_id=user.id, title="Task 2"), session)

        # Complete one task
        complete_task_tool(
            CompleteTaskSchema(user_id=user.id, task_id=task1["task_id"]),
            session
        )

        # List pending tasks
        params = ListTasksSchema(user_id=user.id, status="pending")
        result = list_tasks_tool(params, session)

        assert result["success"] is True
        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "Task 2"

    def test_list_tasks_completed_only(self, session: Session):
        """Test list_tasks filters completed tasks."""
        user = session.execute(select(User)).scalar_one()

        # Create and complete a task
        task = add_task(AddTaskSchema(user_id=user.id, title="Task 1"), session)
        complete_task_tool(
            CompleteTaskSchema(user_id=user.id, task_id=task["task_id"]),
            session
        )

        # List completed tasks
        params = ListTasksSchema(user_id=user.id, status="completed")
        result = list_tasks_tool(params, session)

        assert result["success"] is True
        assert result["count"] == 1
        assert result["tasks"][0]["completed"] is True

    def test_complete_task_success(self, session: Session):
        """Test complete_task tool marks task as complete."""
        user = session.execute(select(User)).scalar_one()

        # Create a task
        task = add_task(AddTaskSchema(user_id=user.id, title="Task 1"), session)

        # Complete it
        params = CompleteTaskSchema(user_id=user.id, task_id=task["task_id"])
        result = complete_task_tool(params, session)

        assert result["success"] is True
        assert result["completed"] is True
        assert "marked as complete" in result["message"]

    def test_complete_task_not_found(self, session: Session):
        """Test complete_task with non-existent task."""
        user = session.execute(select(User)).scalar_one()

        params = CompleteTaskSchema(user_id=user.id, task_id=9999)
        result = complete_task_tool(params, session)

        assert result["success"] is False
        assert "not found" in result["message"]

    def test_delete_task_success(self, session: Session):
        """Test delete_task tool removes task."""
        user = session.execute(select(User)).scalar_one()

        # Create a task
        task = add_task(AddTaskSchema(user_id=user.id, title="Task to delete"), session)

        # Delete it
        params = DeleteTaskSchema(user_id=user.id, task_id=task["task_id"])
        result = delete_task_tool(params, session)

        assert result["success"] is True
        assert "deleted successfully" in result["message"]

        # Verify task is gone
        deleted_task = session.execute(
            select(Task).where(Task.id == task["task_id"])
        ).scalar_one_or_none()
        assert deleted_task is None

    def test_delete_task_not_found(self, session: Session):
        """Test delete_task with non-existent task."""
        user = session.execute(select(User)).scalar_one()

        params = DeleteTaskSchema(user_id=user.id, task_id=9999)
        result = delete_task_tool(params, session)

        assert result["success"] is False
        assert "not found" in result["message"]

    def test_update_task_title(self, session: Session):
        """Test update_task tool updates title."""
        user = session.execute(select(User)).scalar_one()

        # Create a task
        task = add_task(AddTaskSchema(user_id=user.id, title="Old title"), session)

        # Update title
        params = UpdateTaskSchema(
            user_id=user.id,
            task_id=task["task_id"],
            title="New title"
        )
        result = update_task_tool(params, session)

        assert result["success"] is True
        assert result["title"] == "New title"
        assert "updated successfully" in result["message"]

    def test_update_task_priority(self, session: Session):
        """Test update_task tool updates priority."""
        user = session.execute(select(User)).scalar_one()

        # Create a task
        task = add_task(AddTaskSchema(user_id=user.id, title="Task"), session)

        # Update priority
        params = UpdateTaskSchema(
            user_id=user.id,
            task_id=task["task_id"],
            priority="high"
        )
        result = update_task_tool(params, session)

        assert result["success"] is True
        assert result["priority"] == "high"

    def test_update_task_multiple_fields(self, session: Session):
        """Test update_task tool updates multiple fields."""
        user = session.execute(select(User)).scalar_one()

        # Create a task
        task = add_task(AddTaskSchema(user_id=user.id, title="Task"), session)

        # Update multiple fields
        params = UpdateTaskSchema(
            user_id=user.id,
            task_id=task["task_id"],
            title="Updated task",
            description="New description",
            priority="low"
        )
        result = update_task_tool(params, session)

        assert result["success"] is True
        assert result["title"] == "Updated task"
        assert result["description"] == "New description"
        assert result["priority"] == "low"

    def test_update_task_not_found(self, session: Session):
        """Test update_task with non-existent task."""
        user = session.execute(select(User)).scalar_one()

        params = UpdateTaskSchema(
            user_id=user.id,
            task_id=9999,
            title="New title"
        )
        result = update_task_tool(params, session)

        assert result["success"] is False
        assert "not found" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
