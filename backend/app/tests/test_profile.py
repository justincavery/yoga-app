"""
Tests for profile management endpoints.
Tests profile viewing, updating, and password changes.
"""
import pytest
from httpx import AsyncClient
from app.core.security import hash_password


class TestGetProfile:
    """Tests for GET /api/v1/profile endpoint."""

    async def test_get_profile_success(self, async_client: AsyncClient, user_token_headers: dict):
        """Test successfully retrieving user profile."""
        headers = user_token_headers

        response = await async_client.get("/api/v1/profile", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["experience_level"] == "beginner"
        assert "user_id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should never be returned

    async def test_get_profile_without_auth(self, async_client: AsyncClient):
        """Test getting profile without authentication fails."""
        response = await async_client.get("/api/v1/profile")

        assert response.status_code == 401
        # Response might be just a string or have a detail field
        response_data = response.json()
        error_message = response_data if isinstance(response_data, str) else response_data.get("detail", "")
        assert "not authenticated" in error_message.lower()

    async def test_get_profile_with_invalid_token(self, async_client: AsyncClient):
        """Test getting profile with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_here"}

        response = await async_client.get("/api/v1/profile", headers=headers)

        assert response.status_code == 401


class TestUpdateProfile:
    """Tests for PUT /api/v1/profile endpoint."""

    async def test_update_profile_name(self, async_client: AsyncClient, user_token_headers: dict):
        """Test successfully updating user name."""
        headers = user_token_headers
        update_data = {"name": "Updated Name"}

        response = await async_client.put("/api/v1/profile", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "test@example.com"  # Email unchanged

    async def test_update_profile_experience_level(self, async_client: AsyncClient, user_token_headers: dict):
        """Test successfully updating experience level."""
        headers = user_token_headers
        update_data = {"experience_level": "intermediate"}

        response = await async_client.put("/api/v1/profile", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["experience_level"] == "intermediate"
        assert data["name"] == "Test User"  # Name unchanged

    async def test_update_profile_both_fields(self, async_client: AsyncClient, user_token_headers: dict):
        """Test updating both name and experience level."""
        headers = user_token_headers
        update_data = {
            "name": "Advanced Yogi",
            "experience_level": "advanced"
        }

        response = await async_client.put("/api/v1/profile", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Advanced Yogi"
        assert data["experience_level"] == "advanced"

    async def test_update_profile_empty_body(self, async_client: AsyncClient, user_token_headers: dict):
        """Test updating with empty body returns current profile."""
        headers = user_token_headers

        response = await async_client.put("/api/v1/profile", json={}, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test User"  # Unchanged
        assert data["experience_level"] == "beginner"  # Unchanged

    async def test_update_profile_invalid_experience_level(self, async_client: AsyncClient, user_token_headers: dict):
        """Test updating with invalid experience level fails."""
        headers = user_token_headers
        update_data = {"experience_level": "expert"}  # Not a valid option

        response = await async_client.put("/api/v1/profile", json=update_data, headers=headers)

        assert response.status_code == 422  # Validation error

    async def test_update_profile_without_auth(self, async_client: AsyncClient):
        """Test updating profile without authentication fails."""
        update_data = {"name": "Hacker"}

        response = await async_client.put("/api/v1/profile", json=update_data)

        assert response.status_code == 401

    async def test_update_profile_empty_name(self, async_client: AsyncClient, user_token_headers: dict):
        """Test updating with empty name fails."""
        headers = user_token_headers
        update_data = {"name": ""}

        response = await async_client.put("/api/v1/profile", json=update_data, headers=headers)

        assert response.status_code == 422  # Validation error


class TestChangePassword:
    """Tests for PUT /api/v1/profile/password endpoint."""

    async def test_change_password_success(self, async_client: AsyncClient, user_token_headers: dict):
        """Test successfully changing password."""
        headers = user_token_headers
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "NewPassword456"
        }

        response = await async_client.put("/api/v1/profile/password", json=password_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"
        assert data["email"] == "test@example.com"

        # Verify can login with new password
        login_data = {
            "email": "test@example.com",
            "password": "NewPassword456"
        }
        login_response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

    async def test_change_password_wrong_current_password(self, async_client: AsyncClient, user_token_headers: dict):
        """Test changing password with wrong current password fails."""
        headers = user_token_headers
        password_data = {
            "current_password": "WrongPassword123",
            "new_password": "NewPassword456"
        }

        response = await async_client.put("/api/v1/profile/password", json=password_data, headers=headers)

        assert response.status_code == 401
        assert "current password is incorrect" in response.json()["detail"].lower()

    async def test_change_password_too_short(self, async_client: AsyncClient, user_token_headers: dict):
        """Test changing to password that's too short fails."""
        headers = user_token_headers
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "Short1"
        }

        response = await async_client.put("/api/v1/profile/password", json=password_data, headers=headers)

        assert response.status_code == 400
        assert "at least 8 characters" in response.json()["detail"].lower()

    async def test_change_password_no_uppercase(self, async_client: AsyncClient, user_token_headers: dict):
        """Test changing to password without uppercase fails."""
        headers = user_token_headers
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "newpassword123"
        }

        response = await async_client.put("/api/v1/profile/password", json=password_data, headers=headers)

        assert response.status_code == 400
        assert "uppercase" in response.json()["detail"].lower()

    async def test_change_password_no_lowercase(self, async_client: AsyncClient, user_token_headers: dict):
        """Test changing to password without lowercase fails."""
        headers = user_token_headers
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "NEWPASSWORD123"
        }

        response = await async_client.put("/api/v1/profile/password", json=password_data, headers=headers)

        assert response.status_code == 400
        assert "lowercase" in response.json()["detail"].lower()

    async def test_change_password_no_number(self, async_client: AsyncClient, user_token_headers: dict):
        """Test changing to password without number fails."""
        headers = user_token_headers
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "NewPasswordOnly"
        }

        response = await async_client.put("/api/v1/profile/password", json=password_data, headers=headers)

        assert response.status_code == 400
        assert "number" in response.json()["detail"].lower()

    async def test_change_password_without_auth(self, async_client: AsyncClient):
        """Test changing password without authentication fails."""
        password_data = {
            "current_password": "TestPassword123",
            "new_password": "NewPassword456"
        }

        response = await async_client.put("/api/v1/profile/password", json=password_data)

        assert response.status_code == 401

    async def test_change_password_missing_current_password(self, async_client: AsyncClient, user_token_headers: dict):
        """Test changing password without current password fails."""
        headers = user_token_headers
        password_data = {
            "new_password": "NewPassword456"
        }

        response = await async_client.put("/api/v1/profile/password", json=password_data, headers=headers)

        assert response.status_code == 422  # Validation error

    async def test_change_password_missing_new_password(self, async_client: AsyncClient, user_token_headers: dict):
        """Test changing password without new password fails."""
        headers = user_token_headers
        password_data = {
            "current_password": "TestPassword123"
        }

        response = await async_client.put("/api/v1/profile/password", json=password_data, headers=headers)

        assert response.status_code == 422  # Validation error
