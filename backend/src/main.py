# [Task]: T020 [From]: plan.md §Project Structure
"""
FastAPI main application entry point.
Configures CORS, routes, and error handling.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

from sqlmodel import Session
from .db import create_db_and_tables, get_engine
from .middleware.error_handler import setup_error_handlers
from .api.routes import router as api_router
from .models.activity_log import ActivityLogEntry  # noqa: F401 — register for table creation
from .models.schemas import TaskCreate
from .services.task_service import TaskService
from .services.websocket_manager import ws_manager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Creates database tables on startup.
    """
    logger.info("Starting application...")
    create_db_and_tables()
    logger.info("Database tables created/verified")
    yield
    logger.info("Application shutdown")


# Create FastAPI application
app = FastAPI(
    title="Todo App API",
    description="RESTful API for Todo Full-Stack Web Application (Phase II)",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
setup_error_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api")

# Mount Dapr Jobs callback at top-level /job/{name} (Dapr convention)
from .api.routes.jobs import router as jobs_router
app.include_router(jobs_router, tags=["Dapr Jobs"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/internal/create-task")
async def internal_create_task(request_data: dict):
    """
    Internal endpoint for recurring-task service to create next task occurrence.
    Not exposed externally — called via Dapr service invocation.
    """
    user_id = request_data.get("user_id", "")
    task_payload = request_data.get("task", {})
    logger.info("internal/create-task: user_id=%s, title=%s", user_id, task_payload.get("title", ""))
    if not user_id or not task_payload:
        return {"status": "error", "detail": "Missing user_id or task"}
    try:
        task_data = TaskCreate(**task_payload)
        with Session(get_engine()) as session:
            service = TaskService(session, user_id)
            task = service.create_task(task_data)
            return {"status": "ok", "task_id": task.id}
    except Exception as e:
        logger.error("internal/create-task failed: %s", str(e))
        return {"status": "error", "detail": str(e)}


@app.post("/api/internal/ws-broadcast")
async def ws_broadcast(request_data: dict):
    """
    Internal endpoint for notification service to broadcast WebSocket messages.
    Not exposed externally — called via Dapr service invocation or direct HTTP.
    """
    user_id = request_data.get("user_id", "")
    message = request_data.get("message", {})
    logger.info("ws-broadcast received: user_id=%s, message_type=%s", user_id, message.get("type", "none"))
    if user_id and message:
        await ws_manager.broadcast_to_user(user_id, message)
    return {"status": "ok"}
