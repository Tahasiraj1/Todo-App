# [Task]: T013, T014, T015, T016, T017 [From]: contracts/mcp-tools.md
"""
MCP-style tool functions for the AI agent.
Each tool wraps TaskService operations and returns structured results.
User context is injected via RunContextWrapper - NOT passed by the LLM.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from agents import RunContextWrapper, function_tool

from ..db import get_db_session
from ..middleware.error_handler import NotFoundError
from ..models.schemas import TaskCreate, TaskUpdate
from ..services.task_service import TaskService

logger = logging.getLogger(__name__)


@dataclass
class UserContext:
    """Context object containing user information for tool execution."""
    user_id: str


@function_tool
def add_task(
    wrapper: RunContextWrapper[UserContext],
    title: str,
    description: Optional[str] = None,
) -> dict:
    """
    Add a new task for the user.

    Args:
        title: Task title (required, max 200 chars)
        description: Task description (optional, max 1000 chars)

    Returns:
        dict with task_id, status, and title
    """
    user_id = wrapper.context.user_id
    logger.info(f"add_task called: user_id={user_id}, title={title}")

    if not title or not title.strip():
        return {"error": "title is required"}

    if len(title) > 200:
        return {"error": "title exceeds maximum length"}

    try:
        with get_db_session() as session:
            service = TaskService(session, user_id)
            task_data = TaskCreate(title=title.strip(), description=description)
            task = service.create_task(task_data)

            logger.info(f"Task created via tool: id={task.id}, user_id={user_id}")
            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
            }
    except ValueError as e:
        logger.warning(f"add_task validation error: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"add_task error: {e}")
        return {"error": "Failed to create task"}


@function_tool
def list_tasks(
    wrapper: RunContextWrapper[UserContext],
    status: Optional[str] = None,
) -> list[dict]:
    """
    List tasks for the user.

    Args:
        status: Filter by status - "all", "pending", or "completed" (default: "all")

    Returns:
        List of task objects with id, title, completed, and description
    """
    user_id = wrapper.context.user_id
    filter_status = status or "all"
    logger.info(f"list_tasks called: user_id={user_id}, status={filter_status}")

    try:
        with get_db_session() as session:
            service = TaskService(session, user_id)
            tasks = service.list_tasks()

            # Filter by status if specified
            if filter_status == "pending":
                tasks = [t for t in tasks if not t.completed]
            elif filter_status == "completed":
                tasks = [t for t in tasks if t.completed]

            logger.info(f"Listed {len(tasks)} tasks for user_id={user_id}")
            return [
                {
                    "id": t.id,
                    "title": t.title,
                    "completed": t.completed,
                    "description": t.description,
                }
                for t in tasks
            ]
    except Exception as e:
        logger.error(f"list_tasks error: {e}")
        return []


@function_tool
def complete_task(
    wrapper: RunContextWrapper[UserContext],
    task_id: int,
) -> dict:
    """
    Mark a task as complete.

    Args:
        task_id: The task ID to complete

    Returns:
        dict with task_id, status, and title
    """
    user_id = wrapper.context.user_id
    logger.info(f"complete_task called: user_id={user_id}, task_id={task_id}")

    try:
        with get_db_session() as session:
            service = TaskService(session, user_id)
            task = service.toggle_task_completion(task_id)

            # Ensure it's marked as completed (toggle might have uncompleted it)
            if not task.completed:
                task = service.toggle_task_completion(task_id)

            logger.info(f"Task completed via tool: id={task_id}, user_id={user_id}")
            return {
                "task_id": task.id,
                "status": "completed",
                "title": task.title,
            }
    except NotFoundError:
        logger.warning(f"complete_task: Task not found - id={task_id}, user_id={user_id}")
        return {"error": "Task not found"}
    except Exception as e:
        logger.error(f"complete_task error: {e}")
        return {"error": "Failed to complete task"}


@function_tool
def delete_task(
    wrapper: RunContextWrapper[UserContext],
    task_id: int,
) -> dict:
    """
    Delete a task.

    Args:
        task_id: The task ID to delete

    Returns:
        dict with task_id, status, and title
    """
    user_id = wrapper.context.user_id
    logger.info(f"delete_task called: user_id={user_id}, task_id={task_id}")

    try:
        with get_db_session() as session:
            service = TaskService(session, user_id)
            # Get task info before deletion
            task = service.get_task(task_id)
            title = task.title

            service.delete_task(task_id)

            logger.info(f"Task deleted via tool: id={task_id}, user_id={user_id}")
            return {
                "task_id": task_id,
                "status": "deleted",
                "title": title,
            }
    except NotFoundError:
        logger.warning(f"delete_task: Task not found - id={task_id}, user_id={user_id}")
        return {"error": "Task not found"}
    except Exception as e:
        logger.error(f"delete_task error: {e}")
        return {"error": "Failed to delete task"}


@function_tool
def update_task(
    wrapper: RunContextWrapper[UserContext],
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Update a task's title or description.

    Args:
        task_id: The task ID to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        dict with task_id, status, and title
    """
    user_id = wrapper.context.user_id
    logger.info(f"update_task called: user_id={user_id}, task_id={task_id}")

    if title is not None and not title.strip():
        return {"error": "title cannot be empty"}

    if title is None and description is None:
        return {"error": "No updates provided"}

    try:
        with get_db_session() as session:
            service = TaskService(session, user_id)
            task_data = TaskUpdate(title=title, description=description)
            task = service.update_task(task_id, task_data)

            logger.info(f"Task updated via tool: id={task_id}, user_id={user_id}")
            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
            }
    except NotFoundError:
        logger.warning(f"update_task: Task not found - id={task_id}, user_id={user_id}")
        return {"error": "Task not found"}
    except ValueError as e:
        logger.warning(f"update_task validation error: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"update_task error: {e}")
        return {"error": "Failed to update task"}
