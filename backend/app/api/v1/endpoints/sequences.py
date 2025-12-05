"""
Sequence API endpoints for YogaFlow.
Handles CRUD operations, search, and filtering for practice sequences.
"""
from typing import Optional
from fastapi import APIRouter, status, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas.sequence import (
    SequenceResponse,
    SequenceListItem,
    SequenceListResponse,
    SequenceCategoriesResponse,
    FocusAreasResponse,
    StylesResponse,
    SequencePoseResponse,
)
from app.models.sequence import Sequence, SequencePose, FocusArea, YogaStyle
from app.models.pose import DifficultyLevel
from app.api.dependencies import DatabaseSession
from app.core.logging_config import logger

router = APIRouter(prefix="/sequences", tags=["Sequences"])


@router.get(
    "",
    response_model=SequenceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List sequences with pagination and filtering",
    description="Get a paginated list of sequences with optional search and filtering"
)
async def list_sequences(
    db_session: DatabaseSession,
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search by sequence name"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    focus_area: Optional[FocusArea] = Query(None, description="Filter by focus area"),
    style: Optional[YogaStyle] = Query(None, description="Filter by yoga style"),
    min_duration: Optional[int] = Query(None, ge=1, description="Minimum duration in minutes"),
    max_duration: Optional[int] = Query(None, ge=1, description="Maximum duration in minutes"),
    preset_only: Optional[bool] = Query(None, description="Show only preset sequences"),
) -> SequenceListResponse:
    """
    List all sequences with pagination, search, and filtering.

    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search by sequence name
    - difficulty: Filter by difficulty (beginner, intermediate, advanced)
    - focus_area: Filter by focus area (flexibility, strength, relaxation, balance, core, energy)
    - style: Filter by yoga style (vinyasa, yin, restorative, hatha, power, gentle)
    - min_duration: Minimum duration in minutes
    - max_duration: Maximum duration in minutes
    - preset_only: Show only preset sequences (true/false)

    Returns paginated list of sequences with total count and page information.
    """
    # Build base query with pose count
    query = select(
        Sequence,
        func.count(SequencePose.sequence_pose_id).label("pose_count")
    ).outerjoin(SequencePose).group_by(Sequence.sequence_id)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(Sequence.name.ilike(search_pattern))

    # Apply difficulty filter
    if difficulty:
        query = query.where(Sequence.difficulty_level == difficulty)

    # Apply focus area filter
    if focus_area:
        query = query.where(Sequence.focus_area == focus_area)

    # Apply style filter
    if style:
        query = query.where(Sequence.style == style)

    # Apply duration filters
    if min_duration:
        query = query.where(Sequence.duration_minutes >= min_duration)
    if max_duration:
        query = query.where(Sequence.duration_minutes <= max_duration)

    # Apply preset filter
    if preset_only is not None:
        query = query.where(Sequence.is_preset == preset_only)

    # Get total count before pagination
    count_subquery = query.subquery()
    count_query = select(func.count()).select_from(count_subquery)
    result = await db_session.execute(count_query)
    total = result.scalar() or 0

    # Apply pagination and ordering
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Sequence.name)

    # Execute query
    result = await db_session.execute(query)
    rows = result.all()

    # Build response items
    sequences = []
    for sequence, pose_count in rows:
        sequence_item = SequenceListItem(
            sequence_id=sequence.sequence_id,
            name=sequence.name,
            description=sequence.description,
            difficulty_level=sequence.difficulty_level,
            duration_minutes=sequence.duration_minutes,
            focus_area=sequence.focus_area,
            style=sequence.style,
            is_preset=sequence.is_preset,
            pose_count=pose_count or 0,
            created_at=sequence.created_at
        )
        sequences.append(sequence_item)

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    logger.info(
        "Sequences listed",
        total=total,
        page=page,
        page_size=page_size,
        filters={
            "search": search,
            "difficulty": difficulty.value if difficulty else None,
            "focus_area": focus_area.value if focus_area else None,
            "style": style.value if style else None,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "preset_only": preset_only
        }
    )

    return SequenceListResponse(
        sequences=sequences,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/categories",
    response_model=SequenceCategoriesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get sequences grouped by categories",
    description="Get counts of sequences grouped by difficulty, focus area, style, and duration ranges"
)
async def get_sequence_categories(
    db_session: DatabaseSession
) -> SequenceCategoriesResponse:
    """
    Get sequences grouped by various categories.

    Returns counts of sequences in each category:
    - By difficulty level (beginner, intermediate, advanced)
    - By focus area (flexibility, strength, relaxation, balance, core, energy)
    - By yoga style (vinyasa, yin, restorative, hatha, power, gentle)
    - By duration ranges (0-15, 16-30, 31-45, 46+ minutes)

    Useful for displaying category filters and sequence distribution.
    """
    # Get counts by difficulty
    difficulty_query = select(
        Sequence.difficulty_level,
        func.count(Sequence.sequence_id).label("count")
    ).group_by(Sequence.difficulty_level)
    result = await db_session.execute(difficulty_query)
    by_difficulty = {
        row.difficulty_level.value if hasattr(row.difficulty_level, 'value') else row.difficulty_level: row.count
        for row in result
    }

    # Get counts by focus area
    focus_query = select(
        Sequence.focus_area,
        func.count(Sequence.sequence_id).label("count")
    ).group_by(Sequence.focus_area)
    result = await db_session.execute(focus_query)
    by_focus_area = {
        row.focus_area.value if hasattr(row.focus_area, 'value') else row.focus_area: row.count
        for row in result
    }

    # Get counts by style
    style_query = select(
        Sequence.style,
        func.count(Sequence.sequence_id).label("count")
    ).group_by(Sequence.style)
    result = await db_session.execute(style_query)
    by_style = {
        row.style.value if hasattr(row.style, 'value') else row.style: row.count
        for row in result
    }

    # Get counts by duration ranges
    duration_ranges = {
        "0-15": (0, 15),
        "16-30": (16, 30),
        "31-45": (31, 45),
        "46+": (46, 999)
    }
    by_duration = {}
    for range_name, (min_dur, max_dur) in duration_ranges.items():
        duration_query = select(func.count(Sequence.sequence_id)).where(
            Sequence.duration_minutes >= min_dur,
            Sequence.duration_minutes <= max_dur
        )
        result = await db_session.execute(duration_query)
        by_duration[range_name] = result.scalar() or 0

    logger.info("Sequence categories retrieved")

    return SequenceCategoriesResponse(
        by_difficulty=by_difficulty,
        by_focus_area=by_focus_area,
        by_style=by_style,
        by_duration=by_duration
    )


@router.get(
    "/focus-areas",
    response_model=FocusAreasResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available focus areas",
    description="Get list of all available focus areas for sequences"
)
async def get_focus_areas() -> FocusAreasResponse:
    """
    Get list of available focus areas.

    Returns all possible focus areas that can be assigned to sequences:
    - flexibility
    - strength
    - relaxation
    - balance
    - core
    - energy

    Useful for populating filter dropdowns and category selections.
    """
    focus_areas = [area.value for area in FocusArea]

    logger.info("Focus areas retrieved", count=len(focus_areas))

    return FocusAreasResponse(focus_areas=focus_areas)


@router.get(
    "/styles",
    response_model=StylesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available yoga styles",
    description="Get list of all available yoga styles for sequences"
)
async def get_styles() -> StylesResponse:
    """
    Get list of available yoga styles.

    Returns all possible yoga styles that can be assigned to sequences:
    - vinyasa
    - yin
    - restorative
    - hatha
    - power
    - gentle

    Useful for populating filter dropdowns and category selections.
    """
    styles = [style.value for style in YogaStyle]

    logger.info("Yoga styles retrieved", count=len(styles))

    return StylesResponse(styles=styles)


@router.get(
    "/{sequence_id}",
    response_model=SequenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single sequence details",
    description="Get detailed information about a specific sequence including all poses"
)
async def get_sequence(
    sequence_id: int,
    db_session: DatabaseSession
) -> SequenceResponse:
    """
    Get detailed information about a specific sequence.

    Args:
        sequence_id: Unique identifier of the sequence

    Returns detailed sequence information including:
    - Name, description, and metadata
    - Difficulty level, duration, focus area, style
    - Complete list of poses with ordering and durations
    - Full pose details for each pose in the sequence
    """
    # Query sequence with poses eagerly loaded
    query = (
        select(Sequence)
        .where(Sequence.sequence_id == sequence_id)
        .options(
            selectinload(Sequence.sequence_poses).selectinload(SequencePose.pose)
        )
    )

    result = await db_session.execute(query)
    sequence = result.scalar_one_or_none()

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence with ID {sequence_id} not found"
        )

    # Build response with pose details
    pose_responses = []
    total_duration_seconds = 0

    for sequence_pose in sequence.sequence_poses:
        pose_response = SequencePoseResponse(
            sequence_pose_id=sequence_pose.sequence_pose_id,
            pose_id=sequence_pose.pose_id,
            position_order=sequence_pose.position_order,
            duration_seconds=sequence_pose.duration_seconds,
            pose=sequence_pose.pose
        )
        pose_responses.append(pose_response)
        total_duration_seconds += sequence_pose.duration_seconds

    logger.info("Sequence retrieved", sequence_id=sequence_id, name=sequence.name)

    return SequenceResponse(
        sequence_id=sequence.sequence_id,
        name=sequence.name,
        description=sequence.description,
        difficulty_level=sequence.difficulty_level,
        duration_minutes=sequence.duration_minutes,
        focus_area=sequence.focus_area,
        style=sequence.style,
        is_preset=sequence.is_preset,
        created_by=sequence.created_by,
        created_at=sequence.created_at,
        updated_at=sequence.updated_at,
        poses=pose_responses,
        total_duration_seconds=total_duration_seconds
    )
