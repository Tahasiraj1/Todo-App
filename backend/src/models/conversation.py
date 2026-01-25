# [Task]: T006 [From]: data-model.md §Conversation Model
"""
Conversation SQLModel for database representation.
Represents a chat session between a user and the AI assistant.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .message import Message
    from .user import User


class Conversation(SQLModel, table=True):
    """
    Represents a chat conversation session.

    Attributes:
        id: Unique conversation identifier (auto-incrementing)
        user_id: Owner of the conversation (references User.id)
        created_at: Conversation creation timestamp
        updated_at: Last activity timestamp
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")
