# [Task]: T015, T105 [From]: data-model.md §Task Create/Update Schemas
"""
Pydantic schemas for Task API request/response validation.
Includes input sanitization for special characters and unicode.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def sanitize_text(text: str) -> str:
    """
    Sanitize input text by:
    - Stripping leading/trailing whitespace
    - Normalizing unicode characters
    - Removing control characters (except newlines/tabs in descriptions)
    """
    if not text:
        return text
    # Remove control characters except newline and tab
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Normalize whitespace
    sanitized = sanitized.strip()
    return sanitized


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        sanitized = sanitize_text(v)
        if not sanitized:
            raise ValueError("Title cannot be empty after sanitization")
        return sanitized

    @field_validator("description")
    @classmethod
    def description_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            sanitized = sanitize_text(v)
            return sanitized if sanitized else None
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator("title")
    @classmethod
    def title_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty")
            sanitized = sanitize_text(v)
            if not sanitized:
                raise ValueError("Title cannot be empty after sanitization")
            return sanitized
        return v

    @field_validator("description")
    @classmethod
    def description_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            sanitized = sanitize_text(v)
            return sanitized if sanitized else None
        return v


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for list of tasks response."""
    tasks: list[TaskResponse]


class MessageResponse(BaseModel):
    """Schema for simple message response."""
    message: str


# Chat API Schemas (Phase III)


class ChatRequest(BaseModel):
    """Schema for chat API request."""
    conversation_id: Optional[int] = Field(
        None, description="Existing conversation ID. If not provided, creates a new conversation"
    )
    message: str = Field(..., min_length=1, max_length=2000, description="User's natural language message")

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return sanitize_text(v)


class ToolCall(BaseModel):
    """Schema for a tool invocation during chat processing."""
    tool: str = Field(..., description="Name of the MCP tool that was called")
    parameters: dict = Field(..., description="Parameters passed to the tool")
    result: Optional[dict | list] = Field(None, description="Result returned by the tool")

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """Schema for chat API response."""
    conversation_id: int = Field(..., description="The conversation ID (new or existing)")
    response: str = Field(..., description="AI assistant's response message")
    tool_calls: list[ToolCall] = Field(
        default_factory=list, description="List of MCP tools that were invoked during processing"
    )

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    """Schema for a single message in conversation history."""
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    """Schema for conversation list response (without messages)."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Schema for single conversation with messages."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
