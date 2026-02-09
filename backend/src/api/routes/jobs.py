# [Task]: T048 [From]: contracts/api-extensions.yaml §/api/jobs/{job_name}
"""
Dapr Jobs callback route handler.
Called by the Dapr sidecar when a scheduled job fires.
Publishes reminder events to the reminders Kafka topic.
"""

import logging

from fastapi import APIRouter, Request

from ...services.event_service import EventService

logger = logging.getLogger(__name__)
router = APIRouter()

_event_service = EventService()


@router.post("/job/{job_name}")
async def handle_job_callback(job_name: str, request: Request) -> dict:
    """
    Dapr Jobs callback endpoint (POST /job/<name>).
    When a scheduled reminder fires, publish to the reminders topic.
    """
    try:
        body = await request.json()

        # Dapr Jobs sends payload as base64-encoded "Payload" field
        import base64, json as _json
        if "Payload" in body:
            raw = base64.b64decode(body["Payload"])
            data = _json.loads(raw)
        else:
            data = body.get("data", body)

        job_type = data.get("type")
        if job_type != "reminder":
            logger.warning("Unknown job type: %s for job %s", job_type, job_name)
            return {"status": "DROP"}

        task_id = data.get("task_id")
        user_id = data.get("user_id")
        title = data.get("title", "")
        due_at = data.get("due_at", "")
        remind_at = data.get("remind_at", "")

        if not task_id or not user_id:
            logger.error("Missing task_id or user_id in job callback: %s", job_name)
            return {"status": "DROP"}

        # Publish reminder event to Kafka
        await _event_service.publish_reminder_event(
            task_id=task_id,
            title=title,
            due_at=due_at,
            remind_at=remind_at,
            user_id=user_id,
        )

        logger.info(
            "Reminder job fired: job=%s, task=%s, user=%s",
            job_name, task_id, user_id,
        )
        return {"status": "SUCCESS"}

    except Exception:
        logger.exception("Error processing job callback: %s", job_name)
        return {"status": "RETRY"}
