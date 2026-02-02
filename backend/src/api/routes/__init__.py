# [Task]: T042, T043, T024, T050, T066 [From]: plan.md §Project Structure
"""Routes package - exports all API routers."""

from fastapi import APIRouter

from .chat import router as chat_router
from .tasks import router as tasks_router
from .jobs import router as jobs_router
from .events import router as events_router
from .activity import router as activity_router
from .websocket import router as websocket_router

# Main API router
router = APIRouter()

# Include task routes with user_id in path (per hackathon requirements)
# Endpoints: /api/{user_id}/tasks, /api/{user_id}/tasks/{id}, etc.
router.include_router(tasks_router, prefix="/{user_id}/tasks", tags=["Tasks"])

# Include chat routes with user_id in path
# Endpoints: /api/{user_id}/chat, /api/{user_id}/conversations, etc.
router.include_router(chat_router, prefix="/{user_id}", tags=["Chat"])

# Include activity log routes with user_id in path
# Endpoint: /api/{user_id}/activity
router.include_router(activity_router, prefix="/{user_id}/activity", tags=["Activity"])

# Include Dapr Jobs callback route (internal, called by Dapr sidecar)
# Endpoint: /api/jobs/{job_name}
router.include_router(jobs_router, tags=["Jobs"])

# Include Dapr event subscription handler routes (internal, called by Dapr sidecar)
# Endpoint: /api/events/task-events
router.include_router(events_router, tags=["Events"])

# Include WebSocket route for real-time sync
# Endpoint: /api/ws/{user_id}
router.include_router(websocket_router, tags=["WebSocket"])
