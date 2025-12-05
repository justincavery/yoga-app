"""
Monitoring and error tracking configuration for YogaFlow.
Integrates Sentry for error tracking and performance monitoring.
"""
import logging
from typing import Optional
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.core.config import settings


def init_sentry() -> None:
    """
    Initialize Sentry error tracking and performance monitoring.

    Only initializes if SENTRY_DSN is configured in environment.
    Integrates with FastAPI, SQLAlchemy, and logging.
    """
    # Check if Sentry is configured
    sentry_dsn: Optional[str] = getattr(settings, 'sentry_dsn', None)

    if not sentry_dsn:
        logging.info("Sentry DSN not configured. Error tracking disabled.")
        return

    # Configure integrations
    integrations = [
        FastApiIntegration(transaction_style="endpoint"),
        SqlalchemyIntegration(),
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        ),
    ]

    # Initialize Sentry
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=getattr(settings, 'sentry_environment', settings.environment),
        traces_sample_rate=getattr(settings, 'sentry_traces_sample_rate', 0.1),
        profiles_sample_rate=0.1,
        integrations=integrations,
        send_default_pii=False,  # Don't send PII by default
        attach_stacktrace=True,
        max_breadcrumbs=50,
        before_send=before_send_filter,
    )

    logging.info(
        "Sentry initialized",
        extra={
            "environment": settings.environment,
            "traces_sample_rate": getattr(settings, 'sentry_traces_sample_rate', 0.1)
        }
    )


def before_send_filter(event, hint):
    """
    Filter events before sending to Sentry.

    - Removes sensitive data
    - Filters out noise (e.g., health check failures)
    - Adds custom tags

    Args:
        event: Sentry event dictionary
        hint: Additional context about the event

    Returns:
        Modified event or None to drop the event
    """
    # Filter out health check errors
    if 'request' in event:
        url = event.get('request', {}).get('url', '')
        if '/health' in url or '/metrics' in url:
            return None

    # Add custom tags
    if 'tags' not in event:
        event['tags'] = {}

    event['tags']['app'] = 'yogaflow'
    event['tags']['version'] = settings.app_version

    # Remove sensitive data from headers
    if 'request' in event and 'headers' in event['request']:
        headers = event['request']['headers']
        # Redact authorization headers
        if 'Authorization' in headers:
            headers['Authorization'] = '[REDACTED]'
        if 'Cookie' in headers:
            headers['Cookie'] = '[REDACTED]'

    return event


def capture_exception(error: Exception, context: Optional[dict] = None) -> None:
    """
    Capture an exception and send to Sentry with additional context.

    Args:
        error: The exception to capture
        context: Additional context dictionary to include
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_exception(error)
    else:
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: Optional[dict] = None) -> None:
    """
    Capture a message and send to Sentry.

    Args:
        message: The message to capture
        level: Message level (debug, info, warning, error, fatal)
        context: Additional context dictionary to include
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_message(message, level=level)
    else:
        sentry_sdk.capture_message(message, level=level)
