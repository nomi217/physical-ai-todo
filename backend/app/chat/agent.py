"""
AI Agent for Phase III Chatbot

Handles OpenAI API integration with function calling for MCP tools.
Manages conversation flow and tool execution.
"""

import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from sqlmodel import Session

from app.chat.prompts import SYSTEM_PROMPT
from app.mcp.tools import TOOLS


class ChatAgent:
    """AI Agent that manages OpenAI API calls and tool execution."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the chat agent.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (defaults to OPENAI_MODEL env var or gpt-4-turbo-preview)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        # Use gpt-4-turbo-preview for faster responses and lower cost
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.client = OpenAI(api_key=self.api_key)

    def _build_messages(
        self,
        conversation_history: List[Dict[str, Any]],
        user_message: str
    ) -> List[Dict[str, str]]:
        """
        Build messages array for OpenAI API.

        Args:
            conversation_history: Previous messages in conversation
            user_message: Current user message

        Returns:
            List of message dictionaries for OpenAI API
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _build_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Build OpenAI function calling schema from MCP tools.

        Returns:
            List of tool definitions for OpenAI API
        """
        tools = []
        for tool_name, tool_config in TOOLS.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_config["description"],
                    "parameters": tool_config["parameters"]
                }
            })
        return tools

    def _execute_tool(
        self,
        tool_name: str,
        tool_arguments: Dict[str, Any],
        session: Session
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool function.

        Args:
            tool_name: Name of the tool to execute
            tool_arguments: Arguments for the tool
            session: Database session

        Returns:
            Tool execution result
        """
        if tool_name not in TOOLS:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

        tool_config = TOOLS[tool_name]
        tool_function = tool_config["function"]
        schema_class = tool_config["schema"]

        try:
            # Validate and parse arguments
            params = schema_class(**tool_arguments)

            # Execute tool
            result = tool_function(params, session)

            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute {tool_name}: {str(e)}"
            }

    def chat(
        self,
        user_message: str,
        user_id: int,
        conversation_history: List[Dict[str, Any]],
        session: Session,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Process a chat message and execute any necessary tools.

        Args:
            user_message: User's message
            user_id: ID of the user
            conversation_history: Previous messages
            session: Database session
            max_iterations: Maximum number of tool calling iterations

        Returns:
            Dict with assistant_message and tool_calls
        """
        messages = self._build_messages(conversation_history, user_message)
        tools = self._build_tools_schema()

        tool_calls_log = []
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            try:
                # Call OpenAI API with optimized parameters for speed
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.3,  # Lower temperature for faster, more consistent responses
                    max_tokens=500   # Allow enough tokens for complete task lists
                )

                response_message = response.choices[0].message

                # Check if AI wants to call tools
                if response_message.tool_calls:
                    # Add AI's response to messages
                    messages.append({
                        "role": "assistant",
                        "content": response_message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in response_message.tool_calls
                        ]
                    })

                    # Execute each tool call
                    for tool_call in response_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_arguments = json.loads(tool_call.function.arguments)

                        # DEBUG: Log before injection
                        print(f"DEBUG Agent: Tool {tool_name} called with args: {tool_arguments}")
                        print(f"DEBUG Agent: Current user_id for this chat: {user_id}")

                        # Inject user_id if not provided
                        if "user_id" not in tool_arguments:
                            tool_arguments["user_id"] = user_id
                            print(f"DEBUG Agent: Injected user_id {user_id} into tool_arguments")
                        else:
                            print(f"DEBUG Agent: Tool already has user_id: {tool_arguments['user_id']}")

                        # Execute tool
                        tool_result = self._execute_tool(tool_name, tool_arguments, session)

                        # Log tool call
                        tool_calls_log.append({
                            "tool": tool_name,
                            "arguments": tool_arguments,
                            "result": tool_result
                        })

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(tool_result)
                        })

                    # Continue loop to get AI's response with tool results
                    continue

                else:
                    # No more tool calls - return final response
                    return {
                        "assistant_message": response_message.content or "",
                        "tool_calls": tool_calls_log if tool_calls_log else None,
                        "iterations": iterations
                    }

            except Exception as e:
                return {
                    "assistant_message": f"I encountered an error: {str(e)}. Please try again.",
                    "tool_calls": tool_calls_log if tool_calls_log else None,
                    "error": str(e),
                    "iterations": iterations
                }

        # Max iterations reached
        return {
            "assistant_message": "I apologize, but I'm having trouble completing that request. Please try breaking it down into smaller steps.",
            "tool_calls": tool_calls_log if tool_calls_log else None,
            "iterations": iterations,
            "error": "Max iterations reached"
        }
