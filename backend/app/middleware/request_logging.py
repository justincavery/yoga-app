"""
Request logging middleware for YogaFlow.
Logs all HTTP requests with timing information.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import log_request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests with timing.

    Logs:
    - HTTP method
    - Request path
    - Status code
    - Response time in milliseconds
    - Client IP (if available)
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response from next handler
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Log request
        log_request(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            client_ip=client_ip
        )

        return response
