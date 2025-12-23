"""
Authentication API endpoints for YogaFlow.
Handles user registration, login, and logout.
"""
from fastapi import APIRouter, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    AuthResponse,
    TokenResponse,
    PasswordReset,
    PasswordResetConfirm,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    verify_email_token,
    resend_verification_email,
    request_password_reset,
    reset_password,
)
from app.api.dependencies import DatabaseSession, CurrentUser
from app.core.logging_config import log_auth_event
from app.core.rate_limit import auth_rate_limit, limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password"
)
@auth_rate_limit
async def register(
    request: Request,
    user_data: UserRegister,
    db_session: DatabaseSession
) -> AuthResponse:
    """
    Register a new user account.

    Requirements:
    - Email must be unique
    - Password must be at least 8 characters
    - Password must contain uppercase, lowercase, and number

    Returns authentication tokens automatically after registration.
    """
    # Register user
    user = await register_user(user_data, db_session)
    await db_session.commit()

    # Auto-login after registration
    login_data = UserLogin(
        email=user_data.email,
        password=user_data.password,
        remember_me=False
    )
    user, tokens = await authenticate_user(login_data, db_session)
    await db_session.commit()

    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return JWT tokens"
)
@auth_rate_limit
async def login(
    request: Request,
    login_data: UserLogin,
    db_session: DatabaseSession
) -> AuthResponse:
    """
    Authenticate user with email and password.

    Returns:
    - User profile information
    - Access token (valid for 24 hours)
    - Refresh token (valid for 7 days, only if remember_me is true)

    The access token should be included in the Authorization header:
    ```
    Authorization: Bearer <access_token>
    ```
    """
    user, tokens = await authenticate_user(login_data, db_session)
    await db_session.commit()

    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout current user and invalidate token"
)
async def logout(
    request: Request,
    current_user: CurrentUser
) -> dict:
    """
    Logout current user and blacklist their access token.

    The token is added to a Redis blacklist and will be rejected for
    any future requests until it naturally expires.

    Client should also discard the access and refresh tokens locally.
    """
    from app.services.token_blacklist import token_blacklist
    from app.core.config import settings

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix

        # Blacklist the token with TTL matching remaining token lifetime
        # Tokens expire in access_token_expire_minutes
        ttl_seconds = settings.access_token_expire_minutes * 60
        await token_blacklist.blacklist_token(token, ttl_seconds)

    log_auth_event(
        event_type="logout",
        user_id=current_user.user_id,
        email=current_user.email,
        success=True
    )

    return {
        "message": "Successfully logged out",
        "detail": "Your session has been invalidated. Please login again to continue."
    }


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get profile information for authenticated user"
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """
    Get current user profile information.

    Requires valid authentication token in Authorization header.

    Returns complete user profile excluding sensitive data (password).
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    refresh_token: str,
    db_session: DatabaseSession
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Use this endpoint when access token expires but refresh token is still valid.
    This avoids requiring user to login again.

    Args:
        refresh_token: Valid refresh token from login

    Returns:
        New access token with updated expiration
    """
    from app.core.security import decode_token, create_access_token
    from app.core.config import settings

    # Decode and validate refresh token
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    email = payload.get("sub")
    user_id = payload.get("user_id")

    if not email or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Create new access token
    token_data = {"sub": email, "user_id": user_id}
    access_token = create_access_token(token_data)

    log_auth_event(
        event_type="token_refresh",
        user_id=user_id,
        email=email,
        success=True
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,  # Keep same refresh token
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    summary="Verify email address",
    description="Verify user email using verification token from email"
)
async def verify_email(
    token: str,
    db_session: DatabaseSession
) -> dict:
    """
    Verify user email address using verification token.

    Args:
        token: Email verification token from verification email link

    Returns:
        Success message

    The frontend should extract the token from the URL query parameter
    and send it to this endpoint. After successful verification, the user
    can access all features of the application.
    """
    user = await verify_email_token(token, db_session)
    await db_session.commit()

    return {
        "message": "Email verified successfully",
        "email": user.email
    }


@router.post(
    "/resend-verification",
    status_code=status.HTTP_200_OK,
    summary="Resend verification email",
    description="Resend verification email to user"
)
async def resend_verification(
    email: str,
    db_session: DatabaseSession
) -> dict:
    """
    Resend verification email to user.

    Args:
        email: User's email address

    Returns:
        Success message

    Use this endpoint if the user didn't receive the verification email
    or if the token has expired.
    """
    await resend_verification_email(email, db_session)
    await db_session.commit()

    return {
        "message": "Verification email sent",
        "email": email
    }


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Request a password reset email with reset token"
)
@auth_rate_limit
async def forgot_password(
    request: Request,
    reset_request: PasswordReset,
    db_session: DatabaseSession
) -> dict:
    """
    Request password reset for user account.

    Args:
        reset_request: Password reset request with email

    Returns:
        Success message

    Sends an email with a password reset link containing a secure token.
    The token expires after 1 hour for security.

    Note: Always returns success to prevent email enumeration attacks,
    even if the email doesn't exist in the system.
    """
    result = await request_password_reset(reset_request.email, db_session)
    await db_session.commit()

    return result


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset password with token",
    description="Reset user password using reset token from email"
)
@auth_rate_limit
async def reset_password_endpoint(
    request: Request,
    reset_confirm: PasswordResetConfirm,
    db_session: DatabaseSession
) -> dict:
    """
    Reset user password using reset token.

    Args:
        reset_confirm: Reset token and new password

    Returns:
        Success message with email

    The reset token must be valid and not expired (expires after 1 hour).
    The new password must meet strength requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number

    After successful reset, the token is invalidated and cannot be reused.
    """
    user = await reset_password(
        reset_token=reset_confirm.token,
        new_password=reset_confirm.new_password,
        db_session=db_session
    )
    await db_session.commit()

    return {
        "message": "Password reset successful",
        "email": user.email
    }
