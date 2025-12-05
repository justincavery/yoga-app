"""
Pydantic schemas for Sequence API endpoints.
Request and response models for sequence operations.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.sequence import FocusArea, YogaStyle
from app.models.pose import DifficultyLevel
from app.schemas.pose import PoseResponse


class SequencePoseBase(BaseModel):
    """Base schema for SequencePose."""
    pose_id: int = Field(..., description="ID of the pose")
    position_order: int = Field(..., ge=1, description="Position in sequence (1-indexed)")
    duration_seconds: int = Field(..., ge=10, le=600, description="Duration to hold pose in seconds")


class SequencePoseResponse(SequencePoseBase):
    """Schema for SequencePose in responses with full pose details."""
    sequence_pose_id: int = Field(..., description="Unique identifier for sequence-pose relationship")
    pose: PoseResponse = Field(..., description="Full pose details")

    model_config = {
        "from_attributes": True
    }


class SequenceBase(BaseModel):
    """Base schema for Sequence with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Sequence name")
    description: Optional[str] = Field(None, description="Detailed description")
    difficulty_level: DifficultyLevel = Field(..., description="Overall difficulty rating")
    duration_minutes: int = Field(..., ge=1, le=120, description="Estimated total duration in minutes")
    focus_area: FocusArea = Field(..., description="Primary focus area")
    style: YogaStyle = Field(..., description="Yoga style")


class SequenceCreate(SequenceBase):
    """Schema for creating a new sequence."""
    poses: List[SequencePoseBase] = Field(..., min_length=3, description="List of poses in sequence (minimum 3)")
    is_preset: bool = Field(False, description="Whether this is a preset sequence")


class SequenceUpdate(BaseModel):
    """Schema for updating a sequence. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=120)
    focus_area: Optional[FocusArea] = None
    style: Optional[YogaStyle] = None
    poses: Optional[List[SequencePoseBase]] = Field(None, min_length=3)


class SequenceResponse(SequenceBase):
    """Schema for sequence responses."""
    sequence_id: int = Field(..., description="Unique identifier for the sequence")
    is_preset: bool = Field(..., description="True for pre-built sequences, False for user-created")
    created_by: Optional[int] = Field(None, description="User ID of creator (null for preset sequences)")
    created_at: datetime = Field(..., description="Timestamp when sequence was created")
    updated_at: datetime = Field(..., description="Timestamp when sequence was last updated")
    poses: List[SequencePoseResponse] = Field(default_factory=list, description="Poses in this sequence")
    total_duration_seconds: int = Field(..., description="Total duration in seconds (calculated from poses)")

    model_config = {
        "from_attributes": True
    }


class SequenceListItem(BaseModel):
    """Schema for sequence in list view (without full pose details)."""
    sequence_id: int = Field(..., description="Unique identifier for the sequence")
    name: str = Field(..., description="Sequence name")
    description: Optional[str] = Field(None, description="Short description")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    duration_minutes: int = Field(..., description="Estimated duration in minutes")
    focus_area: FocusArea = Field(..., description="Primary focus area")
    style: YogaStyle = Field(..., description="Yoga style")
    is_preset: bool = Field(..., description="Whether this is a preset sequence")
    pose_count: int = Field(..., description="Number of poses in sequence")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {
        "from_attributes": True
    }


class SequenceListResponse(BaseModel):
    """Schema for paginated list of sequences."""
    sequences: List[SequenceListItem]
    total: int = Field(..., description="Total number of sequences matching the criteria")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class SequenceCategoriesResponse(BaseModel):
    """Schema for sequences grouped by categories."""
    by_difficulty: dict = Field(..., description="Count of sequences by difficulty level")
    by_focus_area: dict = Field(..., description="Count of sequences by focus area")
    by_style: dict = Field(..., description="Count of sequences by yoga style")
    by_duration: dict = Field(..., description="Count of sequences by duration ranges")


class FocusAreasResponse(BaseModel):
    """Schema for available focus areas."""
    focus_areas: List[str] = Field(..., description="List of available focus areas")


class StylesResponse(BaseModel):
    """Schema for available yoga styles."""
    styles: List[str] = Field(..., description="List of available yoga styles")
