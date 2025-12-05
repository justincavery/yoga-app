"""
Service for handling file uploads and image processing.
"""
import os
import uuid
from pathlib import Path
from typing import Tuple
from PIL import Image
import io

from app.core.config import settings
from app.core.logging_config import logger


# Allowed image formats
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

# Image size limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_DIMENSION = 2000  # 2000px max width/height


class ImageUploadError(Exception):
    """Custom exception for image upload errors."""
    pass


def validate_image_file(filename: str, content_type: str, file_size: int) -> None:
    """
    Validate image file before processing.

    Args:
        filename: Original filename
        content_type: MIME type of the file
        file_size: Size of file in bytes

    Raises:
        ImageUploadError: If validation fails
    """
    # Check file extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ImageUploadError(
            f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check content type
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ImageUploadError(
            f"Invalid content type. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    # Check file size
    if file_size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise ImageUploadError(
            f"File too large. Maximum size: {max_size_mb}MB"
        )


def optimize_image(image_data: bytes, max_dimension: int = MAX_IMAGE_DIMENSION) -> Tuple[bytes, int, int, str]:
    """
    Optimize image by resizing and compressing.

    Args:
        image_data: Raw image bytes
        max_dimension: Maximum width or height in pixels

    Returns:
        Tuple of (optimized_bytes, width, height, format)

    Raises:
        ImageUploadError: If image processing fails
    """
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))

        # Get original dimensions
        original_width, original_height = image.size
        image_format = image.format or "JPEG"

        # Convert RGBA to RGB if needed (for JPEG)
        if image.mode in ("RGBA", "LA", "P"):
            # Create white background
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
            image = background

        # Resize if needed
        if max(original_width, original_height) > max_dimension:
            # Calculate new dimensions maintaining aspect ratio
            if original_width > original_height:
                new_width = max_dimension
                new_height = int(original_height * (max_dimension / original_width))
            else:
                new_height = max_dimension
                new_width = int(original_width * (max_dimension / original_height))

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.info(
                "Image resized",
                original_size=f"{original_width}x{original_height}",
                new_size=f"{new_width}x{new_height}"
            )
        else:
            new_width, new_height = original_width, original_height

        # Compress image
        output = io.BytesIO()
        if image_format.upper() in ("JPEG", "JPG"):
            image.save(output, format="JPEG", quality=85, optimize=True)
        elif image_format.upper() == "PNG":
            image.save(output, format="PNG", optimize=True)
        elif image_format.upper() == "WEBP":
            image.save(output, format="WEBP", quality=85)
        else:
            # Default to JPEG
            image.save(output, format="JPEG", quality=85, optimize=True)
            image_format = "JPEG"

        optimized_data = output.getvalue()

        logger.info(
            "Image optimized",
            original_size=len(image_data),
            optimized_size=len(optimized_data),
            compression_ratio=f"{len(optimized_data) / len(image_data):.2%}"
        )

        return optimized_data, new_width, new_height, image_format

    except Exception as error:
        logger.error("Image optimization failed", error=str(error))
        raise ImageUploadError(f"Failed to process image: {str(error)}")


async def save_image(
    filename: str,
    content_type: str,
    file_data: bytes
) -> Tuple[str, str, int, int, int, str]:
    """
    Save and optimize an uploaded image.

    Args:
        filename: Original filename
        content_type: MIME type
        file_data: Raw file bytes

    Returns:
        Tuple of (url, saved_filename, file_size, width, height, format)

    Raises:
        ImageUploadError: If save fails
    """
    # Validate file
    validate_image_file(filename, content_type, len(file_data))

    # Optimize image
    optimized_data, width, height, image_format = optimize_image(file_data)

    # Generate unique filename
    file_ext = Path(filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_directory) / "images"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = upload_dir / unique_filename
    try:
        with open(file_path, "wb") as file_object:
            file_object.write(optimized_data)

        logger.info(
            "Image saved",
            filename=unique_filename,
            path=str(file_path),
            size=len(optimized_data)
        )

        # Generate URL (for MVP, use local file path; in production use CDN)
        url = f"/uploads/images/{unique_filename}"

        return url, unique_filename, len(optimized_data), width, height, image_format

    except Exception as error:
        logger.error("Failed to save image", error=str(error))
        raise ImageUploadError(f"Failed to save image: {str(error)}")


async def delete_image(filename: str) -> bool:
    """
    Delete an uploaded image.

    Args:
        filename: Name of file to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        file_path = Path(settings.upload_directory) / "images" / filename
        if file_path.exists():
            file_path.unlink()
            logger.info("Image deleted", filename=filename)
            return True
        else:
            logger.warning("Image not found for deletion", filename=filename)
            return False
    except Exception as error:
        logger.error("Failed to delete image", filename=filename, error=str(error))
        return False
