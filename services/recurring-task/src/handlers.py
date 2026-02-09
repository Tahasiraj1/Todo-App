# [Task]: T058 [From]: plan.md §Phase C, data-model.md §State Transitions
"""
Dapr subscription handler for task-completed events.
Computes the next due date from recurrence rules and creates
the next task occurrence via Dapr service invocation to the backend.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)
router = APIRouter()

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
BACKEND_APP_ID = os.getenv("BACKEND_APP_ID", "todo-backend")


def compute_next_due_date(
    current_due: datetime,
    frequency: str,
    interval: int = 1,
    day_of_week: Optional[int] = None,
    day_of_month: Optional[int] = None,
) -> datetime:
    """
    Compute the next due date based on recurrence rules.

    Args:
        current_due: The current due date
        frequency: daily, weekly, or monthly
        interval: Every N periods (default 1)
        day_of_week: 0-6 for Mon-Sun (weekly)
        day_of_month: 1-31 (monthly)

    Returns:
        The next due date
    """
    if frequency == "daily":
        return current_due + timedelta(days=interval)

    elif frequency == "weekly":
        next_date = current_due + timedelta(weeks=interval)
        if day_of_week is not None:
            # Adjust to the specified day of week
            current_day = next_date.weekday()
            diff = day_of_week - current_day
            if diff <= 0:
                diff += 7
            next_date = current_due + timedelta(days=diff)
            if next_date <= current_due:
                next_date += timedelta(weeks=interval)
        return next_date

    elif frequency == "monthly":
        month = current_due.month + interval
        year = current_due.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        day = day_of_month or current_due.day
        # Clamp day to valid range for the month
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        day = min(day, max_day)
        return current_due.replace(year=year, month=month, day=day)

    else:
        # Default: add 1 day
        logger.warning("Unknown recurrence frequency: %s, defaulting to daily", frequency)
        return current_due + timedelta(days=1)


@router.post("/api/events/task-completed")
async def handle_task_completed(request: Request) -> dict:
    """
    Handle task-completed events from the task-events topic.
    If the completed task is recurring, create the next occurrence.
    """
    try:
        body = await request.json()

        # Dapr wraps the message in a CloudEvents envelope
        data = body.get("data", body)
        event_type = data.get("event_type", "")

        # Only process completed events
        if event_type != "completed":
            return {"status": "SUCCESS"}

        task_data: dict[str, Any] = data.get("task_data", {})
        user_id = data.get("user_id", "")

        # Check if the task is recurring
        if not task_data.get("is_recurring"):
            return {"status": "SUCCESS"}

        frequency = task_data.get("recurrence_frequency")
        if not frequency:
            logger.warning("Recurring task %s has no frequency, skipping", task_data.get("id"))
            return {"status": "SUCCESS"}

        # Compute next due date
        due_date_str = task_data.get("due_date")
        if due_date_str:
            current_due = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        else:
            current_due = datetime.now(timezone.utc)

        next_due = compute_next_due_date(
            current_due=current_due,
            frequency=frequency,
            interval=task_data.get("recurrence_interval", 1),
            day_of_week=task_data.get("recurrence_day_of_week"),
            day_of_month=task_data.get("recurrence_day_of_month"),
        )

        # Check recurrence_end_date
        end_date_str = task_data.get("recurrence_end_date")
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            if next_due > end_date:
                logger.info(
                    "Recurring task %s past end date, not creating next occurrence",
                    task_data.get("id"),
                )
                return {"status": "SUCCESS"}

        # Create next task occurrence via Dapr service invocation
        new_task = {
            "title": task_data.get("title", ""),
            "description": task_data.get("description"),
            "priority": task_data.get("priority", "medium"),
            "tags": task_data.get("tags", []),
            "due_date": next_due.isoformat(),
            "is_recurring": True,
            "recurrence_frequency": frequency,
            "recurrence_interval": task_data.get("recurrence_interval", 1),
            "recurrence_day_of_week": task_data.get("recurrence_day_of_week"),
            "recurrence_day_of_month": task_data.get("recurrence_day_of_month"),
            "recurrence_end_date": end_date_str,
        }

        invoke_url = (
            f"{DAPR_BASE_URL}/v1.0/invoke/{BACKEND_APP_ID}/method"
            f"/api/internal/create-task"
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(invoke_url, json={"user_id": user_id, "task": new_task})
            response.raise_for_status()

        logger.info(
            "Created next recurring task",
            extra={
                "topic": "task-events",
                "original_task_id": task_data.get("id"),
                "next_due": next_due.isoformat(),
                "frequency": frequency,
                "user_id": user_id,
            },
        )
        return {"status": "SUCCESS"}

    except httpx.HTTPStatusError as e:
        logger.error(
            "Failed to create next recurring task",
            extra={"status_code": e.response.status_code, "response_body": e.response.text},
        )
        return {"status": "RETRY"}
    except Exception:
        logger.exception("Error handling task-completed event", extra={"topic": "task-events"})
        return {"status": "RETRY"}
