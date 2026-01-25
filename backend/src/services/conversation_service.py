# [Task]: T010 [From]: plan.md §Project Structure
"""
Conversation service for managing chat conversations and messages.
All operations filter by user_id for data isolation.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlmodel import Session, func, select

from ..middleware.error_handler import NotFoundError
from ..models.conversation import Conversation
from ..models.message import Message, MessageRole

logger = logging.getLogger(__name__)


class ConversationService:
    """Service class for conversation and message operations."""

    def __init__(self, session: Session, user_id: str):
        """
        Initialize ConversationService.

        Args:
            session: SQLModel database session
            user_id: Authenticated user's ID
        """
        self.session = session
        self.user_id = user_id

    def create_conversation(self) -> Conversation:
        """
        Create a new conversation for the authenticated user.

        Returns:
            The created conversation
        """
        conversation = Conversation(user_id=self.user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        logger.info(f"Conversation created: id={conversation.id}, user_id={self.user_id}")
        return conversation

    def get_conversation(self, conversation_id: int) -> Conversation:
        """
        Get a specific conversation by ID.

        Args:
            conversation_id: The conversation ID

        Returns:
            The conversation if found and belongs to user

        Raises:
            NotFoundError: If conversation not found or doesn't belong to user
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == self.user_id,
        )
        conversation = self.session.exec(statement).first()

        if not conversation:
            logger.warning(
                f"Conversation not found: id={conversation_id}, user_id={self.user_id}"
            )
            raise NotFoundError("Conversation not found")

        return conversation

    def list_conversations(self, limit: int = 50, offset: int = 0) -> list[Conversation]:
        """
        List all conversations for the authenticated user.

        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of conversations belonging to the user, ordered by updated_at DESC
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == self.user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        conversations = self.session.exec(statement).all()

        logger.debug(f"Listed {len(conversations)} conversations for user_id={self.user_id}")
        return list(conversations)

    def delete_conversation(self, conversation_id: int) -> None:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: The conversation ID

        Raises:
            NotFoundError: If conversation not found or doesn't belong to user
        """
        conversation = self.get_conversation(conversation_id)
        self.session.delete(conversation)
        self.session.commit()

        logger.info(f"Conversation deleted: id={conversation_id}, user_id={self.user_id}")

    def add_message(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: The conversation ID
            role: Message role (user or assistant)
            content: Message content

        Returns:
            The created message

        Raises:
            NotFoundError: If conversation not found or doesn't belong to user
        """
        # Verify conversation exists and belongs to user
        conversation = self.get_conversation(conversation_id)

        # Create message
        message = Message(
            user_id=self.user_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.session.add(message)

        # Update conversation's updated_at
        conversation.updated_at = datetime.utcnow()
        self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)

        logger.debug(
            f"Message added: conversation_id={conversation_id}, role={role.value}, "
            f"user_id={self.user_id}"
        )
        return message

    def get_messages(
        self,
        conversation_id: int,
        limit: int = 100,
    ) -> list[Message]:
        """
        Get messages for a conversation.

        Args:
            conversation_id: The conversation ID
            limit: Maximum number of messages to return (default 100 per spec)

        Returns:
            List of messages ordered by created_at ASC

        Raises:
            NotFoundError: If conversation not found or doesn't belong to user
        """
        # Verify conversation exists and belongs to user
        self.get_conversation(conversation_id)

        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == self.user_id,
            )
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages = self.session.exec(statement).all()

        logger.debug(
            f"Retrieved {len(messages)} messages for conversation_id={conversation_id}, "
            f"user_id={self.user_id}"
        )
        return list(messages)

    def get_message_count(self, conversation_id: int) -> int:
        """
        Get the number of messages in a conversation.

        Args:
            conversation_id: The conversation ID

        Returns:
            Number of messages in the conversation

        Raises:
            NotFoundError: If conversation not found or doesn't belong to user
        """
        # Verify conversation exists and belongs to user
        self.get_conversation(conversation_id)

        statement = (
            select(func.count(Message.id))
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == self.user_id,
            )
        )
        count = self.session.exec(statement).one()

        return count

    def build_agent_context(self, conversation_id: int) -> list[dict]:
        """
        Build message history for agent from database.

        Args:
            conversation_id: The conversation ID

        Returns:
            List of message dicts with role and content for agent context
        """
        messages = self.get_messages(conversation_id)
        return [
            {"role": str(msg.role), "content": msg.content}
            for msg in messages
        ]
