# [Task]: T073 [From]: plan.md §Phase C, contracts/api-extensions.yaml §WebSocket
"""
WebSocket connection manager.
Tracks connections per user_id, broadcasts messages, handles cleanup.
"""

import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections per user."""

    def __init__(self) -> None:
        # user_id → set of active WebSocket connections
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(websocket)
        logger.info("WebSocket connected: user=%s, total=%d", user_id, len(self._connections[user_id]))

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Remove a WebSocket connection."""
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                del self._connections[user_id]
        logger.info("WebSocket disconnected: user=%s", user_id)

    async def broadcast_to_user(self, user_id: str, message: dict[str, Any]) -> None:
        """Send a message to all of a user's connected WebSocket clients."""
        connections = self._connections.get(user_id, set())
        if not connections:
            logger.info("No WebSocket connections for user=%s, message dropped", user_id)
            return
        logger.info("Broadcasting to user=%s, connections=%d, type=%s", user_id, len(connections), message.get("type", "unknown"))

        payload = json.dumps(message)
        dead_connections = set()

        for ws in connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead_connections.add(ws)

        # Clean up dead connections
        for ws in dead_connections:
            self.disconnect(ws, user_id)

    def get_connection_count(self, user_id: str | None = None) -> int:
        """Get the number of active connections (for a user or total)."""
        if user_id:
            return len(self._connections.get(user_id, set()))
        return sum(len(conns) for conns in self._connections.values())


# Shared instance
ws_manager = WebSocketManager()
