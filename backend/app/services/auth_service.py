"""
Authentication service for YogaFlow.
Handles user registration, login, and session management.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
)
from app.core.config import settings
from app.core.logging_config import log_auth_event, logger
from app.schemas.user import UserRegister, UserLogin, TokenResponse
from app.services.email_service import email_service, generate_verification_token


async def register_user(
    user_data: UserRegister,
    db_session: AsyncSession
) -> User:
    """
    Register a new user account.

    Args:
        user_data: User registration data
        db_session: Database session

    Returns:
        User: Created user object

    Raises:
        HTTPException: If email already exists or password is weak
    """
    # Check if email already exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db_session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        log_auth_event(
            event_type="register",
            user_id=None,
            email=user_data.email,
            success=False,
            reason="email_exists"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered"
        )

    # Validate password strength
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Hash password
    password_hash = hash_password(user_data.password)

    # Generate email verification token
    verification_token = generate_verification_token()
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)

    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        name=user_data.name,
        experience_level=user_data.experience_level,
        email_verification_token=verification_token,
        email_verification_expires=verification_expires,
    )

    db_session.add(new_user)
    await db_session.flush()  # Get user_id before commit
    await db_session.refresh(new_user)

    # Send verification email (async, don't block on failure)
    try:
        await email_service.send_verification_email(
            to_email=new_user.email,
            name=new_user.name,
            verification_token=verification_token
        )
        logger.info(f"Verification email sent to: {new_user.email}")
    except Exception as error:
        logger.error(f"Failed to send verification email: {error}")
        # Don't fail registration if email fails

    log_auth_event(
        event_type="register",
        user_id=new_user.user_id,
        email=new_user.email,
        success=True
    )

    logger.info(f"New user registered: {new_user.email}")
    return new_user


async def authenticate_user(
    login_data: UserLogin,
    db_session: AsyncSession
) -> tuple[User, TokenResponse]:
    """
    Authenticate user and generate tokens.

    Implements account lockout after MAX_LOGIN_ATTEMPTS failed attempts.

    Args:
        login_data: Login credentials
        db_session: Database session

    Returns:
        tuple[User, TokenResponse]: User object and authentication tokens

    Raises:
        HTTPException: If credentials are invalid or account is locked
    """
    # Find user by email
    stmt = select(User).where(User.email == login_data.email)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()

    # Check if account is locked (with backward compatibility)
    if user and hasattr(user, 'account_locked_until') and user.account_locked_until:
        if datetime.now(timezone.utc) < user.account_locked_until:
            # Account is still locked
            lockout_remaining = (user.account_locked_until - datetime.now(timezone.utc)).total_seconds() / 60
            log_auth_event(
                event_type="login",
                user_id=user.user_id,
                email=login_data.email,
                success=False,
                reason="account_locked"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is locked due to too many failed login attempts. Try again in {int(lockout_remaining)} minutes."
            )
        else:
            # Lockout period expired - reset
            user.account_locked_until = None
            user.failed_login_attempts = 0
            await db_session.flush()

    if not user or not verify_password(login_data.password, user.password_hash):
        # Failed login - increment attempts (with backward compatibility)
        if user and hasattr(user, 'failed_login_attempts'):
            user.failed_login_attempts += 1

            # Lock account if max attempts reached
            if user.failed_login_attempts >= settings.max_login_attempts:
                lockout_duration = timedelta(minutes=settings.account_lockout_minutes)
                if hasattr(user, 'account_locked_until'):
                    user.account_locked_until = datetime.now(timezone.utc) + lockout_duration
                await db_session.flush()

                log_auth_event(
                    event_type="account_locked",
                    user_id=user.user_id,
                    email=user.email,
                    success=False,
                    reason="max_login_attempts_exceeded"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account locked due to {settings.max_login_attempts} failed login attempts. Try again in {settings.account_lockout_minutes} minutes."
                )

            await db_session.flush()

        log_auth_event(
            event_type="login",
            user_id=user.user_id if user else None,
            email=login_data.email,
            success=False,
            reason="invalid_credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        log_auth_event(
            event_type="login",
            user_id=user.user_id,
            email=user.email,
            success=False,
            reason="account_inactive"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Successful login - reset failed attempts
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.last_login = datetime.now(timezone.utc)
    await db_session.flush()

    # Generate tokens
    token_data = {"sub": user.email, "user_id": user.user_id}
    access_token = create_access_token(token_data)

    refresh_token = None
    expires_in = settings.access_token_expire_minutes * 60

    if login_data.remember_me:
        refresh_token = create_refresh_token(token_data)
        expires_in = settings.refresh_token_expire_minutes * 60

    tokens = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in
    )

    log_auth_event(
        event_type="login",
        user_id=user.user_id,
        email=user.email,
        success=True,
        remember_me=login_data.remember_me
    )

    logger.info(f"User logged in: {user.email}")
    return user, tokens


async def get_current_user(
    token: str,
    db_session: AsyncSession
) -> User:
    """
    Get current user from JWT token.

    Args:
        token: JWT access token
        db_session: Database session

    Returns:
        User: Current user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    from app.core.security import decode_token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Get user from database
    stmt = select(User).where(User.email == email)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def verify_email_token(
    verification_token: str,
    db_session: AsyncSession
) -> User:
    """
    Verify email using verification token.

    Args:
        verification_token: Email verification token
        db_session: Database session

    Returns:
        User: User with verified email

    Raises:
        HTTPException: If token is invalid or expired
    """
    # Find user by verification token
    stmt = select(User).where(User.email_verification_token == verification_token)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    # Check if token is expired
    if user.email_verification_expires and user.email_verification_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )

    # Mark email as verified
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    await db_session.flush()

    logger.info(f"Email verified for user: {user.email}")
    return user


async def resend_verification_email(
    email: str,
    db_session: AsyncSession
) -> bool:
    """
    Resend verification email to user.

    Args:
        email: User's email address
        db_session: Database session

    Returns:
        bool: True if email sent successfully

    Raises:
        HTTPException: If user not found or already verified
    """
    # Find user by email
    stmt = select(User).where(User.email == email)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    # Generate new verification token
    verification_token = generate_verification_token()
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)

    user.email_verification_token = verification_token
    user.email_verification_expires = verification_expires
    await db_session.flush()

    # Send verification email
    try:
        await email_service.send_verification_email(
            to_email=user.email,
            name=user.name,
            verification_token=verification_token
        )
        logger.info(f"Verification email resent to: {user.email}")
        return True
    except Exception as error:
        logger.error(f"Failed to resend verification email: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )


async def request_password_reset(
    email: str,
    db_session: AsyncSession
) -> dict:
    """
    Request password reset for user.
    Always returns success to prevent email enumeration attacks.

    Args:
        email: User's email address
        db_session: Database session

    Returns:
        dict: Success message (always returns success)
    """
    # Find user by email
    stmt = select(User).where(User.email == email)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()

    # Always return success, even if user doesn't exist (security best practice)
    # This prevents attackers from determining which emails are registered
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {email}")
        return {"message": "Password reset email sent", "email": email}

    # Generate password reset token
    reset_token = generate_verification_token()
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry

    user.password_reset_token = reset_token
    user.password_reset_expires = reset_expires
    await db_session.flush()

    # Send password reset email
    try:
        await email_service.send_password_reset_email(
            to_email=user.email,
            name=user.name,
            reset_token=reset_token
        )
        logger.info(f"Password reset email sent to: {user.email}")
    except Exception as error:
        logger.error(f"Failed to send password reset email: {error}")
        # Don't fail the request if email fails, still return success

    log_auth_event(
        event_type="password_reset_request",
        user_id=user.user_id,
        email=user.email,
        success=True
    )

    return {"message": "Password reset email sent", "email": email}


async def reset_password(
    reset_token: str,
    new_password: str,
    db_session: AsyncSession
) -> User:
    """
    Reset user password using reset token.

    Args:
        reset_token: Password reset token from email
        new_password: New password to set
        db_session: Database session

    Returns:
        User: User with updated password

    Raises:
        HTTPException: If token is invalid, expired, or password is weak
    """
    # Validate password strength
    is_valid, error_message = validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Find user by reset token
    stmt = select(User).where(User.password_reset_token == reset_token)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        log_auth_event(
            event_type="password_reset",
            user_id=None,
            email=None,
            success=False,
            reason="invalid_token"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Check if token is expired
    if user.password_reset_expires and user.password_reset_expires < datetime.now(timezone.utc):
        log_auth_event(
            event_type="password_reset",
            user_id=user.user_id,
            email=user.email,
            success=False,
            reason="expired_token"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )

    # Update password
    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    await db_session.flush()

    log_auth_event(
        event_type="password_reset",
        user_id=user.user_id,
        email=user.email,
        success=True
    )

    logger.info(f"Password reset successful for user: {user.email}")
    return user
