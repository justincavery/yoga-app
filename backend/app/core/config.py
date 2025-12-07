"""
Configuration settings for YogaFlow backend application.
Uses pydantic-settings for environment variable management.
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Security best practices:
    - Never commit secrets to version control
    - Use .env file for local development
    - Use environment variables in production
    - Rotate secrets regularly
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "YogaFlow API"
    app_version: str = "1.0.0"
    app_description: str = "Backend API for YogaFlow yoga practice application"
    debug: bool = False
    environment: str = "development"

    # API
    api_v1_prefix: str = "/api/v1"
    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    # Database
    database_url: str = "sqlite+aiosqlite:///./yogaflow.db"
    # For PostgreSQL in production:
    # database_url: str = "postgresql+asyncpg://user:password@localhost:5432/yogaflow"

    # Security - JWT
    secret_key: str = "CHANGE-THIS-IN-PRODUCTION-USE-STRONG-RANDOM-KEY"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Security - Password
    bcrypt_rounds: int = 12  # Work factor for bcrypt (must be >= 12 per requirements)

    # Security - Rate Limiting (auth endpoints)
    rate_limit_per_minute: int = 5

    # CORS
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,DELETE,PATCH"
    cors_allow_headers: str = "*"

    @property
    def cors_allow_methods_list(self) -> list[str]:
        """Parse allowed methods from comma-separated string."""
        return [method.strip() for method in self.cors_allow_methods.split(",") if method.strip()]

    @property
    def cors_allow_headers_list(self) -> list[str]:
        """Parse allowed headers from comma-separated string."""
        if self.cors_allow_headers == "*":
            return ["*"]
        return [header.strip() for header in self.cors_allow_headers.split(",") if header.strip()]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or console

    # Email Configuration
    email_enabled: bool = False
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_tls: bool = True
    smtp_ssl: bool = False
    email_from: str = "noreply@yogaflow.app"
    email_from_name: str = "YogaFlow"
    frontend_url: str = "http://localhost:3000"

    # Session
    session_timeout_minutes: int = 60 * 24  # 24 hours
    remember_me_timeout_minutes: int = 60 * 24 * 30  # 30 days

    # Account Security
    max_login_attempts: int = 5
    account_lockout_minutes: int = 15

    # File Upload
    upload_directory: str = "./uploads"
    max_upload_size_mb: int = 10

    # CDN Configuration
    cdn_enabled: bool = False
    cdn_base_url: str = "http://localhost"

    # Monitoring (Sentry)
    sentry_dsn: Optional[str] = None
    sentry_environment: Optional[str] = None
    sentry_traces_sample_rate: float = 0.1


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid recreating settings on every call.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()
