# [Task]: T014 [From]: data-model.md §Activity Log Entry
"""
ActivityLogEntry SQLModel for persisting task mutation events.
Entries are retained for 90 days (purge handled by ActivityService).
"""

from datetime import datetime
from typing import Any, Optional

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON


class ActivityLogEntry(SQLModel, table=True):
    """
    Records task mutation events for the activity log.

    Attributes:
        id: Unique entry identifier (auto-incrementing)
        user_id: Owner of the activity (references User.id)
        task_id: Reference to task (not FK — task may be deleted)
        event_type: Type of event (created/updated/completed/deleted)
        task_title: Snapshot of task title at event time
        task_data: Full task snapshot as JSON at event time
        created_at: When the event occurred
    """
    __tablename__ = "activity_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    task_id: int
    event_type: str = Field(max_length=20)
    task_title: str = Field(max_length=200)
    task_data: Any = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
