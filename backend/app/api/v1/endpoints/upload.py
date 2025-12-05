"""
File upload API endpoints for YogaFlow.
Handles image uploads with validation and optimization.
"""
from fastapi import APIRouter, status, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path

from app.schemas.upload import ImageUploadResponse
from app.services.upload_service import save_image, ImageUploadError, delete_image
from app.api.dependencies import AdminUser
from app.core.config import settings
from app.core.logging_config import logger

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post(
    "/image",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload image (admin only)",
    description="Upload and optimize an image. Returns CDN-ready URL."
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    admin_user: AdminUser = None
) -> ImageUploadResponse:
    """
    Upload and optimize an image.

    Requires admin authentication.

    Features:
    - File type validation (JPEG, PNG, WEBP)
    - Size validation (max 10MB)
    - Automatic image optimization
    - Resize to max 2000px dimension
    - Compression with quality optimization

    Returns URL to access the uploaded image.
    """
    try:
        # Read file data
        file_data = await file.read()

        # Save and optimize image
        url, saved_filename, file_size, width, height, image_format = await save_image(
            filename=file.filename or "image.jpg",
            content_type=file.content_type or "image/jpeg",
            file_data=file_data
        )

        logger.info(
            "Image uploaded",
            filename=saved_filename,
            original_filename=file.filename,
            uploaded_by=admin_user.email if admin_user else "anonymous"
        )

        return ImageUploadResponse(
            url=url,
            filename=saved_filename,
            size=file_size,
            width=width,
            height=height,
            format=image_format
        )

    except ImageUploadError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    except Exception as error:
        logger.error("Image upload failed", error=str(error))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )


@router.get(
    "/images/{filename}",
    response_class=FileResponse,
    summary="Get uploaded image",
    description="Retrieve an uploaded image file"
)
async def get_image(filename: str) -> FileResponse:
    """
    Get an uploaded image file.

    Args:
        filename: Name of the image file

    Returns uploaded image file.
    """
    file_path = Path(settings.upload_directory) / "images" / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    return FileResponse(
        path=file_path,
        media_type="image/jpeg",  # Browser will determine actual type
        filename=filename
    )


@router.delete(
    "/images/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete image (admin only)",
    description="Delete an uploaded image file"
)
async def delete_image_endpoint(
    filename: str,
    admin_user: AdminUser
) -> None:
    """
    Delete an uploaded image.

    Requires admin authentication.

    Args:
        filename: Name of the image file to delete
    """
    success = await delete_image(filename)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    logger.info(
        "Image deleted",
        filename=filename,
        deleted_by=admin_user.email
    )
