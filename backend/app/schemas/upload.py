"""
Pydantic schemas for file upload operations.
"""
from pydantic import BaseModel, Field


class ImageUploadResponse(BaseModel):
    """Response schema for image upload."""
    url: str = Field(..., description="URL to access the uploaded image")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    format: str = Field(..., description="Image format (JPEG, PNG, etc.)")
