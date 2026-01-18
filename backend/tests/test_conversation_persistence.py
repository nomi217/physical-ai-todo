"""
Test conversation persistence functionality for Phase III AI Chatbot.

Tests the ConversationMessage model and CRUD operations to ensure:
- Messages can be created and stored in database
- Conversation history can be retrieved with sliding window
- Multiple conversations can be managed per user
- Data persists across sessions (stateless architecture)
"""

import pytest
from sqlmodel import Session, create_engine, select
from sqlalchemy.pool import StaticPool
from datetime import datetime

from app.models import ConversationMessage, User
from app.crud import (
    create_conversation_message,
    get_conversation_history,
    get_user_conversations
)


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
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


class TestConversationPersistence:
    """Test conversation message persistence and retrieval."""

    def test_create_conversation_message(self, session: Session):
        """Test creating a single conversation message."""
        # Get test user
        user = session.execute(select(User)).scalar_one()

        # Create a message
        message = create_conversation_message(
            db=session,
            conversation_id=1,
            user_id=user.id,
            role="user",
            content="Hello, I need help with my tasks",
            tool_calls=None
        )

        assert message.id is not None
        assert message.conversation_id == 1
        assert message.user_id == user.id
        assert message.role == "user"
        assert message.content == "Hello, I need help with my tasks"
        assert message.tool_calls is None
        assert isinstance(message.created_at, datetime)

    def test_create_assistant_message_with_tool_calls(self, session: Session):
        """Test creating an assistant message with tool calls."""
        user = session.execute(select(User)).scalar_one()

        tool_calls_data = {
            "tool": "add_task",
            "parameters": {"title": "Buy groceries", "description": "Milk, eggs, bread"}
        }

        message = create_conversation_message(
            db=session,
            conversation_id=1,
            user_id=user.id,
            role="assistant",
            content="I've added the task 'Buy groceries' to your list.",
            tool_calls=tool_calls_data
        )

        assert message.role == "assistant"
        assert message.tool_calls == tool_calls_data
        assert "add_task" in str(message.tool_calls)

    def test_get_conversation_history(self, session: Session):
        """Test retrieving conversation history in chronological order."""
        user = session.execute(select(User)).scalar_one()
        conversation_id = 1

        # Create multiple messages
        messages_content = [
            ("user", "Show me my tasks"),
            ("assistant", "Here are your tasks: ..."),
            ("user", "Add a new task"),
            ("assistant", "What task would you like to add?"),
            ("user", "Buy groceries")
        ]

        for role, content in messages_content:
            create_conversation_message(
                db=session,
                conversation_id=conversation_id,
                user_id=user.id,
                role=role,
                content=content
            )

        # Retrieve history
        history = get_conversation_history(session, conversation_id, limit=10)

        assert len(history) == 5
        # Verify chronological order (oldest first)
        assert history[0].content == "Show me my tasks"
        assert history[1].content == "Here are your tasks: ..."
        assert history[4].content == "Buy groceries"

    def test_conversation_history_sliding_window(self, session: Session):
        """Test sliding window returns only last N messages."""
        user = session.execute(select(User)).scalar_one()
        conversation_id = 1

        # Create 25 messages
        for i in range(25):
            create_conversation_message(
                db=session,
                conversation_id=conversation_id,
                user_id=user.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}"
            )

        # Get last 20 messages
        history = get_conversation_history(session, conversation_id, limit=20)

        assert len(history) == 20
        # Should get messages 5-24 (last 20)
        assert history[0].content == "Message 5"
        assert history[-1].content == "Message 24"

    def test_multiple_conversations(self, session: Session):
        """Test managing multiple separate conversations."""
        user = session.execute(select(User)).scalar_one()

        # Create messages in conversation 1
        create_conversation_message(
            session, 1, user.id, "user", "Conversation 1 message"
        )

        # Create messages in conversation 2
        create_conversation_message(
            session, 2, user.id, "user", "Conversation 2 message"
        )

        # Retrieve each conversation separately
        conv1_history = get_conversation_history(session, 1)
        conv2_history = get_conversation_history(session, 2)

        assert len(conv1_history) == 1
        assert len(conv2_history) == 1
        assert conv1_history[0].content == "Conversation 1 message"
        assert conv2_history[0].content == "Conversation 2 message"

    def test_get_user_conversations(self, session: Session):
        """Test retrieving list of user's conversations with metadata."""
        user = session.execute(select(User)).scalar_one()

        # Create multiple conversations
        for conv_id in [1, 2, 3]:
            for i in range(5):
                create_conversation_message(
                    session, conv_id, user.id, "user", f"Message {i}"
                )

        # Get user's conversations
        conversations = get_user_conversations(session, user.id, limit=10)

        assert len(conversations) == 3

        # Verify metadata
        for conv in conversations:
            assert 'conversation_id' in conv
            assert 'message_count' in conv
            assert 'last_message_at' in conv
            assert 'created_at' in conv
            assert conv['message_count'] == 5

    def test_conversation_persistence_across_sessions(self, session: Session):
        """Test that conversations persist (simulating server restart)."""
        user = session.execute(select(User)).scalar_one()

        # Create message
        create_conversation_message(
            session, 1, user.id, "user", "Before restart"
        )

        # Simulate session ending and new session starting
        # (In reality, this would be a new database connection)
        session.commit()

        # Retrieve message in "new session"
        history = get_conversation_history(session, 1)

        assert len(history) == 1
        assert history[0].content == "Before restart"
        # Verify persistence by checking we can still access it

    def test_empty_conversation_history(self, session: Session):
        """Test retrieving history for non-existent conversation."""
        history = get_conversation_history(session, conversation_id=999)
        assert len(history) == 0

    def test_role_validation(self, session: Session):
        """Test that message roles are stored correctly."""
        user = session.execute(select(User)).scalar_one()

        roles = ["user", "assistant", "system"]
        for role in roles:
            msg = create_conversation_message(
                session, 1, user.id, role, f"Test {role} message"
            )
            assert msg.role == role


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
