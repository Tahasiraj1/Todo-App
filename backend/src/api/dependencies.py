# [Task]: T021 [From]: plan.md §Project Structure
"""
FastAPI dependencies for authentication and database session management.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from ..db import get_session
from ..middleware.auth import extract_user_id_from_token, JWTAuthError

# Security scheme
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency to get the current authenticated user's ID.

    Args:
        credentials: The HTTP Bearer credentials from the request

    Returns:
        The authenticated user_id from the JWT token

    Raises:
        HTTPException: 401 if authentication fails
    """
    if not credentials:
        raise JWTAuthError("No authentication credentials provided")

    return extract_user_id_from_token(credentials.credentials)


# Type aliases for cleaner dependency injection
DbSession = Annotated[Session, Depends(get_session)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
