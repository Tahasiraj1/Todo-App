# [Task]: T047 [From]: plan.md §Phase C, data-model.md §Reminder Lifecycle
"""
Reminder scheduling service using Dapr Jobs API.
Schedules reminders 30 minutes before task due dates.
Cancels/reschedules when due_date changes.
"""

import logging
import os
from datetime import datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
REMINDER_OFFSET_MINUTES = 30


class ReminderService:
    """Schedules and cancels task reminders via Dapr Jobs API."""

    def __init__(self) -> None:
        self._enabled = os.getenv("DAPR_ENABLED", "false").lower() == "true"

    def _job_name(self, task_id: int) -> str:
        return f"reminder-task-{task_id}"

    async def schedule_reminder(
        self,
        task_id: int,
        user_id: str,
        title: str,
        due_date: datetime,
    ) -> None:
        """Schedule a reminder 30 minutes before due_date via Dapr Jobs."""
        if not self._enabled:
            logger.debug("Dapr disabled — skipping reminder schedule for task %s", task_id)
            return

        remind_at = due_date - timedelta(minutes=REMINDER_OFFSET_MINUTES)
        now = datetime.now(timezone.utc)

        # If remind_at is in the past, skip scheduling
        if remind_at <= now:
            logger.info("Reminder time already passed for task %s, skipping", task_id)
            return

        job_name = self._job_name(task_id)
        url = f"{DAPR_BASE_URL}/v1.0-alpha1/jobs/{job_name}"

        payload = {
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "title": title,
                "due_at": due_date.isoformat(),
                "remind_at": remind_at.isoformat(),
                "type": "reminder",
            },
            "dueTime": remind_at.isoformat(),
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info(
                    "Reminder scheduled: task=%s, remind_at=%s, job=%s",
                    task_id, remind_at.isoformat(), job_name,
                )
        except httpx.ConnectError:
            logger.warning("Dapr sidecar not reachable — reminder not scheduled for task %s", task_id)
        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to schedule reminder: task=%s, status=%s, body=%s",
                task_id, e.response.status_code, e.response.text,
            )
        except Exception:
            logger.exception("Unexpected error scheduling reminder for task %s", task_id)

    async def cancel_reminder(self, task_id: int) -> None:
        """Cancel a scheduled reminder via Dapr Jobs."""
        if not self._enabled:
            return

        job_name = self._job_name(task_id)
        url = f"{DAPR_BASE_URL}/v1.0-alpha1/jobs/{job_name}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.delete(url)
                if response.status_code == 404:
                    logger.debug("No existing reminder to cancel for task %s", task_id)
                    return
                response.raise_for_status()
                logger.info("Reminder cancelled: task=%s, job=%s", task_id, job_name)
        except httpx.ConnectError:
            logger.warning("Dapr sidecar not reachable — reminder cancel skipped for task %s", task_id)
        except Exception:
            logger.exception("Unexpected error cancelling reminder for task %s", task_id)

    async def reschedule_reminder(
        self,
        task_id: int,
        user_id: str,
        title: str,
        new_due_date: datetime,
    ) -> None:
        """Cancel existing reminder and schedule a new one."""
        await self.cancel_reminder(task_id)
        await self.schedule_reminder(task_id, user_id, title, new_due_date)
