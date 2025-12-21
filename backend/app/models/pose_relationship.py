"""
Pose relationship model for YogaFlow application.
Represents relationships between poses (similar poses, progressions, etc.).
"""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class RelationshipType(str, enum.Enum):
    """Types of relationships between poses."""
    SIMILAR = "similar"
    PROGRESSION = "progression"


class PoseRelationship(Base):
    """
    PoseRelationship model representing connections between poses.

    Attributes:
        id: Primary key
        pose_id: Foreign key to the source pose
        related_pose_id: Foreign key to the related pose
        relationship_type: Type of relationship (similar or progression)
        created_at: Record creation timestamp
    """
    __tablename__ = "pose_relationships"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pose_id = Column(Integer, ForeignKey("poses.pose_id", ondelete="CASCADE"), nullable=False, index=True)
    related_pose_id = Column(Integer, ForeignKey("poses.pose_id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(Enum(RelationshipType), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    pose = relationship("Pose", foreign_keys=[pose_id])
    related_pose = relationship("Pose", foreign_keys=[related_pose_id])

    def __repr__(self) -> str:
        return f"<PoseRelationship(pose_id={self.pose_id}, related_pose_id={self.related_pose_id}, type='{self.relationship_type}')>"
