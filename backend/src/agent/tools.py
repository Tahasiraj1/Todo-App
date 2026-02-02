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
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    due_date: Optional[str] = None,
    is_recurring: bool = False,
    recurrence_frequency: Optional[str] = None,
    recurrence_interval: int = 1,
    recurrence_day_of_week: Optional[int] = None,
    recurrence_day_of_month: Optional[int] = None,
) -> dict:
    """
    Add a new task for the user.

    Args:
        title: Task title (required, max 200 chars)
        description: Task description (optional, max 1000 chars)
        priority: Task priority - "high", "medium", or "low" (default: "medium")
        tags: List of tags for the task (e.g., ["work", "urgent"])
        due_date: Due date in ISO format (e.g., "2026-02-01T15:00:00Z")
        is_recurring: Whether the task repeats (default: false)
        recurrence_frequency: "daily", "weekly", or "monthly" (required if is_recurring)
        recurrence_interval: Repeat every N periods (default: 1)
        recurrence_day_of_week: 0-6 for Mon-Sun (weekly only)
        recurrence_day_of_month: 1-31 (monthly only)

    Returns:
        dict with task_id, status, title, and priority
    """
    user_id = wrapper.context.user_id
    logger.info(f"add_task called: user_id={user_id}, title={title}, priority={priority}")

    if not title or not title.strip():
        return {"error": "title is required"}

    if len(title) > 200:
        return {"error": "title exceeds maximum length"}

    try:
        from datetime import datetime as dt

        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = dt.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                return {"error": f"Invalid due_date format: {due_date}"}

        with get_db_session() as session:
            service = TaskService(session, user_id)
            task_data = TaskCreate(
                title=title.strip(),
                description=description,
                priority=priority or "medium",
                tags=tags or [],
                due_date=parsed_due_date,
                is_recurring=is_recurring,
                recurrence_frequency=recurrence_frequency,
                recurrence_interval=recurrence_interval,
                recurrence_day_of_week=recurrence_day_of_week,
                recurrence_day_of_month=recurrence_day_of_month,
            )
            task = service.create_task(task_data)

            logger.info(f"Task created via tool: id={task.id}, user_id={user_id}")
            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
                "priority": task.priority,
                "tags": task.tags,
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
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> list[dict]:
    """
    List tasks for the user with optional filtering, sorting, and search.

    Args:
        status: Filter by status - "all", "pending", or "completed" (default: "all")
        priority: Filter by priority - "high", "medium", or "low"
        tag: Filter by tag (exact match)
        search: Search keyword across title and description
        sort_by: Sort field - "due_date", "priority", "title", or "created_at"
        sort_order: Sort direction - "asc" or "desc" (default: "desc")

    Returns:
        List of task objects with id, title, completed, priority, tags, due_date, and description
    """
    user_id = wrapper.context.user_id
    filter_status = status or "all"
    logger.info(f"list_tasks called: user_id={user_id}, status={filter_status}, priority={priority}, search={search}")

    try:
        with get_db_session() as session:
            service = TaskService(session, user_id)
            tasks = service.list_tasks(
                status=filter_status if filter_status != "all" else None,
                priority=priority,
                tag=tag,
                search=search,
                sort_by=sort_by or "created_at",
                sort_order=sort_order or "desc",
            )

            logger.info(f"Listed {len(tasks)} tasks for user_id={user_id}")
            return [
                {
                    "id": t.id,
                    "title": t.title,
                    "completed": t.completed,
                    "description": t.description,
                    "priority": t.priority,
                    "tags": t.tags,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "is_recurring": t.is_recurring,
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
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    due_date: Optional[str] = None,
    is_recurring: Optional[bool] = None,
    recurrence_frequency: Optional[str] = None,
    recurrence_interval: Optional[int] = None,
    recurrence_day_of_week: Optional[int] = None,
    recurrence_day_of_month: Optional[int] = None,
) -> dict:
    """
    Update a task's details.

    Args:
        task_id: The task ID to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority - "high", "medium", or "low" (optional)
        tags: New list of tags (optional)
        due_date: New due date in ISO format (optional)
        is_recurring: Whether the task repeats (optional)
        recurrence_frequency: "daily", "weekly", or "monthly" (optional)
        recurrence_interval: Repeat every N periods (optional)
        recurrence_day_of_week: 0-6 for Mon-Sun (optional)
        recurrence_day_of_month: 1-31 (optional)

    Returns:
        dict with task_id, status, title, and priority
    """
    user_id = wrapper.context.user_id
    logger.info(f"update_task called: user_id={user_id}, task_id={task_id}")

    if title is not None and not title.strip():
        return {"error": "title cannot be empty"}

    has_updates = any(v is not None for v in [
        title, description, priority, tags, due_date,
        is_recurring, recurrence_frequency, recurrence_interval,
        recurrence_day_of_week, recurrence_day_of_month,
    ])
    if not has_updates:
        return {"error": "No updates provided"}

    try:
        from datetime import datetime as dt

        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = dt.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                return {"error": f"Invalid due_date format: {due_date}"}

        with get_db_session() as session:
            service = TaskService(session, user_id)
            task_data = TaskUpdate(
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=parsed_due_date,
                is_recurring=is_recurring,
                recurrence_frequency=recurrence_frequency,
                recurrence_interval=recurrence_interval,
                recurrence_day_of_week=recurrence_day_of_week,
                recurrence_day_of_month=recurrence_day_of_month,
            )
            task = service.update_task(task_id, task_data)

            logger.info(f"Task updated via tool: id={task_id}, user_id={user_id}")
            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
                "priority": task.priority,
                "tags": task.tags,
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
