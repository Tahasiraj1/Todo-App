# [Task]: T007 [From]: data-model.md §Message Model
"""
Message SQLModel for database representation.
Represents a single message in a conversation (user or assistant).
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation import Conversation
    from .user import User


class MessageRole(str, Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Represents a message in a conversation.

    Attributes:
        id: Unique message identifier (auto-incrementing)
        user_id: Owner of the message (for security filtering)
        conversation_id: Parent conversation
        role: Who sent the message (user or assistant)
        content: The message content
        created_at: Message creation timestamp
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column=sa.Column(sa.String(20), nullable=False))
    content: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="messages")
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
