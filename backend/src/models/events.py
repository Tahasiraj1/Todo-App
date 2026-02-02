# [Task]: T013 [From]: data-model.md §Event Schemas
"""
CloudEvents-compatible event schema models for Dapr pub/sub.
Used for publishing and consuming events across Kafka topics.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class TaskEventData(BaseModel):
    """Data payload for task mutation events on the task-events topic."""
    event_type: Literal["created", "updated", "completed", "deleted"]
    task_id: int
    user_id: str
    task_data: dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReminderEventData(BaseModel):
    """Data payload for reminder events on the reminders topic."""
    task_id: int
    title: str
    due_at: str
    remind_at: str
    user_id: str


class TaskUpdateEventData(BaseModel):
    """Data payload for real-time sync events on the task-updates topic."""
    action: Literal["created", "updated", "completed", "deleted"]
    user_id: str
    task: dict[str, Any]


class CloudEvent(BaseModel):
    """CloudEvents v1.0 envelope used by Dapr pub/sub."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    specversion: str = "1.0"
    type: str
    source: str
    time: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: dict[str, Any]
    topic: Optional[str] = None
    pubsubname: Optional[str] = None

    @classmethod
    def task_event(
        cls,
        event_type: str,
        task_id: int,
        user_id: str,
        task_data: dict[str, Any],
    ) -> "CloudEvent":
        """Create a TaskEvent CloudEvents envelope."""
        type_map = {
            "created": "com.todo.task.created",
            "updated": "com.todo.task.updated",
            "completed": "com.todo.task.completed",
            "deleted": "com.todo.task.deleted",
        }
        return cls(
            type=type_map.get(event_type, f"com.todo.task.{event_type}"),
            source="/api/tasks",
            data=TaskEventData(
                event_type=event_type,
                task_id=task_id,
                user_id=user_id,
                task_data=task_data,
            ).model_dump(),
        )

    @classmethod
    def reminder_event(
        cls,
        task_id: int,
        title: str,
        due_at: str,
        remind_at: str,
        user_id: str,
    ) -> "CloudEvent":
        """Create a ReminderEvent CloudEvents envelope."""
        return cls(
            type="com.todo.reminder.due",
            source="/api/jobs",
            data=ReminderEventData(
                task_id=task_id,
                title=title,
                due_at=due_at,
                remind_at=remind_at,
                user_id=user_id,
            ).model_dump(),
        )

    @classmethod
    def task_update_event(
        cls,
        action: str,
        user_id: str,
        task: dict[str, Any],
    ) -> "CloudEvent":
        """Create a TaskUpdateEvent for real-time sync."""
        return cls(
            type="com.todo.task.sync",
            source="/api/tasks",
            data=TaskUpdateEventData(
                action=action,
                user_id=user_id,
                task=task,
            ).model_dump(),
        )
