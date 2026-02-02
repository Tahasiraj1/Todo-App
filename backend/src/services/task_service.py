# [Task]: T039, T040, T041, T057, T069, T078, T102, T016, T017, T025, T038 [From]: plan.md §Project Structure
"""
Task service for business logic operations.
All operations filter by user_id for data isolation.
Phase V: priority, tags, due_date, recurrence, filter/sort/search, event publishing.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import cast, String
from sqlmodel import Session, select, or_

from ..middleware.error_handler import NotFoundError
from ..models.task import Task
from ..models.schemas import TaskCreate, TaskUpdate
from .event_service import EventService
from .reminder_service import ReminderService

logger = logging.getLogger(__name__)

# Shared service instances
_event_service = EventService()
_reminder_service = ReminderService()


def _task_to_dict(task: Task) -> dict[str, Any]:
    """Serialize a Task to a dict for event payloads."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "tags": task.tags or [],
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "is_recurring": task.is_recurring,
        "recurrence_frequency": task.recurrence_frequency,
        "recurrence_interval": task.recurrence_interval,
    }


def _fire_event(event_type: str, task_id: int, user_id: str, task_data: dict[str, Any]) -> None:
    """Fire an event asynchronously without blocking the sync caller."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_event_service.publish_task_event(event_type, task_id, user_id, task_data))
    except RuntimeError:
        # No running event loop (e.g. during tests) — skip
        logger.debug("No event loop — skipping event publish for task %s", task_id)


def _schedule_reminder(task: Task) -> None:
    """Schedule a Dapr Jobs reminder if the task has a due_date."""
    if not task.due_date:
        return
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            _reminder_service.schedule_reminder(task.id, task.user_id, task.title, task.due_date)
        )
    except RuntimeError:
        logger.debug("No event loop — skipping reminder schedule for task %s", task.id)


def _cancel_reminder(task_id: int) -> None:
    """Cancel a Dapr Jobs reminder."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_reminder_service.cancel_reminder(task_id))
    except RuntimeError:
        logger.debug("No event loop — skipping reminder cancel for task %s", task_id)


class TaskService:
    """Service class for task operations."""

    def __init__(self, session: Session, user_id: str):
        """
        Initialize TaskService.

        Args:
            session: SQLModel database session
            user_id: Authenticated user's ID
        """
        self.session = session
        self.user_id = user_id

    def create_task(self, task_data: TaskCreate) -> Task:
        """
        Create a new task for the authenticated user.

        Args:
            task_data: Task creation data

        Returns:
            The created task
        """
        task = Task(
            user_id=self.user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            tags=task_data.tags,
            due_date=task_data.due_date,
            is_recurring=task_data.is_recurring,
            recurrence_frequency=task_data.recurrence_frequency,
            recurrence_interval=task_data.recurrence_interval,
            recurrence_day_of_week=task_data.recurrence_day_of_week,
            recurrence_day_of_month=task_data.recurrence_day_of_month,
            recurrence_end_date=task_data.recurrence_end_date,
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        logger.info(f"Task created: id={task.id}, user_id={self.user_id}, priority={task.priority}")
        _fire_event("created", task.id, self.user_id, _task_to_dict(task))
        _schedule_reminder(task)
        return task

    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        overdue: Optional[bool] = None,
    ) -> list[Task]:
        """
        List tasks for the authenticated user with optional filtering, sorting, and search.

        Args:
            status: Filter by status (all/pending/completed)
            priority: Filter by priority (high/medium/low)
            tag: Filter by tag (exact match in JSON array)
            search: Keyword search across title and description (ILIKE)
            sort_by: Sort field (due_date/priority/title/created_at)
            sort_order: Sort direction (asc/desc)
            overdue: Filter to overdue tasks only

        Returns:
            Filtered and sorted list of tasks
        """
        statement = select(Task).where(Task.user_id == self.user_id)

        # Status filter
        if status == "pending":
            statement = statement.where(Task.completed == False)  # noqa: E712
        elif status == "completed":
            statement = statement.where(Task.completed == True)  # noqa: E712

        # Priority filter
        if priority and priority in ("high", "medium", "low"):
            statement = statement.where(Task.priority == priority)

        # Tag filter (cast JSON array to text and match quoted tag)
        if tag:
            statement = statement.where(
                cast(Task.tags, String).contains(f'"{tag}"')
            )

        # Keyword search
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    Task.title.ilike(pattern),
                    Task.description.ilike(pattern),
                )
            )

        # Overdue filter
        if overdue:
            statement = statement.where(
                Task.due_date != None,  # noqa: E711
                Task.due_date < datetime.utcnow(),
                Task.completed == False,  # noqa: E712
            )

        # Sorting
        sort_column_map = {
            "due_date": Task.due_date,
            "priority": Task.priority,
            "title": Task.title,
            "created_at": Task.created_at,
        }
        sort_col = sort_column_map.get(sort_by, Task.created_at)
        if sort_order == "asc":
            statement = statement.order_by(sort_col.asc())
        else:
            statement = statement.order_by(sort_col.desc())

        tasks = self.session.exec(statement).all()

        logger.debug(f"Listed {len(tasks)} tasks for user_id={self.user_id}")
        return list(tasks)

    def get_task(self, task_id: int) -> Task:
        """
        Get a specific task by ID.

        Args:
            task_id: The task ID

        Returns:
            The task if found and belongs to user

        Raises:
            NotFoundError: If task not found or doesn't belong to user
        """
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == self.user_id,
        )
        task = self.session.exec(statement).first()

        if not task:
            logger.warning(
                f"Task not found: id={task_id}, user_id={self.user_id}"
            )
            raise NotFoundError("Task not found")

        return task

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Task:
        """
        Update a task.

        Args:
            task_id: The task ID
            task_data: Update data

        Returns:
            The updated task

        Raises:
            NotFoundError: If task not found or doesn't belong to user
        """
        task = self.get_task(task_id)

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.tags is not None:
            task.tags = task_data.tags
        if task_data.due_date is not None:
            # Reset reminder_sent when due_date changes
            if task_data.due_date != task.due_date:
                task.reminder_sent = False
            task.due_date = task_data.due_date
        if task_data.is_recurring is not None:
            task.is_recurring = task_data.is_recurring
        if task_data.recurrence_frequency is not None:
            task.recurrence_frequency = task_data.recurrence_frequency
        if task_data.recurrence_interval is not None:
            task.recurrence_interval = task_data.recurrence_interval
        if task_data.recurrence_day_of_week is not None:
            task.recurrence_day_of_week = task_data.recurrence_day_of_week
        if task_data.recurrence_day_of_month is not None:
            task.recurrence_day_of_month = task_data.recurrence_day_of_month
        if task_data.recurrence_end_date is not None:
            task.recurrence_end_date = task_data.recurrence_end_date

        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        logger.info(f"Task updated: id={task_id}, user_id={self.user_id}")
        _fire_event("updated", task.id, self.user_id, _task_to_dict(task))
        # Reschedule reminder if due_date changed
        if task_data.due_date is not None:
            _schedule_reminder(task)
        return task

    def toggle_task_completion(self, task_id: int) -> Task:
        """
        Toggle the completion status of a task.

        Args:
            task_id: The task ID

        Returns:
            The updated task

        Raises:
            NotFoundError: If task not found or doesn't belong to user
        """
        task = self.get_task(task_id)
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        event_type = "completed" if task.completed else "updated"
        logger.info(
            f"Task completion toggled: id={task_id}, completed={task.completed}, "
            f"user_id={self.user_id}"
        )
        _fire_event(event_type, task.id, self.user_id, _task_to_dict(task))
        return task

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task.

        Args:
            task_id: The task ID

        Raises:
            NotFoundError: If task not found or doesn't belong to user
        """
        task = self.get_task(task_id)
        task_data = _task_to_dict(task)
        self.session.delete(task)
        self.session.commit()

        logger.info(f"Task deleted: id={task_id}, user_id={self.user_id}")
        _fire_event("deleted", task_id, self.user_id, task_data)
        _cancel_reminder(task_id)
