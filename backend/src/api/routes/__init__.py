# [Task]: T042, T043 [From]: plan.md §Project Structure
"""Routes package - exports all API routers."""

from fastapi import APIRouter

from .tasks import router as tasks_router

# Main API router
router = APIRouter()

# Include task routes with user_id in path (per hackathon requirements)
# Endpoints: /api/{user_id}/tasks, /api/{user_id}/tasks/{id}, etc.
router.include_router(tasks_router, prefix="/{user_id}/tasks", tags=["Tasks"])
