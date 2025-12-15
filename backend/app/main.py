"""
Main FastAPI application for YogaFlow backend.
Entry point for the API server.
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import init_database, close_database
from app.core.logging_config import logger
from app.core.monitoring import init_sentry
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.error_handler import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.core.rate_limit import setup_rate_limiting, limiter, custom_rate_limit_exceeded_handler
from app.api.v1.endpoints import auth, poses, upload, sequences, sessions, history, profile
try:
    from app.api.v1.admin import sequences as admin_sequences
    HAS_ADMIN_SEQUENCES = True
except ImportError:
    HAS_ADMIN_SEQUENCES = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting YogaFlow API", version=settings.app_version, environment=settings.environment)

    # Initialize monitoring (Sentry)
    init_sentry()

    # Initialize database
    await init_database()

    # Initialize token blacklist (Redis)
    from app.services.token_blacklist import init_token_blacklist
    await init_token_blacklist()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down YogaFlow API")

    # Close token blacklist
    from app.services.token_blacklist import close_token_blacklist
    await close_token_blacklist()

    await close_database()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Set up rate limiting
setup_rate_limiting(app)

# CORS middleware (REQ-NF-SEC-* for security)
# Uses get_cors_origins() which filters localhost in production
cors_origins = settings.get_cors_origins()
logger.info("CORS configured", allowed_origins=cors_origins, environment=settings.environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware, environment=settings.environment)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# API routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(poses.router, prefix=settings.api_v1_prefix)
app.include_router(sequences.router, prefix=settings.api_v1_prefix)
app.include_router(sessions.router, prefix=f"{settings.api_v1_prefix}/sessions", tags=["Practice Sessions"])
app.include_router(history.router, prefix=settings.api_v1_prefix)
app.include_router(upload.router, prefix=settings.api_v1_prefix)
app.include_router(profile.router, prefix=settings.api_v1_prefix)
if HAS_ADMIN_SEQUENCES:
    app.include_router(admin_sequences.router, prefix=settings.api_v1_prefix)

# Mount static files for development (images, etc.)
content_dir = Path(__file__).parent.parent.parent / "content"
if content_dir.exists():
    app.mount("/images", StaticFiles(directory=str(content_dir / "images")), name="images")
    logger.info("Static files mounted", path=str(content_dir / "images"))


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API health check.

    Returns basic API information and status.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "environment": settings.environment,
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Health status and uptime information
    """
    return {
        "status": "healthy",
        "service": "yogaflow-api",
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
