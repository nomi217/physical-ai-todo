"""
MCP Tool Schemas for Phase III AI Chatbot

Defines Pydantic schemas for all MCP tools that the AI agent can use
to interact with tasks. These schemas validate tool parameters and
ensure type safety.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class AddTaskSchema(BaseModel):
    """Schema for add_task MCP tool"""
    user_id: int = Field(description="ID of the user creating the task")
    title: str = Field(description="Task title", min_length=1, max_length=500)
    description: str = Field(default="", description="Task description", max_length=5000)
    priority: Literal["low", "medium", "high"] = Field(default="medium", description="Task priority level")


class ListTasksSchema(BaseModel):
    """Schema for list_tasks MCP tool"""
    user_id: int = Field(description="ID of the user requesting tasks")
    status: Literal["all", "pending", "completed"] = Field(
        default="all",
        description="Filter by task status"
    )
    priority: Optional[Literal["low", "medium", "high"]] = Field(
        default=None,
        description="Filter by priority level"
    )
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of tasks to return")


class CompleteTaskSchema(BaseModel):
    """Schema for complete_task MCP tool - accepts either task_id OR task_title"""
    user_id: int = Field(description="ID of the user completing the task")
    task_id: Optional[int] = Field(default=None, description="ID of the task to mark as complete", gt=0)
    task_title: Optional[str] = Field(default=None, description="Title/name of the task to complete")


class DeleteTaskSchema(BaseModel):
    """Schema for delete_task MCP tool - accepts either task_id OR task_title"""
    user_id: int = Field(description="ID of the user deleting the task")
    task_id: Optional[int] = Field(default=None, description="ID of the task to delete", gt=0)
    task_title: Optional[str] = Field(default=None, description="Title/name of the task to delete")


class UpdateTaskSchema(BaseModel):
    """Schema for update_task MCP tool - accepts either task_id OR task_title to identify task"""
    user_id: int = Field(description="ID of the user updating the task")
    task_id: Optional[int] = Field(default=None, description="ID of the task to update", gt=0)
    task_title: Optional[str] = Field(default=None, description="Current title/name of the task to update")
    title: Optional[str] = Field(default=None, description="New task title", max_length=500)
    description: Optional[str] = Field(default=None, description="New task description", max_length=5000)
    priority: Optional[Literal["low", "medium", "high"]] = Field(
        default=None,
        description="New priority level"
    )
