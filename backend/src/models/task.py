# [Task]: T014 [From]: data-model.md §Task Model
"""
Task SQLModel for database representation.
Represents a todo item belonging to a user.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

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
        created_at: Task creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks")
