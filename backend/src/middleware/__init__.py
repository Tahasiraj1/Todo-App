# [Task]: T017, T023 [From]: plan.md §Authentication
"""Middleware package - exports authentication and error handling."""

from .auth import (
    JWTAuthError,
    decode_jwt_token,
    extract_user_id_from_token,
    security,
    verify_auth,
)
from .error_handler import (
    AppError,
    BadRequestError,
    NotFoundError,
    UnauthorizedError,
    setup_error_handlers,
)

__all__ = [
    "security",
    "verify_auth",
    "decode_jwt_token",
    "extract_user_id_from_token",
    "JWTAuthError",
    "AppError",
    "NotFoundError",
    "UnauthorizedError",
    "BadRequestError",
    "setup_error_handlers",
]
