"""
Practice History API endpoints for YogaFlow.
Handles history retrieval, statistics, and calendar view.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, status, Query
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import calendar

from app.schemas.practice_history import (
    PracticeHistoryResponse,
    PracticeStatisticsResponse,
    CalendarResponse,
    PracticeSessionWithSequence,
    CalendarMonthData,
    CalendarDayData,
)
from app.models.practice_session import PracticeSession, CompletionStatus
from app.models.sequence import Sequence
from app.api.dependencies import DatabaseSession, CurrentUser
from app.services.practice_history import PracticeHistoryService
from app.core.logging_config import logger

router = APIRouter(tags=["Practice History"])


@router.get(
    "/history",
    response_model=PracticeHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get practice session history",
    description="Get paginated list of practice sessions with optional filtering"
)
async def get_history(
    current_user: CurrentUser,
    db_session: DatabaseSession,
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    status_filter: Optional[CompletionStatus] = Query(None, alias="status", description="Filter by completion status"),
    start_date: Optional[datetime] = Query(None, description="Filter sessions after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter sessions before this date"),
) -> PracticeHistoryResponse:
    """
    Get practice session history for the current user.

    Query Parameters:
        - page: Page number (starts at 1)
        - page_size: Number of sessions per page (max 100)
        - status: Filter by completion status (completed, partial, abandoned)
        - start_date: Filter sessions after this date (ISO 8601 format)
        - end_date: Filter sessions before this date (ISO 8601 format)

    Returns:
        PracticeHistoryResponse with paginated sessions and metadata
    """
    logger.info(
        "Getting practice history",
        user_id=current_user.user_id,
        page=page,
        page_size=page_size,
        status=status_filter.value if status_filter else None
    )

    # Calculate offset
    offset = (page - 1) * page_size

    # Get sessions using service
    sessions = await PracticeHistoryService.get_user_sessions(
        db_session=db_session,
        user_id=current_user.user_id,
        limit=page_size,
        offset=offset,
        status=status_filter,
        start_date=start_date,
        end_date=end_date
    )

    # Get total count
    total = await PracticeHistoryService.get_total_sessions(
        db_session=db_session,
        user_id=current_user.user_id,
        status=status_filter,
        start_date=start_date,
        end_date=end_date
    )

    # Load sequence details for each session
    sessions_with_details = []
    for session in sessions:
        # Load sequence relationship
        await db_session.refresh(session, ["sequence"])

        session_dict = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "sequence_id": session.sequence_id,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "duration_seconds": session.duration_seconds,
            "completion_status": session.completion_status,
            "sequence_name": session.sequence.name,
            "sequence_difficulty": session.sequence.difficulty_level.value,
            "sequence_focus_area": session.sequence.focus_area.value,
        }
        sessions_with_details.append(PracticeSessionWithSequence(**session_dict))

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PracticeHistoryResponse(
        sessions=sessions_with_details,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/stats",
    response_model=PracticeStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get practice statistics",
    description="Get comprehensive practice statistics for the current user"
)
async def get_stats(
    current_user: CurrentUser,
    db_session: DatabaseSession,
) -> PracticeStatisticsResponse:
    """
    Get comprehensive practice statistics.

    Returns:
        PracticeStatisticsResponse with:
        - Total sessions completed
        - Total practice time (seconds and hours)
        - Average session duration
        - Current practice streak
        - Completion rate
        - Sessions in last 30 days
        - Most practiced sequences
    """
    logger.info("Getting practice statistics", user_id=current_user.user_id)

    # Get comprehensive statistics using service
    stats = await PracticeHistoryService.get_user_statistics(
        db_session=db_session,
        user_id=current_user.user_id
    )

    # Get most practiced sequences
    most_practiced = await PracticeHistoryService.get_most_practiced_sequences(
        db_session=db_session,
        user_id=current_user.user_id,
        limit=10
    )

    # Add most practiced sequences to stats
    stats["most_practiced_sequences"] = most_practiced

    return PracticeStatisticsResponse(**stats)


@router.get(
    "/calendar",
    response_model=CalendarResponse,
    status_code=status.HTTP_200_OK,
    summary="Get calendar view of practice history",
    description="Get practice sessions grouped by date for calendar visualization"
)
async def get_calendar(
    current_user: CurrentUser,
    db_session: DatabaseSession,
    start_date: Optional[datetime] = Query(None, description="Start date for calendar range"),
    end_date: Optional[datetime] = Query(None, description="End date for calendar range"),
) -> CalendarResponse:
    """
    Get practice history grouped by date for calendar view.

    Query Parameters:
        - start_date: Start of date range (defaults to 90 days ago)
        - end_date: End of date range (defaults to today)

    Returns:
        CalendarResponse with:
        - Practice data grouped by month and day
        - Total unique days practiced
    """
    logger.info("Getting calendar data", user_id=current_user.user_id)

    # Default date range: last 90 days
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        start_date = end_date - timedelta(days=90)

    # Get sessions grouped by date
    sessions_by_date = await PracticeHistoryService.get_sessions_by_date(
        db_session=db_session,
        user_id=current_user.user_id,
        start_date=start_date,
        end_date=end_date
    )

    # Group by month
    months_data = {}

    for date_str, sessions in sessions_by_date.items():
        date_obj = datetime.fromisoformat(date_str).date()
        month_key = (date_obj.year, date_obj.month)

        if month_key not in months_data:
            months_data[month_key] = {
                "year": date_obj.year,
                "month": date_obj.month,
                "days": []
            }

        # Calculate total duration for this day
        total_duration = sum(session.duration_seconds for session in sessions)

        day_data = CalendarDayData(
            practice_date=date_obj,
            session_count=len(sessions),
            total_duration_seconds=total_duration
        )

        months_data[month_key]["days"].append(day_data)

    # Convert to list of CalendarMonthData
    months = [
        CalendarMonthData(**month_data)
        for month_data in sorted(months_data.values(), key=lambda x: (x["year"], x["month"]))
    ]

    # Total unique days practiced
    total_days_practiced = len(sessions_by_date)

    return CalendarResponse(
        months=months,
        total_days_practiced=total_days_practiced
    )
