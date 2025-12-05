"""
Achievement models for YogaFlow application.
Tracks badges and milestones for gamification (Phase 3).
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AchievementType(str, enum.Enum):
    """Types of achievements users can earn."""
    STREAK = "streak"  # Consecutive days practiced
    SESSIONS = "sessions"  # Total number of sessions
    TIME = "time"  # Total practice time
    MASTERY = "mastery"  # Trying all poses in a category


class Achievement(Base):
    """
    Achievement model defining available badges and milestones.

    Attributes:
        achievement_id: Primary key
        name: Achievement name (e.g., "7-Day Streak")
        description: Achievement description
        type: Achievement type (streak/sessions/time/mastery)
        threshold_value: Value required to unlock achievement
        icon_url: URL to achievement badge icon
    """
    __tablename__ = "achievements"

    achievement_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=False)
    type = Column(Enum(AchievementType), nullable=False, index=True)
    threshold_value = Column(Integer, nullable=False)
    icon_url = Column(String(500), nullable=True)

    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Achievement(achievement_id={self.achievement_id}, name='{self.name}', type={self.type})>"


class UserAchievement(Base):
    """
    User Achievement model tracking earned badges.

    Attributes:
        user_achievement_id: Primary key
        user_id: Foreign key to users table
        achievement_id: Foreign key to achievements table
        earned_at: Timestamp when achievement was earned
    """
    __tablename__ = "user_achievements"

    user_achievement_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.achievement_id", ondelete="CASCADE"), nullable=False, index=True)
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"
