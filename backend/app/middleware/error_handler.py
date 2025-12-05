"""
Global error handling middleware for YogaFlow.
Provides consistent error responses and logging.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging_config import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation errors with detailed error messages.

    Args:
        request: FastAPI request object
        exc: Validation exception

    Returns:
        JSONResponse with validation error details
    """
    logger.warning(
        "Validation error",
        path=request.url.path,
        method=request.method,
        errors=exc.errors()
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "message": "Request validation failed"
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions with consistent format.

    Args:
        request: FastAPI request object
        exc: HTTP exception

    Returns:
        JSONResponse with error details
    """
    logger.warning(
        "HTTP exception",
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        detail=str(exc.detail)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected errors without exposing sensitive details.

    Args:
        request: FastAPI request object
        exc: Exception

    Returns:
        JSONResponse with generic error message
    """
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }
    )
