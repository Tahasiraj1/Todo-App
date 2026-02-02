# [Task]: T074 [From]: contracts/api-extensions.yaml §/api/ws/{user_id}
"""
WebSocket endpoint for real-time task updates and reminders.
Clients connect per user_id. Server pushes task update and reminder messages.
"""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time updates.
    Messages sent to the client are JSON with format:
    {"type": "task_update" | "reminder", "payload": {...}}
    """
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            # Keep the connection alive; receive and discard client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
    except Exception:
        ws_manager.disconnect(websocket, user_id)
