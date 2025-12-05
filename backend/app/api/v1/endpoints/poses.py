"""
Pose API endpoints for YogaFlow.
Handles CRUD operations, search, and filtering for yoga poses.
"""
from typing import Optional
from fastapi import APIRouter, status, HTTPException, Query
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pose import (
    PoseCreate,
    PoseUpdate,
    PoseResponse,
    PoseListResponse,
)
from app.models.pose import Pose, PoseCategory, DifficultyLevel
from app.api.dependencies import DatabaseSession, AdminUser
from app.core.logging_config import logger

router = APIRouter(prefix="/poses", tags=["Poses"])


@router.get(
    "",
    response_model=PoseListResponse,
    status_code=status.HTTP_200_OK,
    summary="List poses with pagination and filtering",
    description="Get a paginated list of poses with optional search and filtering"
)
async def list_poses(
    db_session: DatabaseSession,
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search by name (English or Sanskrit)"),
    category: Optional[PoseCategory] = Query(None, description="Filter by category"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    target_area: Optional[str] = Query(None, description="Filter by target body area"),
) -> PoseListResponse:
    """
    List all poses with pagination, search, and filtering.

    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search by pose name (English or Sanskrit)
    - category: Filter by category (standing, seated, balancing, etc.)
    - difficulty: Filter by difficulty (beginner, intermediate, advanced)
    - target_area: Filter by target body area

    Returns paginated list of poses with total count and page information.
    """
    # Build query
    query = select(Pose)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Pose.name_english.ilike(search_pattern),
                Pose.name_sanskrit.ilike(search_pattern)
            )
        )

    # Apply category filter
    if category:
        query = query.where(Pose.category == category)

    # Apply difficulty filter
    if difficulty:
        query = query.where(Pose.difficulty_level == difficulty)

    # Apply target area filter
    if target_area:
        # JSON contains query for target_areas array
        query = query.where(Pose.target_areas.contains([target_area]))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db_session.execute(count_query)
    total = result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Order by name for consistent results
    query = query.order_by(Pose.name_english)

    # Execute query
    result = await db_session.execute(query)
    poses = result.scalars().all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    logger.info(
        "Poses listed",
        total=total,
        page=page,
        page_size=page_size,
        filters={
            "search": search,
            "category": category.value if category else None,
            "difficulty": difficulty.value if difficulty else None,
            "target_area": target_area
        }
    )

    return PoseListResponse(
        poses=[PoseResponse.model_validate(pose) for pose in poses],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{pose_id}",
    response_model=PoseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single pose details",
    description="Get detailed information about a specific pose"
)
async def get_pose(
    pose_id: int,
    db_session: DatabaseSession
) -> PoseResponse:
    """
    Get detailed information about a specific pose.

    Args:
        pose_id: Unique identifier of the pose

    Returns detailed pose information including:
    - Names (English and Sanskrit)
    - Category and difficulty level
    - Description and instructions
    - Benefits and contraindications
    - Target areas and images
    """
    query = select(Pose).where(Pose.pose_id == pose_id)
    result = await db_session.execute(query)
    pose = result.scalar_one_or_none()

    if not pose:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pose with ID {pose_id} not found"
        )

    logger.info("Pose retrieved", pose_id=pose_id, name=pose.name_english)

    return PoseResponse.model_validate(pose)


@router.post(
    "",
    response_model=PoseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new pose (admin only)",
    description="Create a new yoga pose. Requires admin authentication."
)
async def create_pose(
    pose_data: PoseCreate,
    db_session: DatabaseSession,
    admin_user: AdminUser
) -> PoseResponse:
    """
    Create a new yoga pose.

    Requires admin authentication.

    Request body should include:
    - name_english: English name of the pose
    - name_sanskrit: Sanskrit name (optional)
    - category: Pose category
    - difficulty_level: Difficulty level
    - description: Detailed description
    - instructions: Step-by-step instructions (array)
    - benefits: Health benefits (optional)
    - contraindications: Safety warnings (optional)
    - target_areas: Target body areas (array, optional)
    - image_urls: Image URLs (array, at least one required)
    """
    # Create new pose
    new_pose = Pose(
        name_english=pose_data.name_english,
        name_sanskrit=pose_data.name_sanskrit,
        category=pose_data.category,
        difficulty_level=pose_data.difficulty_level,
        description=pose_data.description,
        instructions=pose_data.instructions,
        benefits=pose_data.benefits,
        contraindications=pose_data.contraindications,
        target_areas=pose_data.target_areas,
        image_urls=pose_data.image_urls
    )

    db_session.add(new_pose)
    await db_session.commit()
    await db_session.refresh(new_pose)

    logger.info(
        "Pose created",
        pose_id=new_pose.pose_id,
        name=new_pose.name_english,
        created_by=admin_user.email
    )

    return PoseResponse.model_validate(new_pose)


@router.put(
    "/{pose_id}",
    response_model=PoseResponse,
    status_code=status.HTTP_200_OK,
    summary="Update pose (admin only)",
    description="Update an existing yoga pose. Requires admin authentication."
)
async def update_pose(
    pose_id: int,
    pose_data: PoseUpdate,
    db_session: DatabaseSession,
    admin_user: AdminUser
) -> PoseResponse:
    """
    Update an existing yoga pose.

    Requires admin authentication.

    All fields in request body are optional - only provided fields will be updated.
    """
    # Get existing pose
    query = select(Pose).where(Pose.pose_id == pose_id)
    result = await db_session.execute(query)
    pose = result.scalar_one_or_none()

    if not pose:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pose with ID {pose_id} not found"
        )

    # Update fields
    update_data = pose_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pose, field, value)

    await db_session.commit()
    await db_session.refresh(pose)

    logger.info(
        "Pose updated",
        pose_id=pose_id,
        name=pose.name_english,
        updated_by=admin_user.email,
        updated_fields=list(update_data.keys())
    )

    return PoseResponse.model_validate(pose)


@router.delete(
    "/{pose_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete pose (admin only)",
    description="Delete a yoga pose. Requires admin authentication."
)
async def delete_pose(
    pose_id: int,
    db_session: DatabaseSession,
    admin_user: AdminUser
) -> None:
    """
    Delete a yoga pose.

    Requires admin authentication.

    This will permanently remove the pose from the database.
    Use with caution!
    """
    # Get existing pose
    query = select(Pose).where(Pose.pose_id == pose_id)
    result = await db_session.execute(query)
    pose = result.scalar_one_or_none()

    if not pose:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pose with ID {pose_id} not found"
        )

    pose_name = pose.name_english
    await db_session.delete(pose)
    await db_session.commit()

    logger.info(
        "Pose deleted",
        pose_id=pose_id,
        name=pose_name,
        deleted_by=admin_user.email
    )
