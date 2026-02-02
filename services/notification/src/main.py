# [Task]: T075 [From]: plan.md §Phase C, contracts/dapr-components.yaml
"""
Notification Service — FastAPI app subscribing to reminders and task-updates topics.
Forwards events to the backend's WebSocket endpoint via Dapr service invocation.
"""

import logging
import os
import sys

from fastapi import FastAPI

from .handlers import router as handlers_router

# Configure structured JSON logging for production observability
_log_level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO

if os.getenv("LOG_FORMAT", "json").lower() == "json":
    from pythonjsonlogger import jsonlogger

    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    ))
    logging.root.handlers = [_handler]
    logging.root.setLevel(_log_level)
else:
    logging.basicConfig(
        level=_log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Notification Service",
    version="1.0.0",
)

app.include_router(handlers_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "notification"}


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr programmatic subscription endpoint.
    Tells Dapr which topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/api/events/reminders",
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-updates",
            "route": "/api/events/task-updates",
        },
    ]
