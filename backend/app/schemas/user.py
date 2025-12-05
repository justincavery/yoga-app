"""
Pydantic schemas for user-related requests and responses.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=255, description="User full name")
    experience_level: str = Field(default="beginner", description="Yoga experience level")


class UserRegister(UserBase):
    """Schema for user registration request."""
    password: str = Field(..., min_length=8, max_length=128, description="User password (min 8 chars, must contain uppercase, lowercase, and number)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "Jane Doe",
                "password": "SecurePass123",
                "experience_level": "beginner"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Extended session duration")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "remember_me": False
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = Field(None, description="User email address")
    experience_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "experience_level": "intermediate"
            }
        }
    )


class PasswordChange(BaseModel):
    """Schema for password change request."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "OldPass123",
                "new_password": "NewSecurePass456"
            }
        }
    )


class PasswordReset(BaseModel):
    """Schema for password reset request (forgot password)."""
    email: EmailStr = Field(..., description="Email address for password reset")


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset with token."""
    token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class UserResponse(UserBase):
    """Schema for user response (excludes sensitive data)."""
    user_id: int
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_id": 1,
                "email": "user@example.com",
                "name": "Jane Doe",
                "experience_level": "beginner",
                "email_verified": True,
                "created_at": "2025-01-15T10:30:00Z",
                "last_login": "2025-01-15T10:30:00Z"
            }
        }
    )


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token (if remember_me enabled)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }
    )


class AuthResponse(BaseModel):
    """Schema for complete authentication response."""
    user: UserResponse
    tokens: TokenResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
                    "user_id": 1,
                    "email": "user@example.com",
                    "name": "Jane Doe",
                    "experience_level": "beginner",
                    "email_verified": True,
                    "created_at": "2025-01-15T10:30:00Z",
                    "last_login": "2025-01-15T10:30:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 86400
                }
            }
        }
    )
