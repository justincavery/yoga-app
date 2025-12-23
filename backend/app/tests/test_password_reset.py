"""
Unit tests for Password Reset functionality.
Tests the forgot password and reset password flow.
"""
import pytest
from datetime import datetime, timedelta, timezone
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.services.email_service import generate_verification_token


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user with verified email."""
    user = User(
        email="testuser@example.com",
        password_hash=hash_password("OldPassword123"),
        name="Test User",
        email_verified=True,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def unverified_user(db_session: AsyncSession):
    """Create a test user with unverified email."""
    user = User(
        email="unverified@example.com",
        password_hash=hash_password("Password123"),
        name="Unverified User",
        email_verified=False,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_forgot_password_success(test_user, db_session: AsyncSession, override_get_db):
    """Test successful forgot password request."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password reset email sent"
    assert data["email"] == test_user.email

    # Verify token was set in database
    await db_session.refresh(test_user)
    assert test_user.password_reset_token is not None
    assert test_user.password_reset_expires is not None
    assert test_user.password_reset_expires > datetime.utcnow()


@pytest.mark.asyncio
async def test_forgot_password_nonexistent_email(override_get_db):
    """Test forgot password with non-existent email (should still return success for security)."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )

    # Should return success to prevent email enumeration attacks
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password reset email sent"


@pytest.mark.asyncio
async def test_forgot_password_invalid_email(override_get_db):
    """Test forgot password with invalid email format."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "not-an-email"}
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_forgot_password_unverified_user(unverified_user, db_session: AsyncSession, override_get_db):
    """Test forgot password for unverified user (should still work)."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": unverified_user.email}
        )

    assert response.status_code == 200

    # Token should still be set (users can reset password even if email not verified)
    await db_session.refresh(unverified_user)
    assert unverified_user.password_reset_token is not None


@pytest.mark.asyncio
async def test_reset_password_success(test_user, db_session: AsyncSession, override_get_db):
    """Test successful password reset with valid token."""
    # Set up reset token
    reset_token = generate_verification_token()
    test_user.password_reset_token = reset_token
    test_user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    await db_session.commit()

    new_password = "NewSecurePassword123"

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": new_password
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password reset successful"
    assert data["email"] == test_user.email

    # Verify password was changed
    await db_session.refresh(test_user)
    assert verify_password(new_password, test_user.password_hash)

    # Verify token was cleared
    assert test_user.password_reset_token is None
    assert test_user.password_reset_expires is None


@pytest.mark.asyncio
async def test_reset_password_invalid_token(override_get_db):
    """Test password reset with invalid token."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid-token",
                "new_password": "NewPassword123"
            }
        )

    assert response.status_code == 400
    data = response.json()
    assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()


@pytest.mark.asyncio
async def test_reset_password_expired_token(test_user, db_session: AsyncSession, override_get_db):
    """Test password reset with expired token."""
    # Set up expired reset token
    reset_token = generate_verification_token()
    test_user.password_reset_token = reset_token
    test_user.password_reset_expires = datetime.utcnow() - timedelta(hours=1)  # Expired
    await db_session.commit()

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewPassword123"
            }
        )

    assert response.status_code == 400
    data = response.json()
    assert "expired" in data["detail"].lower()


@pytest.mark.asyncio
async def test_reset_password_weak_password(test_user, db_session: AsyncSession, override_get_db):
    """Test password reset with weak password."""
    reset_token = generate_verification_token()
    test_user.password_reset_token = reset_token
    test_user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    await db_session.commit()

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "weak"  # Too short
            }
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_reset_password_used_token(test_user, db_session: AsyncSession, override_get_db):
    """Test that reset token can only be used once."""
    reset_token = generate_verification_token()
    test_user.password_reset_token = reset_token
    test_user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    await db_session.commit()

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # First reset should succeed
        response1 = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewPassword123"
            }
        )
        assert response1.status_code == 200

        # Second attempt with same token should fail
        response2 = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "AnotherPassword456"
            }
        )
        assert response2.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_login_after_reset(test_user, db_session: AsyncSession, override_get_db):
    """Test that user can login with new password after reset."""
    # Set up reset token
    reset_token = generate_verification_token()
    test_user.password_reset_token = reset_token
    test_user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    await db_session.commit()

    new_password = "NewSecurePassword789"

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Reset password
        reset_response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": new_password
            }
        )
        assert reset_response.status_code == 200

        # Try to login with new password
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": new_password,
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data["tokens"]


@pytest.mark.asyncio
async def test_forgot_password_rate_limiting(test_user, override_get_db):
    """Test that multiple forgot password requests don't spam emails."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # First request
        response1 = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email}
        )
        assert response1.status_code == 200

        # Immediate second request (should still succeed but may not send another email)
        response2 = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email}
        )
        assert response2.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_missing_fields(override_get_db):
    """Test password reset with missing required fields."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Missing new_password
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": "some-token"}
        )
        assert response.status_code == 422

        # Missing token
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={"new_password": "NewPassword123"}
        )
        assert response.status_code == 422
