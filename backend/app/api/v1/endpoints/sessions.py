"""
Practice Session API endpoints.

Provides endpoints for managing practice sessions:
- Starting sessions
- Completing sessions
- Pausing sessions
- Getting current active session
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel, Field

from app.api.dependencies import DatabaseSession, CurrentUser
from app.models.practice_session import PracticeSession, CompletionStatus
from app.models.sequence import Sequence
from app.core.rate_limit import authenticated_rate_limit

router = APIRouter()


# Request/Response Models
class StartSessionRequest(BaseModel):
    """Request to start a practice session."""
    sequence_id: Optional[int] = Field(None, description="Sequence to practice (optional for free practice)")


class CompleteSessionRequest(BaseModel):
    """Request to complete a practice session."""
    session_id: int = Field(..., description="Session ID to complete")
    duration_seconds: int = Field(..., ge=0, le=14400, description="Duration in seconds (max 4 hours)")
    poses_completed: Optional[int] = Field(None, ge=0, description="Number of poses completed")
    completion_status: Optional[str] = Field("completed", description="Status: completed, partial, or abandoned")


class PauseSessionRequest(BaseModel):
    """Request to pause a practice session."""
    duration_so_far: int = Field(..., ge=0, description="Duration so far in seconds")


class SessionResponse(BaseModel):
    """Practice session response."""
    session_id: int
    user_id: int
    sequence_id: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: int
    completion_status: str
    statistics: Optional[dict] = None

    class Config:
        from_attributes = True


@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
@authenticated_rate_limit
async def start_session(
    request: Request,
    session_request: StartSessionRequest,
    current_user: CurrentUser,
    db_session: DatabaseSession
):
    """
    Start a new practice session.

    - **sequence_id**: Optional sequence to practice. If omitted, creates a free practice session.

    Returns the newly created session with status "abandoned" (will be updated when completed).
    """
    # Validate sequence exists if provided
    if session_request.sequence_id is not None:
        result = await db_session.execute(
            select(Sequence).where(Sequence.sequence_id == session_request.sequence_id)
        )
        sequence = result.scalar_one_or_none()
        if not sequence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sequence with ID {session_request.sequence_id} not found"
            )

    # Create new session
    new_session = PracticeSession(
        user_id=current_user.user_id,
        sequence_id=session_request.sequence_id,
        started_at=datetime.now(timezone.utc),
        completion_status=CompletionStatus.ABANDONED,
        duration_seconds=0
    )

    db_session.add(new_session)
    await db_session.commit()
    await db_session.refresh(new_session)

    return SessionResponse(
        session_id=new_session.session_id,
        user_id=new_session.user_id,
        sequence_id=new_session.sequence_id,
        started_at=new_session.started_at,
        completed_at=new_session.completed_at,
        duration_seconds=new_session.duration_seconds,
        completion_status=new_session.completion_status.value
    )


@router.post("/complete", response_model=SessionResponse)
@authenticated_rate_limit
async def complete_session(
    request: Request,
    complete_request: CompleteSessionRequest,
    db_session: DatabaseSession,
    current_user: CurrentUser
):
    """
    Complete a practice session.

    - **session_id**: The session to complete
    - **duration_seconds**: Total duration of the practice in seconds
    - **poses_completed**: Number of poses completed (optional)
    - **completion_status**: Status (completed, partial, or abandoned)

    Updates the session with completion data and calculates statistics.
    """
    # Get the session
    result = await db_session.execute(
        select(PracticeSession).where(PracticeSession.session_id == complete_request.session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {complete_request.session_id} not found"
        )

    # Verify ownership
    if session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own sessions"
        )

    # Update session
    session.completed_at = datetime.now(timezone.utc)
    session.duration_seconds = complete_request.duration_seconds

    # Set completion status
    if complete_request.completion_status == "completed":
        session.completion_status = CompletionStatus.COMPLETED
    elif complete_request.completion_status == "partial":
        session.completion_status = CompletionStatus.PARTIAL
    elif complete_request.completion_status == "abandoned":
        session.completion_status = CompletionStatus.ABANDONED
    else:
        # Default to completed
        session.completion_status = CompletionStatus.COMPLETED

    await db_session.commit()
    await db_session.refresh(session)

    # Calculate user statistics
    stats = await calculate_user_statistics(current_user.user_id, db_session)

    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        sequence_id=session.sequence_id,
        started_at=session.started_at,
        completed_at=session.completed_at,
        duration_seconds=session.duration_seconds,
        completion_status=session.completion_status.value,
        statistics=stats
    )


@router.put("/{session_id}/pause", response_model=SessionResponse)
@authenticated_rate_limit
async def pause_session(
    request: Request,
    session_id: int,
    pause_request: PauseSessionRequest,
    db_session: DatabaseSession,
    current_user: CurrentUser
):
    """
    Pause a practice session.

    - **session_id**: The session to pause
    - **duration_so_far**: Duration practiced so far in seconds

    Updates the session's duration but keeps it active (can be resumed).
    """
    # Get the session
    result = await db_session.execute(
        select(PracticeSession).where(PracticeSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )

    # Verify ownership
    if session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only pause your own sessions"
        )

    # Update duration but don't mark as completed
    session.duration_seconds = pause_request.duration_so_far

    await db_session.commit()
    await db_session.refresh(session)

    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        sequence_id=session.sequence_id,
        started_at=session.started_at,
        completed_at=session.completed_at,
        duration_seconds=session.duration_seconds,
        completion_status=session.completion_status.value
    )


@router.get("/current", response_model=SessionResponse)
@authenticated_rate_limit
async def get_current_session(
    request: Request,
    db_session: DatabaseSession,
    current_user: CurrentUser
):
    """
    Get the current active practice session.

    Returns the most recent session that hasn't been completed (status is still "abandoned").
    This represents a session that was started but not yet finished.
    """
    # Get most recent active session (not completed)
    result = await db_session.execute(
        select(PracticeSession)
        .where(PracticeSession.user_id == current_user.user_id)
        .where(PracticeSession.completed_at.is_(None))
        .order_by(desc(PracticeSession.started_at))
        .limit(1)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found"
        )

    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        sequence_id=session.sequence_id,
        started_at=session.started_at,
        completed_at=session.completed_at,
        duration_seconds=session.duration_seconds,
        completion_status=session.completion_status.value
    )


async def calculate_user_statistics(user_id: int, db_session: AsyncSession) -> dict:
    """
    Calculate practice statistics for a user.

    Returns:
        dict: Statistics including total sessions, total time, average duration, completion rate
    """
    # Total completed sessions
    result = await db_session.execute(
        select(func.count(PracticeSession.session_id))
        .where(PracticeSession.user_id == user_id)
        .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
    )
    total_completed = result.scalar() or 0

    # Total practice time
    result = await db_session.execute(
        select(func.sum(PracticeSession.duration_seconds))
        .where(PracticeSession.user_id == user_id)
        .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
    )
    total_seconds = result.scalar() or 0

    # Average duration
    result = await db_session.execute(
        select(func.avg(PracticeSession.duration_seconds))
        .where(PracticeSession.user_id == user_id)
        .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
    )
    avg_duration = result.scalar() or 0

    # All sessions (for completion rate)
    result = await db_session.execute(
        select(func.count(PracticeSession.session_id))
        .where(PracticeSession.user_id == user_id)
    )
    total_sessions = result.scalar() or 0

    completion_rate = (total_completed / total_sessions * 100) if total_sessions > 0 else 0

    return {
        "total_sessions": total_completed,
        "total_practice_time_seconds": int(total_seconds),
        "average_duration_seconds": int(avg_duration),
        "completion_rate_percent": round(completion_rate, 1)
    }
