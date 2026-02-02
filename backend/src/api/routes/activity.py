# [Task]: T065 [From]: contracts/api-extensions.yaml §/api/{user_id}/activity
"""
Activity log API route.
GET /api/{user_id}/activity — returns recent activity with pagination.
"""

import logging

from fastapi import APIRouter, Query

from ..dependencies import CurrentUserId, DbSession
from ...services.activity_service import ActivityService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def get_activity(
    user_id: str,
    current_user: CurrentUserId,
    session: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Get activity log entries for the authenticated user.
    Returns paginated list of recent activity.
    """
    service = ActivityService(session)
    entries, total = service.list_entries(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )

    return {
        "entries": [
            {
                "id": e.id,
                "user_id": e.user_id,
                "task_id": e.task_id,
                "event_type": e.event_type,
                "task_title": e.task_title,
                "task_data": e.task_data,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ],
        "total": total,
    }
