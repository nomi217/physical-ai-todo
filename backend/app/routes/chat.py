"""
Chat API Routes for Phase III AI Chatbot

Provides endpoints for:
- POST /chat - Send message and get AI response
- GET /conversations - List user's conversations

Stateless architecture: all state in database, no server-side memory.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlmodel import Session

from app.database import get_session
from app.auth.dependencies import get_current_user
from app.models import User
from app.crud import create_conversation_message, get_user_conversations
from app.chat.agent import ChatAgent
from app.chat.conversation import load_conversation_context, generate_conversation_id


router = APIRouter(prefix="/chat", tags=["chat"])


# Request/Response Schemas
class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    conversation_id: Optional[int] = Field(
        default=None,
        description="Conversation ID (null for new conversation)"
    )
    message: str = Field(
        min_length=1,
        max_length=10000,
        description="User's message"
    )


class ChatResponse(BaseModel):
    """Response schema for chat endpoint"""
    conversation_id: int = Field(description="Conversation ID")
    user_message: str = Field(description="User's message")
    assistant_message: str = Field(description="AI assistant's response")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Tool calls made by the assistant"
    )


class ConversationListResponse(BaseModel):
    """Response schema for conversations list"""
    conversations: List[Dict[str, Any]]


# Chat Agent Instance (singleton)
chat_agent = ChatAgent()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Process a chat message and return AI response.

    Stateless conversation flow:
    1. Load conversation history from database (if conversation exists)
    2. Save user message to database
    3. Call AI agent with history + user message + MCP tools
    4. Save assistant response to database
    5. Return response

    Args:
        request: ChatRequest with conversation_id and message
        current_user: Authenticated user
        db: Database session

    Returns:
        ChatResponse with conversation_id, messages, and tool_calls

    Raises:
        HTTPException 400: Invalid request (empty message, too long, etc.)
        HTTPException 401: Unauthorized (no auth token)
        HTTPException 500: Internal server error
    """
    try:
        # Validate message length
        if len(request.message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        # Generate conversation ID for new conversations
        conversation_id = request.conversation_id
        if conversation_id is None:
            conversation_id = generate_conversation_id()

        # Step 1: Load conversation history
        conversation_history = load_conversation_context(
            db=db,
            conversation_id=conversation_id,
            limit=20  # Sliding window
        )

        # Step 2: Save user message
        create_conversation_message(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            role="user",
            content=request.message,
            tool_calls=None
        )

        # Step 3: Call AI agent
        agent_response = chat_agent.chat(
            user_message=request.message,
            user_id=current_user.id,
            conversation_history=conversation_history,
            session=db,
            max_iterations=5
        )

        assistant_message = agent_response["assistant_message"]
        tool_calls = agent_response.get("tool_calls")

        # Step 4: Save assistant response
        create_conversation_message(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            role="assistant",
            content=assistant_message,
            tool_calls=tool_calls
        )

        # Step 5: Return response
        return ChatResponse(
            conversation_id=conversation_id,
            user_message=request.message,
            assistant_message=assistant_message,
            tool_calls=tool_calls
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
    limit: int = 50
):
    """
    Get list of user's conversations with metadata.

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of conversations to return

    Returns:
        List of conversations with metadata

    Raises:
        HTTPException 401: Unauthorized
    """
    try:
        conversations = get_user_conversations(
            db=db,
            user_id=current_user.id,
            limit=limit
        )

        return ConversationListResponse(conversations=conversations)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load conversations: {str(e)}"
        )
