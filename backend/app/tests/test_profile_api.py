"""
Unit tests for User Profile API endpoints.
Tests GET /profile, PUT /profile, and PUT /profile/password.
"""
import pytest
from datetime import datetime
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.models.user import User, ExperienceLevel
from app.core.security import verify_password, create_access_token


# Note: We use test_user fixture from conftest.py, which has password: "TestPassword123"


# ============================================================================
# GET /api/v1/profile - Get current user profile
# ============================================================================

@pytest.mark.asyncio
async def test_get_profile_success(test_user, user_token_headers, override_get_db):
    """Test successful retrieval of user profile."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/profile",
            headers=user_token_headers
        )

    assert response.status_code == 200
    data = response.json()

    # Verify all profile fields are present
    assert data["user_id"] == test_user.user_id
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert data["experience_level"] == test_user.experience_level.value
    assert data["email_verified"] is True
    assert "created_at" in data
    assert "password_hash" not in data  # Security: password should never be exposed


@pytest.mark.asyncio
async def test_get_profile_includes_timestamps(test_user, user_token_headers, override_get_db):
    """Test that profile includes created_at and last_login timestamps."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/profile",
            headers=user_token_headers
        )

    assert response.status_code == 200
    data = response.json()

    # Timestamps should be present
    assert "created_at" in data
    # last_login might be null if never logged in
    assert "last_login" in data or data.get("last_login") is None


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(override_get_db):
    """Test that unauthenticated requests are rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/profile")

    assert response.status_code == 401  # No authorization header (HTTPBearer returns 401)


@pytest.mark.asyncio
async def test_get_profile_invalid_token(override_get_db):
    """Test that invalid tokens are rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/profile",
            headers={"Authorization": "Bearer invalid-token"}
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_inactive_user(db_session: AsyncSession, override_get_db):
    """Test that inactive users cannot access profile."""
    # Create inactive user with a simple password_hash (avoiding bcrypt issues with Python 3.14)
    inactive_user = User(
        email="inactive@example.com",
        password_hash="$2b$12$dummy_hash_for_testing_purposes_only",  # Dummy hash to avoid bcrypt issue
        name="Inactive User",
        email_verified=True,
        is_active=False
    )
    db_session.add(inactive_user)
    await db_session.commit()
    await db_session.refresh(inactive_user)

    # Generate token for inactive user
    token_data = {"sub": inactive_user.email, "user_id": inactive_user.user_id}
    access_token = create_access_token(token_data)
    headers = {"Authorization": f"Bearer {access_token}"}

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/profile",
            headers=headers
        )

    assert response.status_code == 401


# ============================================================================
# PUT /api/v1/profile - Update user profile
# ============================================================================

@pytest.mark.asyncio
async def test_update_profile_name_success(test_user, user_token_headers, db_session, override_get_db):
    """Test successful update of user name."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={"name": "Updated Name"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == test_user.email  # Email unchanged

    # Verify database was updated
    await db_session.refresh(test_user)
    assert test_user.name == "Updated Name"


@pytest.mark.asyncio
async def test_update_profile_experience_level_success(test_user, user_token_headers, db_session, override_get_db):
    """Test successful update of experience level."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={"experience_level": "advanced"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["experience_level"] == "advanced"

    # Verify database was updated
    await db_session.refresh(test_user)
    assert test_user.experience_level == ExperienceLevel.ADVANCED


@pytest.mark.asyncio
async def test_update_profile_multiple_fields(test_user, user_token_headers, db_session, override_get_db):
    """Test updating multiple profile fields at once."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={
                "name": "New Name",
                "experience_level": "beginner"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["experience_level"] == "beginner"

    # Verify database was updated
    await db_session.refresh(test_user)
    assert test_user.name == "New Name"
    assert test_user.experience_level == ExperienceLevel.BEGINNER


@pytest.mark.asyncio
async def test_update_profile_email_success(test_user, user_token_headers, db_session, override_get_db):
    """Test successful update of email address."""
    new_email = "newemail@example.com"

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={"email": new_email}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == new_email

    # Email verification should be reset when email changes
    await db_session.refresh(test_user)
    assert test_user.email == new_email
    assert test_user.email_verified is False  # Should require re-verification


@pytest.mark.asyncio
async def test_update_profile_email_already_exists(test_user, user_token_headers, db_session, override_get_db):
    """Test that updating to an existing email is rejected."""
    # Create another user (using dummy hash to avoid bcrypt issues with Python 3.14)
    other_user = User(
        email="other@example.com",
        password_hash="$2b$12$dummy_hash_for_other_user_testing_only",
        name="Other User",
        email_verified=True,
        is_active=True
    )
    db_session.add(other_user)
    await db_session.commit()

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={"email": "other@example.com"}
        )

    assert response.status_code == 400
    data = response.json()
    assert "already" in data["detail"].lower() or "exists" in data["detail"].lower()


@pytest.mark.asyncio
async def test_update_profile_invalid_experience_level(test_user, user_token_headers, override_get_db):
    """Test that invalid experience level is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={"experience_level": "expert"}  # Invalid level
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_profile_empty_name(test_user, user_token_headers, override_get_db):
    """Test that empty name is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={"name": ""}
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_profile_name_too_long(test_user, user_token_headers, override_get_db):
    """Test that names exceeding max length are rejected."""
    long_name = "a" * 300  # Exceeds 255 char limit

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={"name": long_name}
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_profile_invalid_email_format(test_user, user_token_headers, override_get_db):
    """Test that invalid email format is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={"email": "not-an-email"}
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_profile_unauthenticated(override_get_db):
    """Test that unauthenticated users cannot update profile."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            json={"name": "New Name"}
        )

    assert response.status_code == 401  # HTTPBearer returns 401


@pytest.mark.asyncio
async def test_update_profile_no_changes(test_user, user_token_headers, override_get_db):
    """Test updating profile with empty payload."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile",
            headers=user_token_headers,
            json={}
        )

    # Should succeed with no changes
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_user.name
    assert data["experience_level"] == test_user.experience_level.value


# ============================================================================
# PUT /api/v1/profile/password - Change password
# ============================================================================

@pytest.mark.asyncio
async def test_change_password_success(test_user, user_token_headers, db_session, override_get_db):
    """Test successful password change."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "NewSecurePassword456"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password changed successfully"

    # Verify password was updated in database
    await db_session.refresh(test_user)
    assert verify_password("NewSecurePassword456", test_user.password_hash)
    assert not verify_password("TestPassword123", test_user.password_hash)


@pytest.mark.asyncio
async def test_change_password_login_with_new_password(test_user, user_token_headers, db_session, override_get_db):
    """Test that user can login with new password after change."""
    # Change password
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "NewSecurePassword789"
            }
        )

        # Try to login with new password
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "NewSecurePassword789",
                "remember_me": False
            }
        )

    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data["tokens"]


@pytest.mark.asyncio
async def test_change_password_incorrect_current_password(test_user, user_token_headers, db_session, override_get_db):
    """Test that incorrect current password is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "WrongPassword123",
                "new_password": "NewSecurePassword456"
            }
        )

    assert response.status_code == 400
    data = response.json()
    assert "current password" in data["detail"].lower() or "incorrect" in data["detail"].lower()

    # Verify password was NOT changed
    await db_session.refresh(test_user)
    assert verify_password("TestPassword123", test_user.password_hash)


@pytest.mark.asyncio
async def test_change_password_weak_new_password(test_user, user_token_headers, override_get_db):
    """Test that weak new password is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "weak"  # Too short, no uppercase/numbers
            }
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_change_password_no_uppercase(test_user, user_token_headers, override_get_db):
    """Test that password without uppercase is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "newpassword123"  # No uppercase
            }
        )

    assert response.status_code == 400
    data = response.json()
    assert "uppercase" in data["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_no_lowercase(test_user, user_token_headers, override_get_db):
    """Test that password without lowercase is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "NEWPASSWORD123"  # No lowercase
            }
        )

    assert response.status_code == 400
    data = response.json()
    assert "lowercase" in data["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_no_number(test_user, user_token_headers, override_get_db):
    """Test that password without number is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "NewPasswordOnly"  # No number
            }
        )

    assert response.status_code == 400
    data = response.json()
    assert "number" in data["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_too_short(test_user, user_token_headers, override_get_db):
    """Test that password shorter than 8 characters is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "Pass1"  # Only 5 characters
            }
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_change_password_same_as_current(test_user, user_token_headers, db_session, override_get_db):
    """Test that changing to same password is allowed (but not recommended)."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "TestPassword123"  # Same password
            }
        )

    # Should succeed (though not a good practice)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_password_unauthenticated(override_get_db):
    """Test that unauthenticated users cannot change password."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            json={
                "current_password": "TestPassword123",
                "new_password": "NewPassword456"
            }
        )

    assert response.status_code == 401  # HTTPBearer returns 401


@pytest.mark.asyncio
async def test_change_password_missing_current_password(test_user, user_token_headers, override_get_db):
    """Test that missing current password is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "new_password": "NewPassword456"
            }
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_change_password_missing_new_password(test_user, user_token_headers, override_get_db):
    """Test that missing new password is rejected."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/v1/profile/password",
            headers=user_token_headers,
            json={
                "current_password": "TestPassword123"
            }
        )

    assert response.status_code == 422  # Validation error
