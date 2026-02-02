# [Task]: T076 [From]: plan.md §Phase C, data-model.md §Event Schemas
"""
Notification service Dapr subscription handlers.
- reminders topic → forward to user's WebSocket as reminder notification
- task-updates topic → forward to user's WebSocket as task update
Uses Dapr service invocation to call backend's WebSocket broadcast endpoint.
"""

import logging
import os

import httpx
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)
router = APIRouter()

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
BACKEND_APP_ID = os.getenv("BACKEND_APP_ID", "todo-backend")
BACKEND_URL = os.getenv("BACKEND_URL", "http://todo-backend:8000")


async def _forward_to_backend_ws(user_id: str, message: dict) -> None:
    """
    Forward a message to the backend for WebSocket broadcast.
    Uses Dapr service invocation if available, falls back to direct HTTP.
    """
    # Try Dapr service invocation first
    dapr_url = f"{DAPR_BASE_URL}/v1.0/invoke/{BACKEND_APP_ID}/method/api/internal/ws-broadcast"
    payload = {"user_id": user_id, "message": message}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(dapr_url, json=payload)
            response.raise_for_status()
            logger.debug("Forwarded to backend via Dapr: user=%s", user_id)
            return
    except Exception:
        logger.debug("Dapr invocation failed, trying direct HTTP")

    # Fallback: direct HTTP to backend
    direct_url = f"{BACKEND_URL}/api/internal/ws-broadcast"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(direct_url, json=payload)
            response.raise_for_status()
            logger.debug("Forwarded to backend via direct HTTP: user=%s", user_id)
    except Exception:
        logger.warning("Failed to forward message to backend for user=%s", user_id)


@router.post("/api/events/reminders")
async def handle_reminder_event(request: Request) -> dict:
    """Handle reminder events — forward to user's WebSocket."""
    try:
        body = await request.json()
        data = body.get("data", body)

        user_id = data.get("user_id", "")
        if not user_id:
            return {"status": "DROP"}

        ws_message = {
            "type": "reminder",
            "payload": {
                "task_id": data.get("task_id"),
                "title": data.get("title", ""),
                "due_at": data.get("due_at", ""),
                "remind_at": data.get("remind_at", ""),
            },
        }

        await _forward_to_backend_ws(user_id, ws_message)

        logger.info(
            "Reminder forwarded",
            extra={"topic": "reminders", "task_id": data.get("task_id"), "user_id": user_id},
        )
        return {"status": "SUCCESS"}

    except Exception:
        logger.exception("Error handling reminder event", extra={"topic": "reminders"})
        return {"status": "RETRY"}


@router.post("/api/events/task-updates")
async def handle_task_update_event(request: Request) -> dict:
    """Handle task-update events — forward to user's WebSocket for real-time sync."""
    try:
        body = await request.json()
        data = body.get("data", body)

        user_id = data.get("user_id", "")
        if not user_id:
            return {"status": "DROP"}

        ws_message = {
            "type": "task_update",
            "payload": {
                "action": data.get("action", ""),
                "task": data.get("task", {}),
            },
        }

        await _forward_to_backend_ws(user_id, ws_message)

        logger.info(
            "Task update forwarded",
            extra={"topic": "task-updates", "action": data.get("action"), "user_id": user_id},
        )
        return {"status": "SUCCESS"}

    except Exception:
        logger.exception("Error handling task-update event", extra={"topic": "task-updates"})
        return {"status": "RETRY"}
