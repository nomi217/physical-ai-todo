# OpenAI Agents SDK Integration Skill

## Purpose
Integrate OpenAI Agents SDK (now part of OpenAI Assistants API) for building conversational AI with tool calling and function execution.

## When to Use
- Building AI chatbots
- Implementing agentic workflows
- Creating conversational interfaces
- Integrating LLMs with application logic

## Inputs Required
- **MCP Tools**: List of available tools
- **System Prompt**: AI assistant behavior definition
- **Conversation History**: Previous messages
- **User Message**: Current user input

## Process

### 1. Install Dependencies
```bash
pip install openai==1.12.0
pip install python-dotenv
```

### 2. Environment Setup
```bash
# .env
OPENAI_API_KEY=sk-...your-key-here
```

### 3. Basic Agent with Tool Calling
```python
# backend/app/services/ai_agent.py
from openai import OpenAI
from typing import List, Dict, Any, Optional
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class TodoAgent:
    """AI agent for task management with MCP tools"""

    def __init__(self, tools: List[Dict[str, Any]]):
        self.tools = tools
        self.system_prompt = """
You are a helpful task management assistant. Your role is to help users manage their todo list through natural conversation.

When users mention:
- Adding/creating/remembering something → use add_task
- Showing/listing tasks → use list_tasks
- Completing/finishing/done → use complete_task
- Deleting/removing/canceling → use delete_task
- Changing/updating/renaming → use update_task

Always:
1. Confirm actions with friendly responses
2. Provide context when showing tasks
3. Handle errors gracefully
4. Be conversational and helpful

Example interactions:
User: "Add buy groceries to my list"
You: *use add_task* "I've added 'Buy groceries' to your task list!"

User: "What do I need to do?"
You: *use list_tasks* "Here are your pending tasks: [list]"

User: "Mark task 3 as done"
You: *use complete_task* "Great! I've marked 'Call mom' as complete."
"""

    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process user message and execute tools as needed.

        Args:
            user_message: User's input message
            conversation_history: Previous messages
            user_id: Current user's ID

        Returns:
            Response with assistant message and tool calls
        """
        # Build messages array
        messages = [
            {"role": "system", "content": self.system_prompt},
            *conversation_history,
            {"role": "user", "content": user_message}
        ]

        try:
            # Call OpenAI with tools
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",  # Let AI decide when to use tools
                temperature=0.7
            )

            assistant_message = response.choices[0].message
            tool_calls_data = []

            # Execute tool calls if any
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Inject user_id into tool arguments
                    tool_args["user_id"] = user_id

                    # Execute tool
                    from mcp_server.server import execute_mcp_tool
                    tool_result = await execute_mcp_tool(tool_name, tool_args)

                    tool_calls_data.append({
                        "id": tool_call.id,
                        "tool_name": tool_name,
                        "arguments": tool_args,
                        "result": tool_result
                    })

                # Get final response after tools
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Add tool results
                for tc_data in tool_calls_data:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc_data["id"],
                        "content": json.dumps(tc_data["result"])
                    })

                # Get natural language response
                final_response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=messages,
                    temperature=0.7
                )

                final_message = final_response.choices[0].message.content

            else:
                # No tools needed, use direct response
                final_message = assistant_message.content
                tool_calls_data = []

            return {
                "response": final_message,
                "tool_calls": tool_calls_data,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "tool_calls": [],
                "error": str(e)
            }
```

### 4. Stateless Chat Endpoint
```python
# backend/app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_session
from app.models import ConversationMessage, User
from app.auth.dependencies import get_current_user
from app.services.ai_agent import TodoAgent
from mcp_server.server import get_mcp_tools_for_openai

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[Dict[str, Any]]

# Initialize agent with MCP tools
mcp_tools = get_mcp_tools_for_openai()
agent = TodoAgent(tools=mcp_tools)

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Stateless chat endpoint.

    Flow:
    1. Fetch conversation history from database
    2. Store user message in database
    3. Call AI agent with history + new message
    4. Store assistant response in database
    5. Return response (server holds NO state)
    """

    # 1. Fetch conversation history
    if request.conversation_id:
        query = select(ConversationMessage).where(
            ConversationMessage.conversation_id == request.conversation_id,
            ConversationMessage.user_id == current_user.id
        ).order_by(ConversationMessage.created_at)

        history_records = session.execute(query).scalars().all()
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in history_records
        ]
    else:
        history = []

    # 2. Store user message
    user_msg = ConversationMessage(
        user_id=current_user.id,
        conversation_id=request.conversation_id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    session.add(user_msg)
    session.commit()
    session.refresh(user_msg)

    conversation_id = user_msg.conversation_id

    # 3. Call AI agent
    agent_response = await agent.chat(
        user_message=request.message,
        conversation_history=history,
        user_id=str(current_user.id)
    )

    # 4. Store assistant response
    assistant_msg = ConversationMessage(
        user_id=current_user.id,
        conversation_id=conversation_id,
        role="assistant",
        content=agent_response["response"],
        tool_calls=json.dumps(agent_response["tool_calls"]) if agent_response["tool_calls"] else None,
        created_at=datetime.utcnow()
    )
    session.add(assistant_msg)
    session.commit()

    # 5. Return response
    return ChatResponse(
        conversation_id=conversation_id,
        response=agent_response["response"],
        tool_calls=agent_response["tool_calls"]
    )
```

### 5. Streaming Responses (Optional)
```python
from fastapi.responses import StreamingResponse
import asyncio

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Streaming chat endpoint for real-time responses"""

    async def generate():
        # Fetch history (same as above)
        history = []  # ... fetch from DB

        # Stream response
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": agent.system_prompt},
                *history,
                {"role": "user", "content": request.message}
            ],
            tools=mcp_tools,
            stream=True
        )

        full_response = ""

        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield f"data: {json.dumps({'content': content})}\n\n"

        # Store messages after streaming
        # ... save to DB

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 6. Advanced: Multi-Turn Tool Execution
```python
async def execute_tools_iteratively(
    messages: List[Dict[str, str]],
    tools: List[Dict[str, Any]],
    user_id: str,
    max_iterations: int = 5
) -> str:
    """
    Allow agent to use multiple tools in sequence.

    Example: User says "delete the meeting task"
    1. Agent uses list_tasks to find "meeting task"
    2. Agent uses delete_task with the found task_id
    """

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # No more tools to call, return response
        if not assistant_message.tool_calls:
            return assistant_message.content

        # Add assistant message
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        # Execute each tool
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_args["user_id"] = user_id

            from mcp_server.server import execute_mcp_tool
            result = await execute_mcp_tool(tool_name, tool_args)

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    # Max iterations reached
    return "I've completed the requested operations."
```

### 7. Error Recovery
```python
async def chat_with_retry(
    user_message: str,
    history: List[Dict[str, str]],
    user_id: str,
    max_retries: int = 3
) -> Dict[str, Any]:
    """Retry logic for agent calls"""

    for attempt in range(max_retries):
        try:
            return await agent.chat(user_message, history, user_id)

        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    "response": "I'm having trouble right now. Please try again in a moment.",
                    "tool_calls": [],
                    "error": str(e)
                }

            await asyncio.sleep(2 ** attempt)  # Exponential backoff

    return {"response": "Error", "tool_calls": []}
```

### 8. Testing
```python
import pytest
from app.services.ai_agent import TodoAgent

@pytest.mark.asyncio
async def test_agent_add_task():
    agent = TodoAgent(tools=mcp_tools)

    response = await agent.chat(
        user_message="Add buy milk to my tasks",
        conversation_history=[],
        user_id="test_user"
    )

    assert "add_task" in str(response["tool_calls"])
    assert "milk" in response["response"].lower()

@pytest.mark.asyncio
async def test_agent_list_tasks():
    agent = TodoAgent(tools=mcp_tools)

    response = await agent.chat(
        user_message="Show me my tasks",
        conversation_history=[],
        user_id="test_user"
    )

    assert "list_tasks" in str(response["tool_calls"])
```

## Best Practices

### System Prompts
- Be specific about tool usage
- Provide examples of user interactions
- Define personality and tone
- Include error handling guidance

### Tool Calling
- Use `tool_choice="auto"` for flexibility
- Always inject user_id into tool arguments
- Handle tool errors gracefully
- Log all tool executions

### Conversation Management
- Store all messages in database
- Include tool calls in message history
- Order by created_at for replay
- Limit history length (last 20-50 messages)

### Performance
- Use GPT-4 Turbo for best results
- Set appropriate temperature (0.7 for chat)
- Implement streaming for better UX
- Cache tool definitions

### Cost Optimization
- Limit context window (last N messages)
- Use cheaper models for simple queries
- Implement caching for repeated queries
- Monitor token usage

## Output
- Conversational AI agent
- Tool calling integration
- Stateless chat endpoint
- Error handling and retry logic
- Streaming support
