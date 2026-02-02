# [Task]: T037 [From]: plan.md §Phase B, data-model.md §Event Schemas
"""
Event publishing service using Dapr HTTP API.
Publishes CloudEvents to Kafka topics via Dapr sidecar (localhost:3500).
Gracefully degrades when Dapr sidecar is not available (local dev).
"""

import logging
import os
from typing import Any

import httpx

from ..models.events import CloudEvent

logger = logging.getLogger(__name__)

# Dapr sidecar HTTP port (default 3500)
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = "kafka-pubsub"

# Topics
TOPIC_TASK_EVENTS = "task-events"
TOPIC_REMINDERS = "reminders"
TOPIC_TASK_UPDATES = "task-updates"


class EventService:
    """Publishes events to Kafka via Dapr HTTP pub/sub API."""

    def __init__(self) -> None:
        self._enabled = os.getenv("DAPR_ENABLED", "false").lower() == "true"

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: str,
        task_data: dict[str, Any],
    ) -> None:
        """Publish a task mutation event to both task-events and task-updates topics."""
        if not self._enabled:
            logger.debug(
                "Dapr disabled — skipping event publish",
                extra={"task_id": task_id, "event_type": event_type, "user_id": user_id},
            )
            return

        # Publish to task-events (consumed by activity log + recurring task service)
        task_event = CloudEvent.task_event(event_type, task_id, user_id, task_data)
        await self._publish(TOPIC_TASK_EVENTS, task_event)

        # Publish to task-updates (consumed by notification service for real-time sync)
        sync_event = CloudEvent.task_update_event(event_type, user_id, task_data)
        await self._publish(TOPIC_TASK_UPDATES, sync_event)

    async def publish_reminder_event(
        self,
        task_id: int,
        title: str,
        due_at: str,
        remind_at: str,
        user_id: str,
    ) -> None:
        """Publish a reminder event to the reminders topic."""
        if not self._enabled:
            logger.debug(
                "Dapr disabled — skipping reminder publish",
                extra={"task_id": task_id, "user_id": user_id},
            )
            return

        event = CloudEvent.reminder_event(task_id, title, due_at, remind_at, user_id)
        await self._publish(TOPIC_REMINDERS, event)

    async def _publish(self, topic: str, event: CloudEvent) -> None:
        """POST event to Dapr pub/sub endpoint."""
        url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"
        log_extra = {"topic": topic, "event_type": event.type, "event_id": event.id}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    json=event.model_dump(),
                    headers={"Content-Type": "application/cloudevents+json"},
                )
                response.raise_for_status()
                logger.info("Event published", extra=log_extra)
        except httpx.ConnectError:
            logger.warning(
                "Dapr sidecar not reachable — event dropped",
                extra={**log_extra, "dapr_url": DAPR_BASE_URL},
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                "Dapr publish failed",
                extra={**log_extra, "status_code": e.response.status_code, "response_body": e.response.text},
            )
        except Exception:
            logger.exception("Unexpected error publishing event", extra=log_extra)
