# [Task]: T019, T028-T033 [From]: plan.md §Architecture Overview
"""
Chat service for orchestrating AI agent conversations.
Handles message processing, agent invocation, and response formatting.
"""

import logging
from typing import Optional

from agents import Runner
from sqlmodel import Session

from ..agent import UserContext, create_todo_agent
from ..models.message import MessageRole
from ..models.schemas import ChatResponse, ToolCall
from .conversation_service import ConversationService

logger = logging.getLogger(__name__)

# Maximum messages to load for agent context
MAX_CONTEXT_MESSAGES = 100


class ChatService:
    """Service class for processing chat messages with AI agent."""

    def __init__(self, session: Session, user_id: str):
        """
        Initialize ChatService.

        Args:
            session: SQLModel database session
            user_id: Authenticated user's ID
        """
        self.session = session
        self.user_id = user_id
        self.conversation_service = ConversationService(session, user_id)
        self._agent = None

    @property
    def agent(self):
        """Lazy initialization of the agent."""
        if self._agent is None:
            self._agent = create_todo_agent()
        return self._agent

    async def process_message(
        self,
        message: str,
        conversation_id: Optional[int] = None,
    ) -> ChatResponse:
        """
        Process a user message and return AI response.

        This method:
        1. Creates or validates conversation
        2. Loads conversation history
        3. Stores user message
        4. Runs agent with context
        5. Stores assistant response
        6. Returns formatted response

        Args:
            message: User's message text
            conversation_id: Optional existing conversation ID

        Returns:
            ChatResponse with conversation_id, response, and tool_calls
        """
        logger.info(
            f"Processing message: user_id={self.user_id}, "
            f"conversation_id={conversation_id}, message_length={len(message)}"
        )

        # Step 1: Get or create conversation
        if conversation_id is None:
            conversation = self.conversation_service.create_conversation()
            conversation_id = conversation.id
            logger.info(f"Created new conversation: id={conversation_id}")
        else:
            # Validate conversation exists and belongs to user
            conversation = self.conversation_service.get_conversation(conversation_id)
            logger.debug(f"Using existing conversation: id={conversation_id}")

        # Step 2: Load conversation history for context
        history = self.conversation_service.build_agent_context(conversation_id)
        logger.debug(f"Loaded {len(history)} messages for context")

        # Step 3: Store user message immediately
        self.conversation_service.add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message,
        )

        # Step 4: Build messages for agent
        # Combine history with new message
        messages_for_agent = []
        if history:
            messages_for_agent.extend(history)
        messages_for_agent.append({"role": "user", "content": message})

        # Step 5: Run agent with UserContext (injected into tools automatically)
        user_context = UserContext(user_id=self.user_id)
        try:
            result = await Runner.run(
                self.agent,
                messages_for_agent,
                context=user_context,
            )

            # Extract response text
            response_text = result.final_output if result.final_output else "I processed your request."

            # Extract tool calls from the run result
            tool_calls = self._extract_tool_calls(result)

            logger.info(
                f"Agent completed: conversation_id={conversation_id}, "
                f"tool_calls={len(tool_calls)}"
            )

        except Exception as e:
            logger.exception(f"Agent error: {e}")
            response_text = (
                "I'm sorry, I encountered an error processing your request. "
                "Please try again or rephrase your message."
            )
            tool_calls = []

        # Step 6: Store assistant response
        self.conversation_service.add_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response_text,
        )

        # Step 7: Return formatted response
        return ChatResponse(
            conversation_id=conversation_id,
            response=response_text,
            tool_calls=tool_calls,
        )

    def _extract_tool_calls(self, result) -> list[ToolCall]:
        """
        Extract tool calls from agent run result.

        Args:
            result: Agent run result

        Returns:
            List of ToolCall objects
        """
        tool_calls = []

        try:
            # The result object structure depends on the agents SDK version
            # Access raw_responses or new_items to find tool calls
            if hasattr(result, "new_items"):
                for item in result.new_items:
                    if hasattr(item, "type") and item.type == "tool_call_item":
                        tool_call = ToolCall(
                            tool=item.raw_item.name if hasattr(item.raw_item, "name") else "unknown",
                            parameters=item.raw_item.arguments if hasattr(item.raw_item, "arguments") else {},
                            result=item.output if hasattr(item, "output") else None,
                        )
                        tool_calls.append(tool_call)
        except Exception as e:
            logger.warning(f"Error extracting tool calls: {e}")

        return tool_calls
