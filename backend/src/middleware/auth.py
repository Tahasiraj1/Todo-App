# [Task]: T017, T103 [From]: plan.md, research.md - JWT verification with JWKS
"""
JWT verification middleware for authenticating requests.
Verifies Better Auth JWT tokens using JWKS (JSON Web Key Set).
"""

import logging
import os
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI documentation
security = HTTPBearer()

# JWKS URL from Better Auth
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
JWKS_URL = f"{BETTER_AUTH_URL}/api/auth/jwks"

# Valid issuers - support both localhost (browser) and K8s service URLs
VALID_ISSUERS = [
    "http://localhost:3000",
    "http://todo-frontend:3000",
    os.getenv("BETTER_AUTH_URL", "http://localhost:3000"),
]

# Cache for JWKS client
_jwks_client: Optional[PyJWKClient] = None
_jwks_cache_time: Optional[datetime] = None
JWKS_CACHE_DURATION = timedelta(hours=1)


class JWTAuthError(HTTPException):
    """Custom exception for JWT authentication errors."""

    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_jwks_client() -> PyJWKClient:
    """
    Get or create the JWKS client with caching.
    Refreshes the cache periodically to pick up key rotations.
    """
    global _jwks_client, _jwks_cache_time

    now = datetime.utcnow()

    # Check if we need to refresh the cache
    if (
        _jwks_client is None
        or _jwks_cache_time is None
        or (now - _jwks_cache_time) > JWKS_CACHE_DURATION
    ):
        logger.info(f"Fetching JWKS from {JWKS_URL}")
        try:
            _jwks_client = PyJWKClient(JWKS_URL, cache_keys=True)
            _jwks_cache_time = now
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise JWTAuthError("Unable to verify token: JWKS unavailable")

    return _jwks_client


def decode_jwt_token(token: str) -> dict:
    """
    Decode and verify a JWT token using JWKS.

    Args:
        token: The JWT token string

    Returns:
        The decoded token payload

    Raises:
        JWTAuthError: If token is invalid or expired
    """
    try:
        # Get the signing key from JWKS
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Try decoding with each valid issuer/audience combination
        # This handles the mismatch between browser URL (localhost) and K8s service URL
        last_error = None
        for issuer in VALID_ISSUERS:
            try:
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["EdDSA", "ES256", "RS256"],
                    audience=issuer,
                    issuer=issuer,
                    options={"verify_exp": True},
                )
                logger.debug(f"Token decoded successfully using issuer: {issuer}")
                return payload
            except (jwt.InvalidAudienceError, jwt.InvalidIssuerError) as e:
                last_error = e
                continue

        # If we get here, none of the issuers worked
        logger.warning(f"Authentication failed: Invalid issuer/audience. Tried: {VALID_ISSUERS}")
        raise JWTAuthError("Invalid token issuer or audience")

    except jwt.ExpiredSignatureError:
        logger.warning("Authentication failed: Token has expired")
        raise JWTAuthError("Token has expired")
    except jwt.PyJWKClientError as e:
        logger.error(f"JWKS client error: {e}")
        raise JWTAuthError("Unable to verify token")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Authentication failed: Invalid token - {str(e)}")
        raise JWTAuthError(f"Invalid token: {str(e)}")
    except JWTAuthError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise JWTAuthError("Token verification failed")


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user_id from a JWT token.

    Args:
        token: The JWT token string

    Returns:
        The user_id from the token

    Raises:
        JWTAuthError: If token is invalid or user_id not found
    """
    payload = decode_jwt_token(token)

    # Better Auth stores user ID in 'sub' field
    user_id = payload.get("sub")

    if not user_id:
        logger.warning("Authentication failed: Token does not contain user identifier")
        raise JWTAuthError("Token does not contain user identifier")

    logger.info(f"User authenticated: user_id={user_id}")
    return str(user_id)


async def get_token_from_header(request) -> Optional[str]:
    """
    Extract JWT token from Authorization header.

    Args:
        request: The FastAPI request object

    Returns:
        The token string or None if not present
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


async def verify_auth(
    credentials: HTTPAuthorizationCredentials = None,
) -> str:
    """
    Verify JWT authentication and return user_id.
    Used as a FastAPI dependency.

    Args:
        credentials: The HTTP Bearer credentials

    Returns:
        The authenticated user_id

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise JWTAuthError("No authentication credentials provided")

    token = credentials.credentials
    return extract_user_id_from_token(token)
