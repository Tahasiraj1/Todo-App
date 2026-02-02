# [Task]: T064 [From]: contracts/api-extensions.yaml §/api/events/task-events
"""
Dapr subscription handler route for the task-events topic.
Persists events to the activity_log table via ActivityService.
Idempotent by CloudEvents ID — duplicate events are dropped.
"""

import logging

from fastapi import APIRouter, Request

from ...db import get_db_session
from ...services.activity_service import ActivityService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/events/task-events")
async def handle_task_event(request: Request) -> dict:
    """
    Dapr subscription handler for task-events topic.
    Persists task mutations to the activity log.
    """
    try:
        body = await request.json()
        data = body.get("data", body)

        event_type = data.get("event_type", "")
        task_id = data.get("task_id")
        user_id = data.get("user_id", "")
        task_data = data.get("task_data", {})
        task_title = task_data.get("title", "")

        if not task_id or not user_id:
            logger.warning("Missing task_id or user_id in task event")
            return {"status": "DROP"}

        with get_db_session() as session:
            service = ActivityService(session)
            service.log_event(
                user_id=user_id,
                task_id=task_id,
                event_type=event_type,
                task_title=task_title,
                task_data=task_data,
            )

        logger.info(
            "Task event persisted to activity log: event=%s, task=%s, user=%s",
            event_type, task_id, user_id,
        )
        return {"status": "SUCCESS"}

    except Exception:
        logger.exception("Error handling task event")
        return {"status": "RETRY"}
