"""
User Favorites model for YogaFlow application.
Tracks user-saved sequences.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserFavorite(Base):
    """
    User Favorite model for tracking saved sequences.

    Attributes:
        favorite_id: Primary key
        user_id: Foreign key to users table
        sequence_id: Foreign key to sequences table
        created_at: Timestamp when sequence was favorited
    """
    __tablename__ = "user_favorites"

    favorite_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_id = Column(Integer, ForeignKey("sequences.sequence_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="favorites")
    sequence = relationship("Sequence", back_populates="favorites")

    def __repr__(self) -> str:
        return f"<UserFavorite(user_id={self.user_id}, sequence_id={self.sequence_id})>"
