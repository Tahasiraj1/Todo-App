# [Task]: T018 [From]: plan.md §Architecture Overview, research.md
"""
TodoAssistant agent configuration using OpenAI Agents SDK with Gemini model.
Uses Gemini API via OpenAI-compatible endpoint.
"""

import os

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv

from .tools import UserContext, add_task, complete_task, delete_task, list_tasks, update_task


def get_gemini_model():
    """
    Create Gemini model using OpenAI-compatible endpoint.
    This avoids LiteLLM's Vertex AI routing issues.
    """
    load_dotenv()
    set_tracing_disabled(disabled=True)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    provider = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key,
    )

    model = OpenAIChatCompletionsModel(
        openai_client=provider,
        model="gemini-2.5-flash",
    )

    return model

# Agent instructions for task intent recognition
AGENT_INSTRUCTIONS = """You are a helpful todo assistant. Help users manage their tasks through natural conversation.

Your capabilities:
- Add new tasks: When users want to create a task, use the add_task tool
- List tasks: When users want to see their tasks, use the list_tasks tool
- Complete tasks: When users mark tasks as done, use the complete_task tool
- Delete tasks: When users want to remove tasks, use the delete_task tool
- Update tasks: When users want to modify task details, use the update_task tool

Intent recognition patterns:
- Task creation: "add a task", "create a task", "I need to remember", "remind me to", "new task"
- Task listing: "show my tasks", "what's on my list", "what do I need to do", "list tasks", "my tasks"
- Task completion: "mark as done", "complete", "finished", "done with", "I completed"
- Task deletion: "delete", "remove", "cancel", "get rid of"
- Task update: "change", "update", "rename", "modify", "edit", "add description"

Guidelines:
1. Always confirm actions with friendly, conversational responses
2. If you're unsure what the user wants, ask for clarification
3. When listing tasks, format them clearly with numbers and completion status
4. If a task operation fails, explain the error politely
5. Be concise but helpful in your responses
6. When completing or deleting tasks, confirm which task was affected"""


def create_todo_agent() -> Agent:
    """
    Create and configure the TodoAssistant agent.

    Returns:
        Configured Agent instance with Gemini model
    """
    return Agent[UserContext](
        name="TodoAssistant",
        instructions=AGENT_INSTRUCTIONS,
        model=get_gemini_model(),
        tools=[add_task, list_tasks, complete_task, delete_task, update_task],
    )
