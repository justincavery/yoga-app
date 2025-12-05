"""
Centralized logging configuration for YogaFlow backend.
Uses structlog for structured logging with JSON output.

Per CLAUDE.md requirements:
- Always implement a centralized, robust logging module
- Structured logging for easy parsing and analysis
"""
import logging
import sys
from typing import Any
import structlog
from structlog.types import FilteringBoundLogger

from app.core.config import settings


def setup_logging() -> FilteringBoundLogger:
    """
    Configure structured logging for the application.

    Features:
    - JSON output for production (easy parsing by log aggregators)
    - Console output for development (human-readable)
    - Request ID tracking
    - Timestamp inclusion
    - Log level filtering
    - Exception tracking

    Returns:
        FilteringBoundLogger: Configured logger instance
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )

    # Shared processors for all configurations
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Configure structlog
    if settings.log_format == "json":
        # JSON output for production
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console output for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


# Global logger instance
logger: FilteringBoundLogger = setup_logging()


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **extra: Any
) -> None:
    """
    Log HTTP request with structured data.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        **extra: Additional context to log
    """
    logger.info(
        "HTTP request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **extra
    )


def log_auth_event(
    event_type: str,
    user_id: int | None,
    email: str | None,
    success: bool,
    **extra: Any
) -> None:
    """
    Log authentication events for security monitoring.

    Args:
        event_type: Type of auth event (login, logout, register, etc.)
        user_id: User ID if known
        email: User email if known
        success: Whether the operation succeeded
        **extra: Additional context
    """
    log_func = logger.info if success else logger.warning
    log_func(
        "Authentication event",
        event_type=event_type,
        user_id=user_id,
        email=email,
        success=success,
        **extra
    )


def log_error(
    error: Exception,
    context: str,
    **extra: Any
) -> None:
    """
    Log errors with full context and stack trace.

    Args:
        error: Exception that occurred
        context: Context description
        **extra: Additional context
    """
    logger.error(
        context,
        error=str(error),
        error_type=type(error).__name__,
        exc_info=True,
        **extra
    )
