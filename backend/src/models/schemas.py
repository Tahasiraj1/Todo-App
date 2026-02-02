# [Task]: T015, T105, T009, T010, T011 [From]: data-model.md §Task Create/Update Schemas
"""
Pydantic schemas for Task API request/response validation.
Includes input sanitization for special characters and unicode.
Phase V extensions: priority, tags, due_date, recurrence fields.
"""

import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


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
    priority: Literal["high", "medium", "low"] = Field(default="medium")
    tags: list[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_frequency: Optional[Literal["daily", "weekly", "monthly"]] = None
    recurrence_interval: int = Field(default=1, ge=1)
    recurrence_day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    recurrence_day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    recurrence_end_date: Optional[datetime] = None

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

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("Maximum 10 tags per task")
        validated = []
        for tag in v:
            tag = tag.strip().lower()
            if not tag:
                continue
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag[:20]}...' exceeds 50 character limit")
            validated.append(tag)
        return validated

    @model_validator(mode="after")
    def validate_recurrence(self) -> "TaskCreate":
        if self.is_recurring and not self.recurrence_frequency:
            raise ValueError("recurrence_frequency is required when is_recurring is true")
        if not self.is_recurring:
            self.recurrence_frequency = None
            self.recurrence_day_of_week = None
            self.recurrence_day_of_month = None
            self.recurrence_end_date = None
        if self.recurrence_day_of_week is not None and self.recurrence_frequency != "weekly":
            raise ValueError("recurrence_day_of_week is only valid for weekly frequency")
        if self.recurrence_day_of_month is not None and self.recurrence_frequency != "monthly":
            raise ValueError("recurrence_day_of_month is only valid for monthly frequency")
        return self


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Literal["high", "medium", "low"]] = None
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_frequency: Optional[Literal["daily", "weekly", "monthly"]] = None
    recurrence_interval: Optional[int] = Field(default=None, ge=1)
    recurrence_day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    recurrence_day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    recurrence_end_date: Optional[datetime] = None

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

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("Maximum 10 tags per task")
        validated = []
        for tag in v:
            tag = tag.strip().lower()
            if not tag:
                continue
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag[:20]}...' exceeds 50 character limit")
            validated.append(tag)
        return validated


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str = "medium"
    tags: list[str] = []
    due_date: Optional[datetime] = None
    is_overdue: bool = False
    is_recurring: bool = False
    recurrence_frequency: Optional[str] = None
    recurrence_interval: int = 1
    recurrence_day_of_week: Optional[int] = None
    recurrence_day_of_month: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def compute_is_overdue(self) -> "TaskResponse":
        if self.due_date and not self.completed:
            from datetime import timezone
            now = datetime.now(timezone.utc)
            due = self.due_date if self.due_date.tzinfo else self.due_date.replace(tzinfo=timezone.utc)
            self.is_overdue = due < now
        else:
            self.is_overdue = False
        return self


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
