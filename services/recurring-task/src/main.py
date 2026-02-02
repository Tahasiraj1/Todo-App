# [Task]: T057 [From]: plan.md §Phase C, contracts/dapr-components.yaml
"""
Recurring Task Service — FastAPI app with Dapr subscription handler.
Subscribes to task-events topic. When a recurring task is completed,
computes the next due date and creates a new task via Dapr service invocation.
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
    title="Recurring Task Service",
    version="1.0.0",
)

app.include_router(handlers_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "recurring-task"}


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr programmatic subscription endpoint.
    Tells Dapr which topics this service subscribes to.
    Note: Declarative subscriptions in k8s/dapr/subscriptions.yaml are preferred,
    but this serves as a fallback for local development.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/api/events/task-completed",
        },
    ]
