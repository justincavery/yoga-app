"""
Centralized logging configuration for the YogaFlow application.

This module provides a robust, structured logging framework that:
- Supports JSON and text formats
- Includes context information (request_id, user_id, etc.)
- Integrates with Sentry for error tracking
- Provides structured logging for easy parsing
- Supports different log levels per environment

Usage:
    from core.logging_config import get_logger

    logger = get_logger(__name__)
    logger.info("Application started", extra={"version": "1.0.0"})
    logger.error("Error occurred", exc_info=True, extra={"user_id": 123})
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
import os
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as JSON for structured logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields (like request_id, user_id, etc.)
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        # Add any other extra fields passed to logger
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs", "message",
                "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info"
            ]:
                log_data[key] = value

        return json.dumps(log_data)


class HumanReadableFormatter(logging.Formatter):
    """
    Formatter for human-readable console output with colors (if supported).
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for human-readable output."""
        # Add color if terminal supports it
        color = self.COLORS.get(record.levelname, "")
        reset = self.COLORS["RESET"]

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        # Basic log line
        log_line = (
            f"{color}{timestamp} [{record.levelname:8s}]{reset} "
            f"{record.name:20s} - {record.getMessage()}"
        )

        # Add extra context if present
        extras = []
        if hasattr(record, "request_id"):
            extras.append(f"request_id={record.request_id}")
        if hasattr(record, "user_id"):
            extras.append(f"user_id={record.user_id}")
        if hasattr(record, "duration_ms"):
            extras.append(f"duration={record.duration_ms}ms")

        if extras:
            log_line += f" ({', '.join(extras)})"

        # Add exception if present
        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"

        return log_line


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    enable_sentry: bool = False,
    sentry_dsn: Optional[str] = None,
) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ('json' or 'human')
        log_file: Optional path to log file
        enable_sentry: Whether to enable Sentry integration
        sentry_dsn: Sentry DSN for error tracking
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Choose formatter based on format preference
    if log_format.lower() == "json":
        formatter = StructuredFormatter()
    else:
        formatter = HumanReadableFormatter()

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_handler.setFormatter(StructuredFormatter())  # Always use JSON for files
        root_logger.addHandler(file_handler)

    # Sentry integration (for error tracking)
    if enable_sentry and sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration

            sentry_logging = LoggingIntegration(
                level=logging.INFO,        # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors and above as events
            )

            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[sentry_logging],
                traces_sample_rate=0.1,  # Sample 10% of transactions for performance monitoring
                environment=os.getenv("APP_ENV", "development"),
            )

            root_logger.info("Sentry integration enabled")
        except ImportError:
            root_logger.warning("Sentry SDK not installed, skipping Sentry integration")

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)

    root_logger.info(
        f"Logging configured: level={log_level}, format={log_format}, "
        f"file={log_file}, sentry={enable_sentry}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("User logged in", extra={"user_id": 123})
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for adding contextual information to logs.

    Example:
        with LogContext(request_id="abc123", user_id=42):
            logger.info("Processing request")
    """

    def __init__(self, **kwargs):
        """Initialize context with key-value pairs."""
        self.context = kwargs
        self.old_factory = None

    def __enter__(self):
        """Enter context and modify log record factory."""
        self.old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original log record factory."""
        logging.setLogRecordFactory(self.old_factory)


# Initialize logging from environment variables on module import
if __name__ != "__main__":
    setup_logging(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_format=os.getenv("LOG_FORMAT", "json"),
        log_file=os.getenv("LOG_FILE"),
        enable_sentry=bool(os.getenv("SENTRY_DSN")),
        sentry_dsn=os.getenv("SENTRY_DSN"),
    )
