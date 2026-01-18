"""
Conversation Context Management for Phase III Chatbot

Loads conversation history from the database and formats it
for the AI agent. Implements sliding window to keep context
manageable.
"""

from typing import List, Dict, Any
from sqlmodel import Session

from app.crud import get_conversation_history


def load_conversation_context(
    db: Session,
    conversation_id: int,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Load conversation history from database for AI context.

    Args:
        db: Database session
        conversation_id: ID of the conversation
        limit: Maximum number of messages to load (sliding window)

    Returns:
        List of message dictionaries with role and content
    """
    messages = get_conversation_history(db, conversation_id, limit)

    # Convert to format expected by AI agent
    conversation_context = []
    for msg in messages:
        message_dict = {
            "role": msg.role,
            "content": msg.content
        }

        # Include tool calls if present (for assistant messages)
        if msg.tool_calls:
            message_dict["tool_calls"] = msg.tool_calls

        conversation_context.append(message_dict)

    return conversation_context


def generate_conversation_id() -> int:
    """
    Generate a new conversation ID.

    For now, we use timestamp-based IDs. In production,
    this could be a UUID or database-generated sequence.

    Returns:
        New conversation ID as integer
    """
    import time
    return int(time.time() * 1000)  # Millisecond timestamp
