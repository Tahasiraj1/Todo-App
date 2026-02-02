# [Task]: T014, T008 [From]: data-model.md §Task Model
"""
Task SQLModel for database representation.
Represents a todo item belonging to a user.
Phase V extensions: priority, tags, due_date, recurrence fields, reminder_sent.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy import JSON


if TYPE_CHECKING:
    from .user import User


class Task(SQLModel, table=True):
    """
    Represents a todo item.

    Attributes:
        id: Unique task identifier (auto-incrementing)
        user_id: Owner of the task (references User.id)
        title: Task title (1-200 characters)
        description: Task description (optional, max 1000 characters)
        completed: Task completion status (defaults to False)
        priority: Task priority level (high/medium/low, default medium)
        tags: JSON array of string tags (default [])
        due_date: Optional deadline timestamp
        is_recurring: Whether task repeats on a schedule
        recurrence_frequency: daily/weekly/monthly (required if is_recurring)
        recurrence_interval: Repeat every N periods (default 1)
        recurrence_day_of_week: 0-6 Mon-Sun (weekly only)
        recurrence_day_of_month: 1-31 (monthly only)
        recurrence_end_date: Optional end date for recurrence
        reminder_sent: Whether reminder was published for current due_date
        created_at: Task creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)

    # Phase V: Priority and tags
    priority: str = Field(default="medium", max_length=10, index=True)
    tags: Any = Field(default=[], sa_column=Column(JSON, nullable=False, server_default="[]"))

    # Phase V: Due date and reminders
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_sent: bool = Field(default=False)

    # Phase V: Recurrence
    is_recurring: bool = Field(default=False)
    recurrence_frequency: Optional[str] = Field(default=None, max_length=10)
    recurrence_interval: int = Field(default=1)
    recurrence_day_of_week: Optional[int] = Field(default=None)
    recurrence_day_of_month: Optional[int] = Field(default=None)
    recurrence_end_date: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks")
