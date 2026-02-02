# [Task]: T042, T043, T044, T045, T058, T059, T060, T070, T071, T079, T080, T024 [From]: contracts/api-endpoints.md
"""
Task API routes.
All endpoints require JWT authentication and validate user_id from URL matches JWT.
Endpoint pattern: /api/{user_id}/tasks (per hackathon requirements)
Phase V: filter, sort, search query parameters on list endpoint.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from ..dependencies import CurrentUserId, DbSession
from ...models.schemas import (
    MessageResponse,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from ...services.task_service import TaskService

router = APIRouter()


def validate_user_id(path_user_id: str, jwt_user_id: str) -> None:
    """
    Validate that the user_id in the URL path matches the user_id from JWT token.
    This ensures users can only access their own tasks even if they manipulate URLs.

    Args:
        path_user_id: The user_id from the URL path
        jwt_user_id: The user_id extracted from the JWT token

    Raises:
        HTTPException: 403 Forbidden if user_ids don't match
    """
    if path_user_id != jwt_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own tasks"
        )


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user_id: str,
    session: DbSession,
    jwt_user_id: CurrentUserId,
    status: Optional[str] = Query(None, enum=["all", "pending", "completed"]),
    priority: Optional[str] = Query(None, enum=["high", "medium", "low"]),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    sort_by: str = Query("created_at", enum=["due_date", "priority", "title", "created_at"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    overdue: Optional[bool] = Query(None),
) -> TaskListResponse:
    """
    List tasks for the authenticated user with optional filtering, sorting, and search.
    GET /api/{user_id}/tasks

    Args:
        user_id: User ID from URL path (must match JWT token)
        status: Filter by status (all/pending/completed)
        priority: Filter by priority (high/medium/low)
        tag: Filter by tag (exact match)
        search: Keyword search across title and description
        sort_by: Sort field (due_date/priority/title/created_at)
        sort_order: Sort direction (asc/desc)
        overdue: Filter to overdue tasks only

    Returns:
        TaskListResponse: Filtered and sorted list of tasks
    """
    validate_user_id(user_id, jwt_user_id)
    service = TaskService(session, user_id)
    tasks = service.list_tasks(
        status=status if status and status != "all" else None,
        priority=priority,
        tag=tag,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        overdue=overdue,
    )
    return TaskListResponse(tasks=[TaskResponse.model_validate(t) for t in tasks])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    session: DbSession,
    jwt_user_id: CurrentUserId,
) -> TaskResponse:
    """
    Create a new task for the authenticated user.
    POST /api/{user_id}/tasks

    Args:
        user_id: User ID from URL path (must match JWT token)
        task_data: Task creation data (title required, description optional)

    Returns:
        TaskResponse: The created task
    """
    validate_user_id(user_id, jwt_user_id)
    service = TaskService(session, user_id)
    task = service.create_task(task_data)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    session: DbSession,
    jwt_user_id: CurrentUserId,
) -> TaskResponse:
    """
    Get a specific task by ID.
    GET /api/{user_id}/tasks/{task_id}

    Args:
        user_id: User ID from URL path (must match JWT token)
        task_id: The task ID

    Returns:
        TaskResponse: The task if found and belongs to user
    """
    validate_user_id(user_id, jwt_user_id)
    service = TaskService(session, user_id)
    task = service.get_task(task_id)
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    session: DbSession,
    jwt_user_id: CurrentUserId,
) -> TaskResponse:
    """
    Update a task.
    PUT /api/{user_id}/tasks/{task_id}

    Args:
        user_id: User ID from URL path (must match JWT token)
        task_id: The task ID
        task_data: Update data (title and/or description)

    Returns:
        TaskResponse: The updated task
    """
    validate_user_id(user_id, jwt_user_id)
    service = TaskService(session, user_id)
    task = service.update_task(task_id, task_data)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    user_id: str,
    task_id: int,
    session: DbSession,
    jwt_user_id: CurrentUserId,
) -> MessageResponse:
    """
    Delete a task.
    DELETE /api/{user_id}/tasks/{task_id}

    Args:
        user_id: User ID from URL path (must match JWT token)
        task_id: The task ID

    Returns:
        MessageResponse: Success message
    """
    validate_user_id(user_id, jwt_user_id)
    service = TaskService(session, user_id)
    service.delete_task(task_id)
    return MessageResponse(message="Task deleted successfully")


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    session: DbSession,
    jwt_user_id: CurrentUserId,
) -> TaskResponse:
    """
    Toggle the completion status of a task.
    PATCH /api/{user_id}/tasks/{task_id}/complete

    Args:
        user_id: User ID from URL path (must match JWT token)
        task_id: The task ID

    Returns:
        TaskResponse: The updated task with toggled completion status
    """
    validate_user_id(user_id, jwt_user_id)
    service = TaskService(session, user_id)
    task = service.toggle_task_completion(task_id)
    return TaskResponse.model_validate(task)
