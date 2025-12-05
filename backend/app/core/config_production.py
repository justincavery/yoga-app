"""
Production-specific configuration settings.
This module provides production-ready defaults and validation.
"""
from typing import Optional
from pydantic import field_validator
from app.core.config import Settings


class ProductionSettings(Settings):
    """
    Production configuration with enhanced security and validation.

    Extends base Settings with production-specific requirements:
    - Forces DEBUG to False
    - Requires PostgreSQL (no SQLite)
    - Validates secret keys are not defaults
    - Enforces HTTPS for frontend URL
    """

    # Override defaults for production
    debug: bool = False
    environment: str = "production"

    # Security validation
    @field_validator('debug')
    @classmethod
    def validate_debug_false(cls, value: bool) -> bool:
        """Ensure DEBUG is always False in production."""
        if value:
            raise ValueError("DEBUG must be False in production environment")
        return False

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        """Ensure secret key is not the default value."""
        if "CHANGE-THIS" in value or len(value) < 32:
            raise ValueError(
                "SECRET_KEY must be changed from default and be at least 32 characters. "
                "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )
        return value

    @field_validator('database_url')
    @classmethod
    def validate_postgresql(cls, value: str) -> str:
        """Ensure PostgreSQL is used in production (not SQLite)."""
        if 'sqlite' in value.lower():
            raise ValueError(
                "SQLite is not suitable for production. Use PostgreSQL. "
                "Example: postgresql+asyncpg://user:password@host:5432/dbname"
            )
        if 'postgresql' not in value.lower():
            raise ValueError("Production requires PostgreSQL database")
        return value

    @field_validator('frontend_url')
    @classmethod
    def validate_https(cls, value: str) -> str:
        """Ensure frontend URL uses HTTPS in production."""
        if not value.startswith('https://'):
            raise ValueError(
                f"Frontend URL must use HTTPS in production. Got: {value}"
            )
        return value

    @field_validator('allowed_origins')
    @classmethod
    def validate_no_localhost(cls, value: str) -> str:
        """Warn if localhost is in allowed origins."""
        if 'localhost' in value or '127.0.0.1' in value:
            raise ValueError(
                "Localhost origins should not be allowed in production. "
                "Use your actual domain(s)."
            )
        return value

    # Production-specific settings
    workers: int = 4
    max_connections: int = 100
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "production"
    sentry_traces_sample_rate: float = 0.1
