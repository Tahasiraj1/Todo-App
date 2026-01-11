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
