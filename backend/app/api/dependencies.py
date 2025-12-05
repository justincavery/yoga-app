"""
FastAPI dependencies for authentication and database access.
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_database_session
from app.services.auth_service import get_current_user
from app.models.user import User

# Security scheme for Swagger UI
security = HTTPBearer()

# Type aliases for cleaner dependency injection
DatabaseSession = Annotated[AsyncSession, Depends(get_database_session)]


async def get_current_active_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db_session: DatabaseSession
) -> User:
    """
    Dependency to get current authenticated user.

    Args:
        credentials: HTTP Bearer token credentials
        db_session: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If authentication fails

    Example:
        @app.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_active_user)):
            return current_user
    """
    token = credentials.credentials
    user = await get_current_user(token, db_session)
    return user


# Type alias for current user dependency
CurrentUser = Annotated[User, Depends(get_current_active_user)]


async def get_admin_user(current_user: CurrentUser) -> User:
    """
    Dependency to ensure current user is an admin.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current user if they are admin

    Raises:
        HTTPException: If user is not admin

    Note:
        For MVP, we'll check if user email ends with @admin.yogaflow.com
        In production, implement proper role-based access control (RBAC)
    """
    # MVP admin check - in production use proper RBAC
    if not current_user.email.endswith("@admin.yogaflow.com"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Type alias for admin user dependency
AdminUser = Annotated[User, Depends(get_admin_user)]
