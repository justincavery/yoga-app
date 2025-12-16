"""
Rate limiting configuration for YogaFlow API.
Uses slowapi for request rate limiting with Redis or in-memory storage.
"""
from fastapi import Request, Response, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Callable

from app.core.config import settings
from app.core.logging_config import logger


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.

    Priority:
    1. Authenticated user ID (from token)
    2. Client IP address

    This ensures authenticated users get their own rate limit bucket,
    while unauthenticated requests are limited by IP.
    """
    # Check for authenticated user in request state
    if hasattr(request.state, "user_id") and request.state.user_id:
        return f"user:{request.state.user_id}"

    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP from the chain (original client)
        return forwarded.split(",")[0].strip()

    return get_remote_address(request) or "unknown"


def get_ip_address(request: Request) -> str:
    """
    Get client IP address for auth endpoint rate limiting.
    Always uses IP regardless of authentication status.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request) or "unknown"


# Create limiter with identifier function
limiter = Limiter(
    key_func=get_identifier,
    default_limits=[],  # No default limit - apply per-route
    storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}" if hasattr(settings, 'redis_host') and settings.redis_host else "memory://",
    strategy="fixed-window",
)


def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    Returns a JSON response with rate limit information.
    """
    response_body = {
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please slow down.",
        "detail": str(exc.detail),
        "retry_after": exc.retry_after if hasattr(exc, 'retry_after') else None
    }

    logger.warning(
        "Rate limit exceeded",
        client_ip=get_ip_address(request),
        path=request.url.path,
        method=request.method,
    )

    return Response(
        content=str(response_body).replace("'", '"'),
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        media_type="application/json",
        headers={
            "Retry-After": str(exc.retry_after) if hasattr(exc, 'retry_after') and exc.retry_after else "60",
            "X-RateLimit-Limit": str(exc.limit) if hasattr(exc, 'limit') else "",
        }
    )


# Rate limit decorators for different endpoint types

# Auth endpoints: 5 requests per minute (strict to prevent brute force)
auth_rate_limit = limiter.limit(
    "5/minute",
    key_func=get_ip_address,
    error_message="Too many authentication attempts. Please wait before trying again."
)

# Public API endpoints: 100 requests per minute
public_rate_limit = limiter.limit(
    "100/minute",
    key_func=get_ip_address,
    error_message="Too many requests. Please slow down."
)

# Authenticated user endpoints: 1000 requests per hour
authenticated_rate_limit = limiter.limit(
    "1000/hour",
    key_func=get_identifier,
    error_message="Hourly request limit exceeded. Please try again later."
)


def setup_rate_limiting(app):
    """
    Configure rate limiting for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

    logger.info(
        "Rate limiting configured",
        auth_limit="5/minute",
        public_limit="100/minute",
        authenticated_limit="1000/hour"
    )
