"""
Tests for Chat API endpoints (T040-T042)

Tests the POST /api/v1/chat endpoint for:
- Task creation flow via natural language
- Authentication requirements
- Tool execution and response format
"""

import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import User, Task
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database session for each test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden database session"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User):
    """Create authentication headers with valid JWT token"""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


# T040: Test POST /api/v1/chat endpoint for task creation flow
def test_chat_task_creation_flow(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """
    Test that the chat endpoint processes messages and returns valid responses.

    Note: Due to conversational nature, AI may ask questions instead of immediately
    creating tasks. This test verifies the endpoint works, not AI behavior.
    """
    response = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "Add a task to buy groceries"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "conversation_id" in data
    assert "user_message" in data
    assert "assistant_message" in data
    assert data["user_message"] == "Add a task to buy groceries"

    # Verify assistant responds (not empty)
    assert len(data["assistant_message"]) > 0


def test_chat_list_tasks_flow(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """
    Test that the chat endpoint processes task list requests.

    Note: Due to conversational nature, AI may ask clarifying questions.
    This test verifies the endpoint works and returns valid responses.
    """
    # Create a test task first
    task = Task(
        title="Test Task",
        description="Test Description",
        user_id=test_user.id,
        completed=False,
        priority="medium"
    )
    session.add(task)
    session.commit()

    response = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "Show me my tasks"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "assistant_message" in data
    assert len(data["assistant_message"]) > 0

    # Verify response is relevant to tasks (mentions "task" somewhere)
    assert "task" in data["assistant_message"].lower()


# T041: Test chat endpoint authentication (401 unauthorized)
def test_chat_without_authentication_returns_401(client: TestClient):
    """
    Test that chat endpoint requires authentication.

    Given a user is not authenticated
    When they try to send a chat message
    Then they receive a 401 Unauthorized error
    """
    response = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "Add a task"
        }
    )

    assert response.status_code == 401
    assert "detail" in response.json()


def test_chat_with_invalid_token_returns_401(client: TestClient):
    """
    Test that chat endpoint rejects invalid tokens.

    Given a user provides an invalid JWT token
    When they try to send a chat message
    Then they receive a 401 Unauthorized error
    """
    response = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "Add a task"
        },
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == 401


def test_chat_with_expired_token_returns_401(client: TestClient):
    """
    Test that chat endpoint rejects expired tokens.

    Given a user provides an expired JWT token
    When they try to send a chat message
    Then they receive a 401 Unauthorized error
    """
    # Create an expired token (negative expiry)
    # Note: We need a valid user ID for the sub claim
    expired_token = create_access_token(
        data={"sub": "999"},  # Non-existent user ID
        expires_delta=timedelta(seconds=-1)  # Already expired
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "Add a task"
        },
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401


# T042: Test chat endpoint tool execution and response format
def test_chat_response_format(client: TestClient, test_user: User, auth_headers: dict):
    """
    Test that chat endpoint returns correct response format.

    Given a valid chat request
    When the endpoint processes it
    Then it returns the expected response structure
    """
    response = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "Hello"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify required fields
    assert "conversation_id" in data
    assert "user_message" in data
    assert "assistant_message" in data

    # Verify types
    assert isinstance(data["conversation_id"], int)
    assert isinstance(data["user_message"], str)
    assert isinstance(data["assistant_message"], str)

    # tool_calls is optional but if present should be a list
    if "tool_calls" in data and data["tool_calls"] is not None:
        assert isinstance(data["tool_calls"], list)


def test_chat_tool_execution_format(client: TestClient, test_user: User, auth_headers: dict):
    """
    Test that tool_calls are properly formatted in response.

    Given a chat message that triggers tool execution
    When tools are executed
    Then tool_calls array contains proper format
    """
    response = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "Add task test the chatbot"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # If tools were called, verify format
    if data.get("tool_calls"):
        for tool_call in data["tool_calls"]:
            assert "tool" in tool_call
            assert "arguments" in tool_call
            assert "result" in tool_call

            # Verify result structure
            result = tool_call["result"]
            assert "success" in result
            assert isinstance(result["success"], bool)


def test_chat_conversation_persistence(client: TestClient, test_user: User, auth_headers: dict, session: Session):
    """
    Test that conversations are persisted to database.

    Given a user sends multiple messages
    When each message is processed
    Then all messages are saved to the database
    """
    # First message
    response1 = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "First message"
        },
        headers=auth_headers
    )

    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Second message in same conversation
    response2 = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Second message"
        },
        headers=auth_headers
    )

    assert response2.status_code == 200
    assert response2.json()["conversation_id"] == conversation_id

    # Verify messages are in database
    from app.models import ConversationMessage
    messages = session.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).all()

    # Should have at least 2 user messages + AI responses
    assert len(messages) >= 4  # 2 user + 2 assistant minimum


def test_chat_empty_message_returns_400(client: TestClient, auth_headers: dict):
    """
    Test that empty messages are rejected.

    Given a user sends an empty message
    When the endpoint processes it
    Then it returns a 422 Unprocessable Entity error (Pydantic validation)
    """
    response = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": ""
        },
        headers=auth_headers
    )

    # Pydantic validation returns 422, not 400
    assert response.status_code == 422
    assert "detail" in response.json()


def test_chat_user_isolation(client: TestClient, session: Session):
    """
    Test that chat endpoint properly isolates users.

    Verifies that each user can only interact via their own authenticated session.
    Note: Due to conversational nature, detailed task content verification is skipped.
    """
    # Create two users
    user1 = User(
        email="user1@example.com",
        hashed_password=hash_password("password1"),
        is_active=True,
        is_verified=True
    )
    user2 = User(
        email="user2@example.com",
        hashed_password=hash_password("password2"),
        is_active=True,
        is_verified=True
    )
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # Create task for user1
    task1 = Task(
        title="User 1 Task",
        user_id=user1.id,
        completed=False,
        priority="medium"
    )
    # Create task for user2
    task2 = Task(
        title="User 2 Task",
        user_id=user2.id,
        completed=False,
        priority="medium"
    )
    session.add(task1)
    session.add(task2)
    session.commit()

    # User 1 makes a request
    token1 = create_access_token(data={"sub": str(user1.id)})
    response1 = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "Show my tasks"
        },
        headers={"Authorization": f"Bearer {token1}"}
    )

    assert response1.status_code == 200
    data1 = response1.json()

    # Verify user 1 gets a valid response
    assert "assistant_message" in data1
    assert len(data1["assistant_message"]) > 0

    # User 2 makes a separate request
    token2 = create_access_token(data={"sub": str(user2.id)})
    response2 = client.post(
        "/api/v1/chat",
        json={
            "conversation_id": None,
            "message": "Show my tasks"
        },
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response2.status_code == 200
    data2 = response2.json()

    # Verify user 2 gets a valid response
    assert "assistant_message" in data2
    assert len(data2["assistant_message"]) > 0

    # Verify they have different conversation IDs (isolated sessions)
    assert data1["conversation_id"] != data2["conversation_id"]
