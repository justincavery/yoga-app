"""
Pose model for YogaFlow application.
Represents individual yoga poses/asanas.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Enum, JSON, Text
import enum

from app.core.database import Base


class PoseCategory(str, enum.Enum):
    """Categories for organizing yoga poses."""
    STANDING = "standing"
    SEATED = "seated"
    BALANCING = "balancing"
    BACKBENDS = "backbends"
    FORWARD_BENDS = "forward_bends"
    TWISTS = "twists"
    INVERSIONS = "inversions"
    ARM_BALANCES = "arm_balances"
    RESTORATIVE = "restorative"


class DifficultyLevel(str, enum.Enum):
    """Difficulty levels for poses and sequences."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Pose(Base):
    """
    Pose model representing individual yoga positions.

    Attributes:
        pose_id: Primary key
        name_english: English name of the pose
        name_sanskrit: Sanskrit name of the pose
        category: Pose category (standing, seated, etc.)
        difficulty_level: Difficulty rating
        description: Detailed description of the pose
        instructions: Step-by-step instructions (JSON array)
        benefits: Health and wellness benefits
        contraindications: Safety warnings and precautions
        target_areas: Target muscle groups/body areas (JSON array)
        image_urls: URLs to pose images (JSON array, minimum 1)
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "poses"

    pose_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name_english = Column(String(255), nullable=False, index=True)
    name_sanskrit = Column(String(255), nullable=True, index=True)
    category = Column(Enum(PoseCategory), nullable=False, index=True)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False, index=True)
    description = Column(Text, nullable=False)
    instructions = Column(JSON, nullable=False)  # Array of step-by-step instructions
    benefits = Column(Text, nullable=True)
    contraindications = Column(Text, nullable=True)
    target_areas = Column(JSON, nullable=True)  # Array of target muscle groups
    image_urls = Column(JSON, nullable=False)  # Array of image URLs (minimum 1)
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow(), nullable=False)

    def __repr__(self) -> str:
        return f"<Pose(pose_id={self.pose_id}, name_english='{self.name_english}', name_sanskrit='{self.name_sanskrit}')>"
