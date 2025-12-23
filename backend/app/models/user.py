"""
User model for YogaFlow application.
Handles user authentication and profile information.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ExperienceLevel(str, enum.Enum):
    """User experience levels for yoga practice."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class User(Base):
    """
    User model for authentication and profile management.

    Attributes:
        user_id: Primary key
        email: Unique email address (indexed for performance)
        password_hash: Bcrypt hashed password (never store plaintext)
        name: User's full name
        experience_level: Yoga experience level (beginner/intermediate/advanced)
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp
        email_verified: Email verification status
        email_verification_token: Token for email verification
        email_verification_expires: Expiration time for verification token
        last_login: Last successful login timestamp
        is_active: Account active status (for soft deletes)
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    experience_level = Column(Enum(ExperienceLevel), default=ExperienceLevel.BEGINNER)
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow(), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Account security fields
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime, nullable=True)

    # Relationships
    practice_sessions = relationship("PracticeSession", back_populates="user", cascade="all, delete-orphan")
    custom_sequences = relationship("Sequence", back_populates="creator", cascade="all, delete-orphan")
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email='{self.email}', name='{self.name}')>"
