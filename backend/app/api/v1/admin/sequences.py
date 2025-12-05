"""
Admin Sequence API endpoints for YogaFlow.
Handles admin CRUD operations for practice sequences.
"""
from fastapi import APIRouter, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.schemas.sequence import (
    SequenceCreate,
    SequenceUpdate,
    SequenceResponse,
    SequencePoseResponse,
)
from app.models.sequence import Sequence, SequencePose
from app.models.pose import Pose
from app.api.dependencies import DatabaseSession, AdminUser
from app.core.logging_config import logger

router = APIRouter(prefix="/admin/sequences", tags=["Admin - Sequences"])


@router.post(
    "",
    response_model=SequenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new sequence (admin only)",
    description="Create a new practice sequence. Requires admin authentication."
)
async def create_sequence(
    sequence_data: SequenceCreate,
    db_session: DatabaseSession,
    admin_user: AdminUser
) -> SequenceResponse:
    """
    Create a new practice sequence.

    Requires admin authentication.

    Request body should include:
    - name: Sequence name
    - description: Detailed description (optional)
    - difficulty_level: Difficulty level
    - duration_minutes: Estimated total duration
    - focus_area: Primary focus area
    - style: Yoga style
    - is_preset: Whether this is a preset sequence
    - poses: List of poses with position and duration (minimum 3)
    """
    # Verify all pose IDs exist
    pose_ids = [pose.pose_id for pose in sequence_data.poses]
    result = await db_session.execute(
        select(Pose).where(Pose.pose_id.in_(pose_ids))
    )
    existing_poses = result.scalars().all()
    existing_pose_ids = {pose.pose_id for pose in existing_poses}

    missing_pose_ids = set(pose_ids) - existing_pose_ids
    if missing_pose_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Poses not found: {sorted(missing_pose_ids)}"
        )

    # Create new sequence
    new_sequence = Sequence(
        name=sequence_data.name,
        description=sequence_data.description,
        difficulty_level=sequence_data.difficulty_level.value,
        duration_minutes=sequence_data.duration_minutes,
        focus_area=sequence_data.focus_area,
        style=sequence_data.style,
        is_preset=sequence_data.is_preset,
        created_by=None if sequence_data.is_preset else admin_user.user_id
    )

    db_session.add(new_sequence)
    await db_session.flush()

    # Add poses to sequence
    for pose_data in sequence_data.poses:
        sequence_pose = SequencePose(
            sequence_id=new_sequence.sequence_id,
            pose_id=pose_data.pose_id,
            position_order=pose_data.position_order,
            duration_seconds=pose_data.duration_seconds
        )
        db_session.add(sequence_pose)

    await db_session.commit()

    # Reload with poses
    query = (
        select(Sequence)
        .where(Sequence.sequence_id == new_sequence.sequence_id)
        .options(
            selectinload(Sequence.sequence_poses).selectinload(SequencePose.pose)
        )
    )
    result = await db_session.execute(query)
    new_sequence = result.scalar_one()

    # Build response with pose details
    pose_responses = []
    total_duration_seconds = 0

    for sequence_pose in new_sequence.sequence_poses:
        pose_response = SequencePoseResponse(
            sequence_pose_id=sequence_pose.sequence_pose_id,
            pose_id=sequence_pose.pose_id,
            position_order=sequence_pose.position_order,
            duration_seconds=sequence_pose.duration_seconds,
            pose=sequence_pose.pose
        )
        pose_responses.append(pose_response)
        total_duration_seconds += sequence_pose.duration_seconds

    logger.info(
        "Sequence created by admin",
        sequence_id=new_sequence.sequence_id,
        name=new_sequence.name,
        created_by=admin_user.email,
        pose_count=len(pose_responses)
    )

    return SequenceResponse(
        sequence_id=new_sequence.sequence_id,
        name=new_sequence.name,
        description=new_sequence.description,
        difficulty_level=new_sequence.difficulty_level,
        duration_minutes=new_sequence.duration_minutes,
        focus_area=new_sequence.focus_area,
        style=new_sequence.style,
        is_preset=new_sequence.is_preset,
        created_by=new_sequence.created_by,
        created_at=new_sequence.created_at,
        updated_at=new_sequence.updated_at,
        poses=pose_responses,
        total_duration_seconds=total_duration_seconds
    )


@router.put(
    "/{sequence_id}",
    response_model=SequenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update sequence (admin only)",
    description="Update an existing practice sequence. Requires admin authentication."
)
async def update_sequence(
    sequence_id: int,
    sequence_data: SequenceUpdate,
    db_session: DatabaseSession,
    admin_user: AdminUser
) -> SequenceResponse:
    """
    Update an existing practice sequence.

    Requires admin authentication.

    All fields in request body are optional - only provided fields will be updated.
    If poses are provided, all existing poses will be replaced with the new list.
    """
    # Get existing sequence
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

    # Update fields
    update_data = sequence_data.model_dump(exclude_unset=True, exclude={'poses'})

    # Convert difficulty_level enum to string if present
    if 'difficulty_level' in update_data and update_data['difficulty_level'] is not None:
        update_data['difficulty_level'] = update_data['difficulty_level'].value

    for field, value in update_data.items():
        setattr(sequence, field, value)

    # Update poses if provided
    if sequence_data.poses is not None:
        # Verify all pose IDs exist
        pose_ids = [pose.pose_id for pose in sequence_data.poses]
        result = await db_session.execute(
            select(Pose).where(Pose.pose_id.in_(pose_ids))
        )
        existing_poses = result.scalars().all()
        existing_pose_ids = {pose.pose_id for pose in existing_poses}

        missing_pose_ids = set(pose_ids) - existing_pose_ids
        if missing_pose_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Poses not found: {sorted(missing_pose_ids)}"
            )

        # Delete existing sequence poses
        for existing_pose in sequence.sequence_poses:
            await db_session.delete(existing_pose)
        await db_session.flush()

        # Add new poses
        for pose_data in sequence_data.poses:
            sequence_pose = SequencePose(
                sequence_id=sequence.sequence_id,
                pose_id=pose_data.pose_id,
                position_order=pose_data.position_order,
                duration_seconds=pose_data.duration_seconds
            )
            db_session.add(sequence_pose)

    await db_session.commit()

    # Reload with poses
    query = (
        select(Sequence)
        .where(Sequence.sequence_id == sequence_id)
        .options(
            selectinload(Sequence.sequence_poses).selectinload(SequencePose.pose)
        )
    )
    result = await db_session.execute(query)
    sequence = result.scalar_one()

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

    logger.info(
        "Sequence updated by admin",
        sequence_id=sequence_id,
        name=sequence.name,
        updated_by=admin_user.email,
        updated_fields=list(update_data.keys())
    )

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


@router.delete(
    "/{sequence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete sequence (admin only)",
    description="Delete a practice sequence. Requires admin authentication."
)
async def delete_sequence(
    sequence_id: int,
    db_session: DatabaseSession,
    admin_user: AdminUser
) -> None:
    """
    Delete a practice sequence.

    Requires admin authentication.

    This will permanently remove the sequence from the database.
    Associated sequence_poses will be cascade deleted.
    Use with caution!
    """
    # Get existing sequence
    query = select(Sequence).where(Sequence.sequence_id == sequence_id)
    result = await db_session.execute(query)
    sequence = result.scalar_one_or_none()

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence with ID {sequence_id} not found"
        )

    sequence_name = sequence.name
    await db_session.delete(sequence)
    await db_session.commit()

    logger.info(
        "Sequence deleted by admin",
        sequence_id=sequence_id,
        name=sequence_name,
        deleted_by=admin_user.email
    )
