"""
Pydantic schemas for Pose API endpoints.
Request and response models for pose operations.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.models.pose import PoseCategory, DifficultyLevel


class PoseBase(BaseModel):
    """Base schema for Pose with common fields."""
    name_english: str = Field(..., min_length=1, max_length=255, description="English name of the pose")
    name_sanskrit: Optional[str] = Field(None, max_length=255, description="Sanskrit name of the pose")
    category: PoseCategory = Field(..., description="Pose category")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    description: str = Field(..., min_length=1, description="Description of the pose")
    instructions: List[str] = Field(..., min_length=1, description="Step-by-step instructions")
    benefits: Optional[str] = Field(None, description="Health and wellness benefits")
    contraindications: Optional[str] = Field(None, description="Safety warnings and precautions")
    target_areas: Optional[List[str]] = Field(None, description="Target muscle groups or body areas")
    image_urls: List[str] = Field(..., min_length=1, description="URLs to pose images")


class PoseCreate(PoseBase):
    """Schema for creating a new pose."""

    @field_validator('instructions')
    @classmethod
    def validate_instructions(cls, instructions_value: List[str]) -> List[str]:
        """Validate that instructions are not empty."""
        if not instructions_value:
            raise ValueError("Instructions cannot be empty")
        for instruction in instructions_value:
            if not instruction.strip():
                raise ValueError("Instructions cannot contain empty strings")
        return instructions_value

    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, urls_value: List[str]) -> List[str]:
        """Validate that at least one image URL is provided."""
        if not urls_value:
            raise ValueError("At least one image URL is required")
        return urls_value


class PoseUpdate(BaseModel):
    """Schema for updating a pose. All fields are optional."""
    name_english: Optional[str] = Field(None, min_length=1, max_length=255)
    name_sanskrit: Optional[str] = Field(None, max_length=255)
    category: Optional[PoseCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    description: Optional[str] = Field(None, min_length=1)
    instructions: Optional[List[str]] = None
    benefits: Optional[str] = None
    contraindications: Optional[str] = None
    target_areas: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None


class PoseResponse(PoseBase):
    """Schema for pose responses."""
    pose_id: int = Field(..., description="Unique identifier for the pose")
    created_at: datetime = Field(..., description="Timestamp when pose was created")
    updated_at: datetime = Field(..., description="Timestamp when pose was last updated")

    model_config = {
        "from_attributes": True
    }


class PoseListResponse(BaseModel):
    """Schema for paginated list of poses."""
    poses: List[PoseResponse]
    total: int = Field(..., description="Total number of poses matching the criteria")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PoseSearchParams(BaseModel):
    """Query parameters for searching and filtering poses."""
    search: Optional[str] = Field(None, description="Search by name (English or Sanskrit)")
    category: Optional[PoseCategory] = Field(None, description="Filter by category")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Filter by difficulty level")
    target_area: Optional[str] = Field(None, description="Filter by target body area")
    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page (max 100)")
