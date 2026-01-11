# [Task]: T013 [From]: data-model.md, Better Auth documentation
"""
User SQLModel for database representation.
Note: User authentication is managed by Better Auth on frontend.
Backend primarily receives user_id from JWT token.
This model matches Better Auth's user table schema.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .task import Task


class User(SQLModel, table=True):
    """
    Represents an authenticated user account.
    Schema matches Better Auth's user table.

    Attributes:
        id: Unique user identifier (from Better Auth)
        email: User's email address (unique)
        name: User's display name
        emailVerified: Whether the email has been verified
        image: User's profile image URL
        createdAt: Account creation timestamp
        updatedAt: Last update timestamp
    """
    __tablename__ = "user"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None, max_length=255)
    emailVerified: bool = Field(default=False)
    image: Optional[str] = Field(default=None, max_length=255)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: list["Task"] = Relationship(back_populates="user")
