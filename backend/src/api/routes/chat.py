# [Task]: T020-T027 [From]: contracts/chat-api.md
"""
Chat API routes.
All endpoints require JWT authentication and validate user_id from URL matches JWT.
Endpoint pattern: /api/{user_id}/chat, /api/{user_id}/conversations
"""

from fastapi import APIRouter, HTTPException, status

from ..dependencies import CurrentUserId, DbSession
from ...models.schemas import (
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationSummary,
    MessageResponse,
)
from ...services.chat_service import ChatService
from ...services.conversation_service import ConversationService

router = APIRouter()


def validate_user_id(path_user_id: str, jwt_user_id: str) -> None:
    """
    Validate that the user_id in the URL path matches the user_id from JWT token.

    Args:
        path_user_id: The user_id from the URL path
        jwt_user_id: The user_id extracted from the JWT token

    Raises:
        HTTPException: 403 Forbidden if user_ids don't match
    """
    if path_user_id != jwt_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own data",
        )


# ============================================================================
# Chat Endpoint
# ============================================================================


@router.post("/chat", response_model=ChatResponse)
async def send_message(
    user_id: str,
    request: ChatRequest,
    session: DbSession,
    jwt_user_id: CurrentUserId,
) -> ChatResponse:
    """
    Send a message and receive an AI-generated response.
    POST /api/{user_id}/chat

    Args:
        user_id: User ID from URL path (must match JWT token)
        request: Chat request with message and optional conversation_id

    Returns:
        ChatResponse: AI response with conversation_id and tool_calls
    """
    validate_user_id(user_id, jwt_user_id)

    chat_service = ChatService(session, user_id)
    response = await chat_service.process_message(
        message=request.message,
        conversation_id=request.conversation_id,
    )

    return response


# ============================================================================
# Conversation Management Endpoints
# ============================================================================


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    user_id: str,
    session: DbSession,
    jwt_user_id: CurrentUserId,
    limit: int = 50,
    offset: int = 0,
) -> list[ConversationSummary]:
    """
    List all conversations for the authenticated user.
    GET /api/{user_id}/conversations

    Args:
        user_id: User ID from URL path (must match JWT token)
        limit: Maximum number of conversations to return (default 50)
        offset: Number of conversations to skip (for pagination)

    Returns:
        List of conversation summaries ordered by most recent
    """
    validate_user_id(user_id, jwt_user_id)

    service = ConversationService(session, user_id)
    conversations = service.list_conversations(limit=limit, offset=offset)

    return [
        ConversationSummary(
            id=c.id,
            user_id=c.user_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=service.get_message_count(c.id),
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    user_id: str,
    conversation_id: int,
    session: DbSession,
    jwt_user_id: CurrentUserId,
) -> ConversationResponse:
    """
    Get a specific conversation with its messages.
    GET /api/{user_id}/conversations/{conversation_id}

    Args:
        user_id: User ID from URL path (must match JWT token)
        conversation_id: The conversation ID

    Returns:
        ConversationResponse: Conversation with all messages
    """
    validate_user_id(user_id, jwt_user_id)

    service = ConversationService(session, user_id)
    conversation = service.get_conversation(conversation_id)
    messages = service.get_messages(conversation_id)

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            ChatMessageResponse(
                id=m.id,
                role=str(m.role),
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


@router.delete("/conversations/{conversation_id}", response_model=MessageResponse)
async def delete_conversation(
    user_id: str,
    conversation_id: int,
    session: DbSession,
    jwt_user_id: CurrentUserId,
) -> MessageResponse:
    """
    Delete a conversation and all its messages.
    DELETE /api/{user_id}/conversations/{conversation_id}

    Args:
        user_id: User ID from URL path (must match JWT token)
        conversation_id: The conversation ID

    Returns:
        MessageResponse: Success message
    """
    validate_user_id(user_id, jwt_user_id)

    service = ConversationService(session, user_id)
    service.delete_conversation(conversation_id)

    return MessageResponse(message="Conversation deleted successfully")
