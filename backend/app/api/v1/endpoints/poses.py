"""
Pose API endpoints for YogaFlow.
Handles CRUD operations, search, and filtering for yoga poses.
"""
from typing import Optional
from fastapi import APIRouter, status, HTTPException, Query, Request, Response
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
from app.core.rate_limit import public_rate_limit, authenticated_rate_limit

router = APIRouter(prefix="/poses", tags=["Poses"])


@router.get(
    "",
    response_model=PoseListResponse,
    status_code=status.HTTP_200_OK,
    summary="List poses with pagination and filtering",
    description="Get a paginated list of poses with optional search and filtering. Supports both page-based and offset-based pagination."
)
@public_rate_limit
async def list_poses(
    request: Request,
    response: Response,
    db_session: DatabaseSession,
    page: Optional[int] = Query(None, ge=1, description="Page number (starts at 1) - for page-based pagination"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Number of items per page (max 100) - for page-based pagination"),
    offset: Optional[int] = Query(None, ge=0, description="Number of items to skip - for offset-based pagination (infinite scroll)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of items to return (default: 20, max: 100) - for offset-based pagination"),
    search: Optional[str] = Query(None, description="Search by name (English or Sanskrit)"),
    category: Optional[PoseCategory] = Query(None, description="Filter by category"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    target_area: Optional[str] = Query(None, description="Filter by target body area"),
) -> PoseListResponse:
    """
    List all poses with pagination, search, and filtering.

    Supports two pagination modes:
    1. Page-based: Use 'page' and 'page_size' parameters
    2. Offset-based (for infinite scroll): Use 'offset' and 'limit' parameters

    Query Parameters:
    - page: Page number (default: 1) - optional for page-based pagination
    - page_size: Items per page (default: 20, max: 100) - optional for page-based pagination
    - offset: Number of items to skip (default: 0) - optional for offset-based pagination
    - limit: Maximum items to return (default: 20, max: 100) - optional for offset-based pagination
    - search: Search by pose name (English or Sanskrit)
    - category: Filter by category (standing, seated, balancing, etc.)
    - difficulty: Filter by difficulty (beginner, intermediate, advanced)
    - target_area: Filter by target body area

    Returns paginated list of poses with total count and page information.
    Response includes X-Total-Count header with total number of poses.
    """
    # Determine pagination mode and calculate offset/limit
    if offset is not None or limit is not None:
        # Offset-based pagination (infinite scroll)
        pagination_offset = offset if offset is not None else 0
        pagination_limit = limit if limit is not None else 20
        current_page = None
        current_page_size = None
    else:
        # Page-based pagination (traditional)
        current_page = page if page is not None else 1
        current_page_size = page_size if page_size is not None else 20
        pagination_offset = (current_page - 1) * current_page_size
        pagination_limit = current_page_size

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
    query = query.offset(pagination_offset).limit(pagination_limit)

    # Order by name for consistent results
    query = query.order_by(Pose.name_english)

    # Execute query
    result = await db_session.execute(query)
    poses = result.scalars().all()

    # Calculate total pages (only for page-based pagination)
    if current_page is not None:
        total_pages = (total + pagination_limit - 1) // pagination_limit if total > 0 else 0
    else:
        total_pages = None

    logger.info(
        "Poses listed",
        total=total,
        offset=pagination_offset,
        limit=pagination_limit,
        page=current_page,
        page_size=current_page_size,
        filters={
            "search": search,
            "category": category.value if category else None,
            "difficulty": difficulty.value if difficulty else None,
            "target_area": target_area
        }
    )

    # Add X-Total-Count header for infinite scroll
    response.headers["X-Total-Count"] = str(total)

    return PoseListResponse(
        poses=[PoseResponse.model_validate(pose) for pose in poses],
        total=total,
        page=current_page if current_page is not None else 1,
        page_size=pagination_limit,
        total_pages=total_pages if total_pages is not None else 0
    )


@router.get(
    "/{pose_id}",
    response_model=PoseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single pose details",
    description="Get detailed information about a specific pose"
)
@public_rate_limit
async def get_pose(
    request: Request,
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


@router.get(
    "/{pose_id}/related",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get related poses",
    description="Get similar poses and progression poses for a specific pose"
)
@public_rate_limit
async def get_related_poses(
    request: Request,
    pose_id: int,
    db_session: DatabaseSession
) -> dict:
    """
    Get related poses for a specific pose.

    Returns:
    - similar: List of 2 similar poses (same category, similar difficulty)
    - progressions: List of 2 progression poses (next difficulty level, related muscle groups)

    Algorithm for similar poses:
    - Same category
    - Similar difficulty level (same or ±1 level)
    - Different pose

    Algorithm for progression poses:
    - Related muscle groups (overlapping target_areas)
    - Higher difficulty level
    - Different pose
    """
    # First, verify the pose exists
    pose_query = select(Pose).where(Pose.pose_id == pose_id)
    result = await db_session.execute(pose_query)
    current_pose = result.scalar_one_or_none()

    if not current_pose:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pose with ID {pose_id} not found"
        )

    # Get similar poses (same category, similar difficulty)
    difficulty_map = {
        DifficultyLevel.BEGINNER: 0,
        DifficultyLevel.INTERMEDIATE: 1,
        DifficultyLevel.ADVANCED: 2
    }
    current_difficulty_level = difficulty_map.get(current_pose.difficulty_level, 1)

    # Build query for similar poses
    similar_query = select(Pose).where(
        Pose.pose_id != pose_id,
        Pose.category == current_pose.category
    )

    # Filter by similar difficulty (same or ±1 level)
    allowed_difficulties = []
    for diff, level in difficulty_map.items():
        if abs(level - current_difficulty_level) <= 1:
            allowed_difficulties.append(diff)

    if allowed_difficulties:
        similar_query = similar_query.where(Pose.difficulty_level.in_(allowed_difficulties))

    similar_query = similar_query.order_by(Pose.name_english).limit(2)
    result = await db_session.execute(similar_query)
    similar_poses = result.scalars().all()

    # Get progression poses (higher difficulty, related muscle groups)
    progression_query = select(Pose).where(
        Pose.pose_id != pose_id
    )

    # Filter by higher difficulty
    higher_difficulties = [diff for diff, level in difficulty_map.items() if level > current_difficulty_level]
    if higher_difficulties:
        progression_query = progression_query.where(Pose.difficulty_level.in_(higher_difficulties))
    else:
        # Already at max difficulty, just get similar difficulty different poses
        progression_query = progression_query.where(Pose.difficulty_level == current_pose.difficulty_level)

    # Order by difficulty and name for consistent results
    progression_query = progression_query.order_by(Pose.difficulty_level, Pose.name_english).limit(2)
    result = await db_session.execute(progression_query)
    progression_poses = result.scalars().all()

    logger.info(
        "Related poses retrieved",
        pose_id=pose_id,
        similar_count=len(similar_poses),
        progression_count=len(progression_poses)
    )

    return {
        "similar": [PoseResponse.model_validate(pose) for pose in similar_poses],
        "progressions": [PoseResponse.model_validate(pose) for pose in progression_poses]
    }


@router.post(
    "",
    response_model=PoseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new pose (admin only)",
    description="Create a new yoga pose. Requires admin authentication."
)
@authenticated_rate_limit
async def create_pose(
    request: Request,
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
@authenticated_rate_limit
async def update_pose(
    request: Request,
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
@authenticated_rate_limit
async def delete_pose(
    request: Request,
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
