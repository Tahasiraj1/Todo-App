# [Task]: T039, T040, T041, T057, T069, T078, T102 [From]: plan.md §Project Structure
"""
Task service for business logic operations.
All operations filter by user_id for data isolation.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from ..middleware.error_handler import NotFoundError
from ..models.task import Task
from ..models.schemas import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


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
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        logger.info(f"Task created: id={task.id}, user_id={self.user_id}")
        return task

    def list_tasks(self) -> list[Task]:
        """
        List all tasks for the authenticated user.

        Returns:
            List of tasks belonging to the user
        """
        statement = select(Task).where(Task.user_id == self.user_id)
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

        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        logger.info(f"Task updated: id={task_id}, user_id={self.user_id}")
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

        logger.info(
            f"Task completion toggled: id={task_id}, completed={task.completed}, "
            f"user_id={self.user_id}"
        )
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
        self.session.delete(task)
        self.session.commit()

        logger.info(f"Task deleted: id={task_id}, user_id={self.user_id}")
