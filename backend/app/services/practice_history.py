"""
Practice History Service for YogaFlow application.

Provides functions for querying and analyzing practice session history.
Implements history queries for statistics and analytics.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.sql import extract

from app.models.practice_session import PracticeSession, CompletionStatus
from app.models.sequence import Sequence
from app.models.user import User
from app.core.logging_config import logger


class PracticeHistoryService:
    """Service for querying and analyzing practice session history."""

    @staticmethod
    async def get_user_sessions(
        db_session: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        status: Optional[CompletionStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PracticeSession]:
        """
        Get practice sessions for a user with optional filtering.

        Args:
            db_session: Database session
            user_id: User ID to query sessions for
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            status: Optional completion status filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of PracticeSession objects
        """
        query = select(PracticeSession).where(PracticeSession.user_id == user_id)

        # Apply filters
        if status:
            query = query.where(PracticeSession.completion_status == status)

        if start_date:
            query = query.where(PracticeSession.started_at >= start_date)

        if end_date:
            query = query.where(PracticeSession.started_at <= end_date)

        # Order by most recent first
        query = query.order_by(desc(PracticeSession.started_at))

        # Apply pagination
        query = query.limit(limit).offset(offset)

        result = await db_session.execute(query)
        sessions = result.scalars().all()

        logger.info(
            "Retrieved user sessions",
            user_id=user_id,
            count=len(sessions),
            status=status.value if status else "all",
        )

        return sessions

    @staticmethod
    async def get_total_sessions(
        db_session: AsyncSession,
        user_id: int,
        status: Optional[CompletionStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        Count total practice sessions for a user.

        Args:
            db_session: Database session
            user_id: User ID to count sessions for
            status: Optional completion status filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Total number of sessions
        """
        query = select(func.count(PracticeSession.session_id)).where(
            PracticeSession.user_id == user_id
        )

        if status:
            query = query.where(PracticeSession.completion_status == status)

        if start_date:
            query = query.where(PracticeSession.started_at >= start_date)

        if end_date:
            query = query.where(PracticeSession.started_at <= end_date)

        result = await db_session.execute(query)
        total = result.scalar()

        logger.debug(
            "Counted total sessions",
            user_id=user_id,
            total=total,
            status=status.value if status else "all",
        )

        return total or 0

    @staticmethod
    async def get_total_practice_time(
        db_session: AsyncSession,
        user_id: int,
        status: Optional[CompletionStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        Calculate total practice time in seconds for a user.

        Args:
            db_session: Database session
            user_id: User ID to calculate time for
            status: Optional completion status filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Total practice time in seconds
        """
        query = select(func.sum(PracticeSession.duration_seconds)).where(
            PracticeSession.user_id == user_id
        )

        if status:
            query = query.where(PracticeSession.completion_status == status)

        if start_date:
            query = query.where(PracticeSession.started_at >= start_date)

        if end_date:
            query = query.where(PracticeSession.started_at <= end_date)

        result = await db_session.execute(query)
        total_seconds = result.scalar()

        logger.debug(
            "Calculated total practice time",
            user_id=user_id,
            total_seconds=total_seconds,
        )

        return total_seconds or 0

    @staticmethod
    async def get_average_session_duration(
        db_session: AsyncSession,
        user_id: int,
        status: Optional[CompletionStatus] = None,
    ) -> float:
        """
        Calculate average session duration for a user.

        Args:
            db_session: Database session
            user_id: User ID to calculate average for
            status: Optional completion status filter

        Returns:
            Average duration in seconds (0 if no sessions)
        """
        query = select(func.avg(PracticeSession.duration_seconds)).where(
            PracticeSession.user_id == user_id
        )

        if status:
            query = query.where(PracticeSession.completion_status == status)

        result = await db_session.execute(query)
        avg_duration = result.scalar()

        return float(avg_duration) if avg_duration else 0.0

    @staticmethod
    async def get_practice_streak(
        db_session: AsyncSession,
        user_id: int,
    ) -> int:
        """
        Calculate current practice streak (consecutive days with practice).

        Args:
            db_session: Database session
            user_id: User ID to calculate streak for

        Returns:
            Number of consecutive days with practice
        """
        # Get all completed sessions ordered by date (most recent first)
        result = await db_session.execute(
            select(func.date(PracticeSession.started_at).label("practice_date"))
            .where(PracticeSession.user_id == user_id)
            .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
            .group_by("practice_date")
            .order_by(desc("practice_date"))
        )
        practice_dates = [row.practice_date for row in result.all()]

        if not practice_dates:
            return 0

        # Check if user practiced today or yesterday
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        most_recent = practice_dates[0]
        if most_recent not in [today, yesterday]:
            return 0

        # Count consecutive days
        streak = 1
        expected_date = most_recent - timedelta(days=1)

        for practice_date in practice_dates[1:]:
            if practice_date == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            else:
                break

        logger.info("Calculated practice streak", user_id=user_id, streak=streak)
        return streak

    @staticmethod
    async def get_sessions_by_date(
        db_session: AsyncSession,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, List[PracticeSession]]:
        """
        Get sessions grouped by date for calendar view.

        Args:
            db_session: Database session
            user_id: User ID to query sessions for
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Dictionary mapping date strings to lists of sessions
        """
        result = await db_session.execute(
            select(PracticeSession)
            .where(PracticeSession.user_id == user_id)
            .where(PracticeSession.started_at >= start_date)
            .where(PracticeSession.started_at <= end_date)
            .order_by(PracticeSession.started_at)
        )
        sessions = result.scalars().all()

        # Group by date
        sessions_by_date: Dict[str, List[PracticeSession]] = {}
        for session in sessions:
            date_key = session.started_at.date().isoformat()
            if date_key not in sessions_by_date:
                sessions_by_date[date_key] = []
            sessions_by_date[date_key].append(session)

        return sessions_by_date

    @staticmethod
    async def get_practice_frequency(
        db_session: AsyncSession,
        user_id: int,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get practice frequency over the last N days.

        Args:
            db_session: Database session
            user_id: User ID to analyze
            days: Number of days to analyze

        Returns:
            List of dictionaries with date and session count
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = await db_session.execute(
            select(
                func.date(PracticeSession.started_at).label("practice_date"),
                func.count(PracticeSession.session_id).label("session_count"),
            )
            .where(PracticeSession.user_id == user_id)
            .where(PracticeSession.started_at >= start_date)
            .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
            .group_by("practice_date")
            .order_by("practice_date")
        )

        frequency_data = []
        for row in result.all():
            frequency_data.append(
                {
                    "date": row.practice_date.isoformat(),
                    "sessions": row.session_count,
                }
            )

        return frequency_data

    @staticmethod
    async def get_completion_rate(
        db_session: AsyncSession,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> float:
        """
        Calculate session completion rate.

        Args:
            db_session: Database session
            user_id: User ID to calculate rate for
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Completion rate as percentage (0-100)
        """
        total = await PracticeHistoryService.get_total_sessions(
            db_session, user_id, start_date=start_date, end_date=end_date
        )

        if total == 0:
            return 0.0

        completed = await PracticeHistoryService.get_total_sessions(
            db_session,
            user_id,
            status=CompletionStatus.COMPLETED,
            start_date=start_date,
            end_date=end_date,
        )

        completion_rate = (completed / total) * 100
        return round(completion_rate, 2)

    @staticmethod
    async def get_most_practiced_sequences(
        db_session: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get user's most practiced sequences.

        Args:
            db_session: Database session
            user_id: User ID to analyze
            limit: Maximum number of sequences to return

        Returns:
            List of sequences with practice counts
        """
        result = await db_session.execute(
            select(
                Sequence.sequence_id,
                Sequence.name,
                func.count(PracticeSession.session_id).label("practice_count"),
            )
            .join(PracticeSession, Sequence.sequence_id == PracticeSession.sequence_id)
            .where(PracticeSession.user_id == user_id)
            .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
            .group_by(Sequence.sequence_id, Sequence.name)
            .order_by(desc("practice_count"))
            .limit(limit)
        )

        most_practiced = []
        for row in result.all():
            most_practiced.append(
                {
                    "sequence_id": row.sequence_id,
                    "name": row.name,
                    "practice_count": row.practice_count,
                }
            )

        return most_practiced

    @staticmethod
    async def get_user_statistics(
        db_session: AsyncSession,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a user.

        Args:
            db_session: Database session
            user_id: User ID to get statistics for

        Returns:
            Dictionary of user practice statistics
        """
        # Run all queries concurrently would be better in production
        total_sessions = await PracticeHistoryService.get_total_sessions(
            db_session, user_id, status=CompletionStatus.COMPLETED
        )

        total_time = await PracticeHistoryService.get_total_practice_time(
            db_session, user_id, status=CompletionStatus.COMPLETED
        )

        avg_duration = await PracticeHistoryService.get_average_session_duration(
            db_session, user_id, status=CompletionStatus.COMPLETED
        )

        streak = await PracticeHistoryService.get_practice_streak(db_session, user_id)

        completion_rate = await PracticeHistoryService.get_completion_rate(
            db_session, user_id
        )

        # Last 30 days stats
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_sessions = await PracticeHistoryService.get_total_sessions(
            db_session,
            user_id,
            status=CompletionStatus.COMPLETED,
            start_date=thirty_days_ago,
        )

        statistics = {
            "total_sessions": total_sessions,
            "total_practice_time_seconds": total_time,
            "total_practice_time_hours": round(total_time / 3600, 2),
            "average_session_duration_minutes": round(avg_duration / 60, 2),
            "current_streak_days": streak,
            "completion_rate_percentage": completion_rate,
            "sessions_last_30_days": recent_sessions,
        }

        logger.info("Retrieved user statistics", user_id=user_id, stats=statistics)
        return statistics
