"""
Profile management API endpoints for YogaFlow.
Handles user profile viewing and updating.
"""
from fastapi import APIRouter, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.api.dependencies import DatabaseSession, CurrentUser
from app.models.user import User, ExperienceLevel
from app.core.security import verify_password, hash_password, validate_password_strength
from app.core.logging_config import logger

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    description="Get current user's profile information"
)
async def get_profile(current_user: CurrentUser) -> UserResponse:
    """
    Get current user profile information.

    Requires valid authentication token in Authorization header.

    Returns complete user profile excluding sensitive data (password).
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
    description="Update current user's profile information"
)
async def update_profile(
    profile_update: UserUpdate,
    current_user: CurrentUser,
    db_session: DatabaseSession
) -> UserResponse:
    """
    Update user profile information.

    Allowed updates:
    - Name (1-255 characters)
    - Email (valid email format, must be unique)
    - Experience level (beginner, intermediate, advanced)

    Notes:
    - Changing email will reset email_verified to False
    - All fields are optional - only provided fields will be updated
    - Email must be unique across all users

    Returns updated user profile.
    """
    update_data = profile_update.model_dump(exclude_unset=True)

    if not update_data:
        # No updates provided, return current profile
        return UserResponse.model_validate(current_user)

    # Handle email update separately (requires uniqueness check)
    if "email" in update_data:
        new_email = update_data["email"]

        # Check if email is already in use by another user
        stmt = select(User).where(
            User.email == new_email,
            User.user_id != current_user.user_id
        )
        result = await db_session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(
                f"Email update failed - email already exists: {new_email}",
                extra={"user_id": current_user.user_id}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already in use by another account"
            )

        # Update email and reset verification
        current_user.email = new_email
        current_user.email_verified = False
        logger.info(
            f"Email updated for user {current_user.user_id}: {new_email} (verification reset)"
        )

    # Update name if provided
    if "name" in update_data:
        current_user.name = update_data["name"]
        logger.info(f"Name updated for user {current_user.user_id}: {update_data['name']}")

    # Update experience level if provided
    if "experience_level" in update_data:
        experience_level_str = update_data["experience_level"]
        current_user.experience_level = ExperienceLevel(experience_level_str)
        logger.info(
            f"Experience level updated for user {current_user.user_id}: {experience_level_str}"
        )

    # Save changes
    await db_session.commit()
    await db_session.refresh(current_user)

    logger.info(f"Profile updated successfully for user: {current_user.email}")
    return UserResponse.model_validate(current_user)


@router.put(
    "/password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change current user's password"
)
async def change_password(
    password_change: PasswordChange,
    current_user: CurrentUser,
    db_session: DatabaseSession
) -> dict:
    """
    Change user password.

    Requires:
    - Current password (for verification)
    - New password (must meet strength requirements)

    Password requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number

    Security:
    - Verifies current password before allowing change
    - Validates new password strength
    - Hashes password with bcrypt

    Returns success message on completion.
    """
    # Verify current password
    if not verify_password(password_change.current_password, current_user.password_hash):
        logger.warning(
            f"Password change failed - incorrect current password",
            extra={"user_id": current_user.user_id, "email": current_user.email}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    is_valid, error_message = validate_password_strength(password_change.new_password)
    if not is_valid:
        logger.warning(
            f"Password change failed - weak password",
            extra={"user_id": current_user.user_id, "reason": error_message}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Update password
    current_user.password_hash = hash_password(password_change.new_password)
    await db_session.commit()

    logger.info(f"Password changed successfully for user: {current_user.email}")

    return {
        "message": "Password changed successfully",
        "email": current_user.email
    }
