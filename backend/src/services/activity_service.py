# [Task]: T063 [From]: plan.md §Phase C, data-model.md §Activity Log Entry
"""
Activity log service.
Persists task mutation events, queries activity entries, and purges old entries.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlmodel import Session, select, func, col

from ..models.activity_log import ActivityLogEntry

logger = logging.getLogger(__name__)

RETENTION_DAYS = 90


class ActivityService:
    """Service for activity log operations."""

    def __init__(self, session: Session):
        self.session = session

    def log_event(
        self,
        user_id: str,
        task_id: int,
        event_type: str,
        task_title: str,
        task_data: dict[str, Any],
    ) -> ActivityLogEntry:
        """Persist a task mutation event to the activity log."""
        entry = ActivityLogEntry(
            user_id=user_id,
            task_id=task_id,
            event_type=event_type,
            task_title=task_title,
            task_data=task_data,
        )
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)

        logger.info(
            "Activity logged: event=%s, task=%s, user=%s",
            event_type, task_id, user_id,
        )
        return entry

    def list_entries(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ActivityLogEntry], int]:
        """
        List activity log entries for a user with pagination.
        Returns (entries, total_count).
        """
        # Count total
        count_stmt = (
            select(func.count())
            .select_from(ActivityLogEntry)
            .where(ActivityLogEntry.user_id == user_id)
        )
        total = self.session.exec(count_stmt).one()

        # Fetch page
        stmt = (
            select(ActivityLogEntry)
            .where(ActivityLogEntry.user_id == user_id)
            .order_by(col(ActivityLogEntry.created_at).desc())
            .offset(offset)
            .limit(limit)
        )
        entries = list(self.session.exec(stmt).all())

        return entries, total

    def purge_old_entries(self) -> int:
        """Delete activity log entries older than RETENTION_DAYS. Returns count deleted."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
        stmt = select(ActivityLogEntry).where(ActivityLogEntry.created_at < cutoff)
        old_entries = list(self.session.exec(stmt).all())

        count = len(old_entries)
        for entry in old_entries:
            self.session.delete(entry)

        if count > 0:
            self.session.commit()
            logger.info("Purged %d activity log entries older than %d days", count, RETENTION_DAYS)

        return count
