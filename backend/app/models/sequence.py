"""
Sequence model for YogaFlow application.
Represents ordered collections of poses for practice sessions.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class FocusArea(str, enum.Enum):
    """Focus areas for practice sequences."""
    FLEXIBILITY = "flexibility"
    STRENGTH = "strength"
    RELAXATION = "relaxation"
    BALANCE = "balance"
    CORE = "core"
    ENERGY = "energy"


class YogaStyle(str, enum.Enum):
    """Yoga styles for sequences."""
    VINYASA = "vinyasa"
    YIN = "yin"
    RESTORATIVE = "restorative"
    HATHA = "hatha"
    POWER = "power"
    GENTLE = "gentle"


class Sequence(Base):
    """
    Sequence model representing ordered collections of poses.

    Attributes:
        sequence_id: Primary key
        name: Sequence name
        description: Detailed description
        difficulty_level: Overall difficulty rating
        duration_minutes: Estimated total duration
        focus_area: Primary focus (flexibility, strength, etc.)
        style: Yoga style (vinyasa, yin, etc.)
        is_preset: True for pre-built sequences, False for user-created
        created_by: User ID of creator (null for preset sequences)
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "sequences"

    sequence_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    difficulty_level = Column(Enum('beginner', 'intermediate', 'advanced', name='difficulty_enum'), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    focus_area = Column(Enum(FocusArea), nullable=False, index=True)
    style = Column(Enum(YogaStyle), nullable=False, index=True)
    is_preset = Column(Boolean, default=False, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow(), nullable=False)

    # Relationships
    creator = relationship("User", back_populates="custom_sequences")
    sequence_poses = relationship("SequencePose", back_populates="sequence", cascade="all, delete-orphan", order_by="SequencePose.position_order")
    favorites = relationship("UserFavorite", back_populates="sequence", cascade="all, delete-orphan")
    practice_sessions = relationship("PracticeSession", back_populates="sequence")

    def __repr__(self) -> str:
        return f"<Sequence(sequence_id={self.sequence_id}, name='{self.name}', is_preset={self.is_preset})>"


class SequencePose(Base):
    """
    Junction table for Sequence-Pose many-to-many relationship.
    Stores pose order and duration within a sequence.

    Attributes:
        sequence_pose_id: Primary key
        sequence_id: Foreign key to sequences table
        pose_id: Foreign key to poses table
        position_order: Order of pose in sequence (1-indexed)
        duration_seconds: Duration to hold this pose in seconds
    """
    __tablename__ = "sequence_poses"

    sequence_pose_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sequence_id = Column(Integer, ForeignKey("sequences.sequence_id", ondelete="CASCADE"), nullable=False, index=True)
    pose_id = Column(Integer, ForeignKey("poses.pose_id", ondelete="CASCADE"), nullable=False, index=True)
    position_order = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False, default=60)

    # Relationships
    sequence = relationship("Sequence", back_populates="sequence_poses")
    pose = relationship("Pose")

    def __repr__(self) -> str:
        return f"<SequencePose(sequence_id={self.sequence_id}, pose_id={self.pose_id}, order={self.position_order})>"
