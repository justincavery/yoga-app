"""
Unit tests for Practice History Service.

Tests the query functions and statistical analysis for practice sessions.
"""
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.practice_session import PracticeSession, CompletionStatus
from app.models.user import User
from app.models.sequence import Sequence
from app.services.practice_history import PracticeHistoryService


class TestPracticeHistoryQueries:
    """Test basic history query functions."""

    @pytest.mark.asyncio
    async def test_get_user_sessions_basic(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test retrieving user sessions."""
        # Create test sessions
        for i in range(3):
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.now(timezone.utc) - timedelta(days=i),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        sessions = await PracticeHistoryService.get_user_sessions(
            db_session, test_user.user_id
        )

        assert len(sessions) == 3
        # Should be ordered by most recent first
        assert sessions[0].started_at > sessions[1].started_at

    @pytest.mark.asyncio
    async def test_get_user_sessions_with_status_filter(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test filtering sessions by completion status."""
        # Create sessions with different statuses
        completed = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        partial = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc),
            duration_seconds=450,
            completion_status=CompletionStatus.PARTIAL
        )
        db_session.add_all([completed, partial])
        await db_session.commit()

        sessions = await PracticeHistoryService.get_user_sessions(
            db_session, test_user.user_id, status=CompletionStatus.COMPLETED
        )

        assert len(sessions) == 1
        assert sessions[0].completion_status == CompletionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_user_sessions_with_date_range(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test filtering sessions by date range."""
        now = datetime.now(timezone.utc)

        # Create sessions at different times
        old_session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=now - timedelta(days=10),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        recent_session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=now - timedelta(days=2),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add_all([old_session, recent_session])
        await db_session.commit()

        # Query last 7 days
        sessions = await PracticeHistoryService.get_user_sessions(
            db_session,
            test_user.user_id,
            start_date=now - timedelta(days=7)
        )

        assert len(sessions) == 1
        assert sessions[0].started_at == recent_session.started_at

    @pytest.mark.asyncio
    async def test_get_user_sessions_pagination(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test pagination of session results."""
        # Create 10 sessions
        for i in range(10):
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.now(timezone.utc) - timedelta(hours=i),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        # Get first page
        page1 = await PracticeHistoryService.get_user_sessions(
            db_session, test_user.user_id, limit=5, offset=0
        )
        # Get second page
        page2 = await PracticeHistoryService.get_user_sessions(
            db_session, test_user.user_id, limit=5, offset=5
        )

        assert len(page1) == 5
        assert len(page2) == 5
        # No overlap
        assert page1[0].session_id != page2[0].session_id


class TestPracticeStatistics:
    """Test statistical analysis functions."""

    @pytest.mark.asyncio
    async def test_get_total_sessions(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test counting total sessions."""
        # Create sessions
        for i in range(5):
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.now(timezone.utc),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        total = await PracticeHistoryService.get_total_sessions(
            db_session, test_user.user_id
        )

        assert total == 5

    @pytest.mark.asyncio
    async def test_get_total_practice_time(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test calculating total practice time."""
        durations = [600, 900, 1200]  # 10, 15, 20 minutes
        for duration in durations:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.now(timezone.utc),
                duration_seconds=duration,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        total_time = await PracticeHistoryService.get_total_practice_time(
            db_session, test_user.user_id
        )

        assert total_time == sum(durations)
        assert total_time == 2700  # 45 minutes

    @pytest.mark.asyncio
    async def test_get_average_session_duration(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test calculating average session duration."""
        durations = [600, 900, 1200]
        for duration in durations:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.now(timezone.utc),
                duration_seconds=duration,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        avg_duration = await PracticeHistoryService.get_average_session_duration(
            db_session, test_user.user_id
        )

        assert avg_duration == 900.0  # 15 minutes average

    @pytest.mark.asyncio
    async def test_get_practice_streak_current(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test calculating current practice streak."""
        now = datetime.now(timezone.utc)

        # Create sessions for last 3 consecutive days
        for days_ago in [0, 1, 2]:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=now - timedelta(days=days_ago),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        streak = await PracticeHistoryService.get_practice_streak(
            db_session, test_user.user_id
        )

        assert streak == 3

    @pytest.mark.asyncio
    async def test_get_practice_streak_broken(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test streak calculation when streak is broken."""
        now = datetime.now(timezone.utc)

        # Last practice was 3 days ago (streak broken)
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=now - timedelta(days=3),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add(session)
        await db_session.commit()

        streak = await PracticeHistoryService.get_practice_streak(
            db_session, test_user.user_id
        )

        assert streak == 0

    @pytest.mark.asyncio
    async def test_get_practice_streak_no_sessions(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test streak calculation with no sessions."""
        streak = await PracticeHistoryService.get_practice_streak(
            db_session, test_user.user_id
        )

        assert streak == 0

    @pytest.mark.asyncio
    async def test_get_completion_rate(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test calculating completion rate."""
        # Create mix of completed and abandoned sessions
        statuses = [
            CompletionStatus.COMPLETED,
            CompletionStatus.COMPLETED,
            CompletionStatus.COMPLETED,
            CompletionStatus.PARTIAL,
            CompletionStatus.ABANDONED,
        ]
        for status in statuses:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.now(timezone.utc),
                duration_seconds=900 if status == CompletionStatus.COMPLETED else 450,
                completion_status=status
            )
            db_session.add(session)
        await db_session.commit()

        completion_rate = await PracticeHistoryService.get_completion_rate(
            db_session, test_user.user_id
        )

        assert completion_rate == 60.0  # 3 out of 5 = 60%

    @pytest.mark.asyncio
    async def test_get_sessions_by_date(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test grouping sessions by date."""
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=7)

        # Create sessions on different days
        for days_ago in [0, 0, 1, 2]:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=now - timedelta(days=days_ago),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        sessions_by_date = await PracticeHistoryService.get_sessions_by_date(
            db_session, test_user.user_id, start_date, now
        )

        # Should have 3 different dates
        assert len(sessions_by_date) == 3
        # Today should have 2 sessions
        today_key = now.date().isoformat()
        assert len(sessions_by_date[today_key]) == 2

    @pytest.mark.asyncio
    async def test_get_practice_frequency(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test getting practice frequency over time."""
        now = datetime.now(timezone.utc)

        # Create sessions
        for days_ago in [0, 0, 1, 5]:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=now - timedelta(days=days_ago),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        frequency = await PracticeHistoryService.get_practice_frequency(
            db_session, test_user.user_id, days=30
        )

        assert len(frequency) == 3  # 3 different days
        # Find today's entry
        today_entry = next(
            (f for f in frequency if f["date"] == now.date().isoformat()),
            None
        )
        assert today_entry is not None
        assert today_entry["sessions"] == 2

    @pytest.mark.asyncio
    async def test_get_most_practiced_sequences(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        custom_sequence: Sequence
    ):
        """Test getting most practiced sequences."""
        # Create sessions - more for test_sequence
        for i in range(3):
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.now(timezone.utc),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)

        # One session for custom_sequence
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=custom_sequence.sequence_id,
            started_at=datetime.now(timezone.utc),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add(session)
        await db_session.commit()

        most_practiced = await PracticeHistoryService.get_most_practiced_sequences(
            db_session, test_user.user_id, limit=5
        )

        assert len(most_practiced) == 2
        # test_sequence should be first (3 practices)
        assert most_practiced[0]["sequence_id"] == test_sequence.sequence_id
        assert most_practiced[0]["practice_count"] == 3
        # custom_sequence should be second (1 practice)
        assert most_practiced[1]["sequence_id"] == custom_sequence.sequence_id
        assert most_practiced[1]["practice_count"] == 1


class TestComprehensiveStatistics:
    """Test comprehensive statistics function."""

    @pytest.mark.asyncio
    async def test_get_user_statistics(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test getting comprehensive user statistics."""
        now = datetime.now(timezone.utc)

        # Create varied sessions
        sessions_data = [
            (now - timedelta(days=0), 900, CompletionStatus.COMPLETED),
            (now - timedelta(days=1), 1200, CompletionStatus.COMPLETED),
            (now - timedelta(days=2), 600, CompletionStatus.COMPLETED),
            (now - timedelta(days=40), 900, CompletionStatus.COMPLETED),
            (now - timedelta(days=1), 300, CompletionStatus.ABANDONED),
        ]

        for started_at, duration, status in sessions_data:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=started_at,
                duration_seconds=duration,
                completion_status=status
            )
            db_session.add(session)
        await db_session.commit()

        stats = await PracticeHistoryService.get_user_statistics(
            db_session, test_user.user_id
        )

        assert stats["total_sessions"] == 4  # 4 completed
        assert stats["total_practice_time_seconds"] == 3600  # 60 minutes
        assert stats["total_practice_time_hours"] == 1.0
        assert stats["average_session_duration_minutes"] == 15.0
        assert stats["current_streak_days"] == 3  # last 3 days
        assert stats["completion_rate_percentage"] == 80.0  # 4/5 = 80%
        assert stats["sessions_last_30_days"] == 3  # excludes the 40-day old one


class TestMultiUserIsolation:
    """Test that queries are properly isolated by user."""

    @pytest.mark.asyncio
    async def test_statistics_isolated_by_user(
        self,
        db_session: AsyncSession,
        test_user: User,
        intermediate_user: User,
        test_sequence: Sequence
    ):
        """Test that statistics are properly isolated by user."""
        # Create sessions for both users
        session1 = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        session2 = PracticeSession(
            user_id=intermediate_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc),
            duration_seconds=1200,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add_all([session1, session2])
        await db_session.commit()

        # Get stats for each user
        stats1 = await PracticeHistoryService.get_user_statistics(
            db_session, test_user.user_id
        )
        stats2 = await PracticeHistoryService.get_user_statistics(
            db_session, intermediate_user.user_id
        )

        assert stats1["total_sessions"] == 1
        assert stats2["total_sessions"] == 1
        assert stats1["total_practice_time_seconds"] == 900
        assert stats2["total_practice_time_seconds"] == 1200
