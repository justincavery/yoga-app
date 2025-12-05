"""
Practice Session model for YogaFlow application.
Tracks user practice history and statistics.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CompletionStatus(str, enum.Enum):
    """Status of practice session completion."""
    COMPLETED = "completed"
    PARTIAL = "partial"
    ABANDONED = "abandoned"


class PracticeSession(Base):
    """
    Practice Session model tracking user practice history.

    Attributes:
        session_id: Primary key
        user_id: Foreign key to users table
        sequence_id: Foreign key to sequences table
        started_at: Session start timestamp
        completed_at: Session completion timestamp (null if abandoned)
        duration_seconds: Actual session duration in seconds
        completion_status: Status (completed/partial/abandoned)
    """
    __tablename__ = "practice_sessions"

    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_id = Column(Integer, ForeignKey("sequences.sequence_id", ondelete="SET NULL"), nullable=True, index=True)
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=False, default=0)
    completion_status = Column(Enum(CompletionStatus), nullable=False, default=CompletionStatus.ABANDONED)

    # Relationships
    user = relationship("User", back_populates="practice_sessions")
    sequence = relationship("Sequence", back_populates="practice_sessions")

    def __repr__(self) -> str:
        return f"<PracticeSession(session_id={self.session_id}, user_id={self.user_id}, status={self.completion_status})>"
