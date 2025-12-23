"""
Unit tests for Practice Session tracking functionality.

Tests cover:
- Creating practice sessions
- Completing practice sessions
- Session history queries
- Session statistics
- User practice tracking
"""
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.practice_session import PracticeSession, CompletionStatus
from app.models.user import User
from app.models.sequence import Sequence


class TestPracticeSessionModel:
    """Test PracticeSession model and database operations."""

    @pytest.mark.asyncio
    async def test_create_practice_session(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test creating a practice session."""
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert session.session_id is not None
        assert session.user_id == test_user.user_id
        assert session.sequence_id == test_sequence.sequence_id
        assert session.completion_status == CompletionStatus.ABANDONED
        assert session.duration_seconds == 0
        assert session.completed_at is None

    @pytest.mark.asyncio
    async def test_complete_practice_session(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test completing a practice session."""
        started_at = datetime.utcnow()
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=started_at,
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()

        # Complete the session
        completed_at = started_at + timedelta(minutes=15)
        session.completed_at = completed_at
        session.duration_seconds = 900  # 15 minutes
        session.completion_status = CompletionStatus.COMPLETED
        await db_session.commit()
        await db_session.refresh(session)

        assert session.completion_status == CompletionStatus.COMPLETED
        assert session.duration_seconds == 900
        assert session.completed_at is not None

    @pytest.mark.asyncio
    async def test_partial_session(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test creating a partial (incomplete) session."""
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow() + timedelta(minutes=8),
            duration_seconds=480,  # 8 minutes (partial)
            completion_status=CompletionStatus.PARTIAL
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert session.completion_status == CompletionStatus.PARTIAL
        assert session.duration_seconds == 480

    @pytest.mark.asyncio
    async def test_session_relationships(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test relationships between session, user, and sequence."""
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            completion_status=CompletionStatus.COMPLETED,
            duration_seconds=900
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Test user relationship
        result = await db_session.execute(
            select(User).where(User.user_id == session.user_id)
        )
        user = result.scalar_one()
        assert user.email == test_user.email

        # Test sequence relationship
        result = await db_session.execute(
            select(Sequence).where(Sequence.sequence_id == session.sequence_id)
        )
        sequence = result.scalar_one()
        assert sequence.name == test_sequence.name


class TestPracticeSessionHistory:
    """Test practice session history queries."""

    @pytest.mark.asyncio
    async def test_get_user_sessions(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test retrieving all sessions for a user."""
        # Create multiple sessions
        sessions = []
        for i in range(3):
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.utcnow() - timedelta(days=i),
                completed_at=datetime.utcnow() - timedelta(days=i) + timedelta(minutes=15),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
            sessions.append(session)
        await db_session.commit()

        # Query user sessions
        result = await db_session.execute(
            select(PracticeSession)
            .where(PracticeSession.user_id == test_user.user_id)
            .order_by(PracticeSession.started_at.desc())
        )
        user_sessions = result.scalars().all()

        assert len(user_sessions) == 3
        # Most recent first
        assert user_sessions[0].started_at > user_sessions[1].started_at

    @pytest.mark.asyncio
    async def test_get_sessions_by_date_range(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test querying sessions within a date range."""
        now = datetime.utcnow()

        # Create sessions spanning different days
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
        start_date = now - timedelta(days=7)
        result = await db_session.execute(
            select(PracticeSession)
            .where(PracticeSession.user_id == test_user.user_id)
            .where(PracticeSession.started_at >= start_date)
        )
        sessions = result.scalars().all()

        assert len(sessions) == 1
        assert sessions[0].session_id == recent_session.session_id

    @pytest.mark.asyncio
    async def test_get_sessions_by_status(
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
            started_at=datetime.utcnow(),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        partial = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=450,
            completion_status=CompletionStatus.PARTIAL
        )
        abandoned = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=0,
            completion_status=CompletionStatus.ABANDONED
        )
        db_session.add_all([completed, partial, abandoned])
        await db_session.commit()

        # Query only completed sessions
        result = await db_session.execute(
            select(PracticeSession)
            .where(PracticeSession.user_id == test_user.user_id)
            .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
        )
        completed_sessions = result.scalars().all()

        assert len(completed_sessions) == 1
        assert completed_sessions[0].completion_status == CompletionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_sessions_by_sequence(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        custom_sequence: Sequence
    ):
        """Test filtering sessions by sequence."""
        # Create sessions for different sequences
        session1 = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        session2 = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=custom_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=600,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add_all([session1, session2])
        await db_session.commit()

        # Query sessions for specific sequence
        result = await db_session.execute(
            select(PracticeSession)
            .where(PracticeSession.sequence_id == test_sequence.sequence_id)
        )
        sequence_sessions = result.scalars().all()

        assert len(sequence_sessions) == 1
        assert sequence_sessions[0].sequence_id == test_sequence.sequence_id


class TestPracticeSessionStatistics:
    """Test practice session statistics calculations."""

    @pytest.mark.asyncio
    async def test_count_total_sessions(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test counting total completed sessions."""
        # Create multiple sessions
        for i in range(5):
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.utcnow() - timedelta(days=i),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        # Count total sessions
        result = await db_session.execute(
            select(func.count(PracticeSession.session_id))
            .where(PracticeSession.user_id == test_user.user_id)
            .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
        )
        total_sessions = result.scalar()

        assert total_sessions == 5

    @pytest.mark.asyncio
    async def test_calculate_total_practice_time(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test calculating total practice time."""
        # Create sessions with different durations
        durations = [900, 1200, 600]  # 15, 20, 10 minutes
        for duration in durations:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.utcnow(),
                duration_seconds=duration,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        # Calculate total time
        result = await db_session.execute(
            select(func.sum(PracticeSession.duration_seconds))
            .where(PracticeSession.user_id == test_user.user_id)
            .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
        )
        total_seconds = result.scalar()

        assert total_seconds == sum(durations)
        assert total_seconds == 2700  # 45 minutes total

    @pytest.mark.asyncio
    async def test_calculate_average_session_duration(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test calculating average session duration."""
        durations = [600, 900, 1200]  # 10, 15, 20 minutes
        for duration in durations:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.utcnow(),
                duration_seconds=duration,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        # Calculate average duration
        result = await db_session.execute(
            select(func.avg(PracticeSession.duration_seconds))
            .where(PracticeSession.user_id == test_user.user_id)
            .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
        )
        avg_duration = result.scalar()

        assert avg_duration == 900  # 15 minutes average

    @pytest.mark.asyncio
    async def test_get_sessions_per_day(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test grouping sessions by day."""
        now = datetime.utcnow()

        # Create sessions on different days
        for days_ago in [0, 0, 1, 2, 2, 2]:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=now - timedelta(days=days_ago),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        # Group by date (simplified - would use date_trunc in production)
        result = await db_session.execute(
            select(
                func.date(PracticeSession.started_at).label('practice_date'),
                func.count(PracticeSession.session_id).label('session_count')
            )
            .where(PracticeSession.user_id == test_user.user_id)
            .group_by('practice_date')
        )
        daily_counts = result.all()

        assert len(daily_counts) == 3  # 3 different days
        # Check that we have the expected distribution
        counts = sorted([row.session_count for row in daily_counts])
        assert counts == [2, 2, 3]  # 2 today, 2 day ago, 3 two days ago

    @pytest.mark.asyncio
    async def test_completion_rate(
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
                started_at=datetime.utcnow(),
                duration_seconds=900 if status == CompletionStatus.COMPLETED else 450,
                completion_status=status
            )
            db_session.add(session)
        await db_session.commit()

        # Count completed vs total
        result = await db_session.execute(
            select(func.count(PracticeSession.session_id))
            .where(PracticeSession.user_id == test_user.user_id)
        )
        total = result.scalar()

        result = await db_session.execute(
            select(func.count(PracticeSession.session_id))
            .where(PracticeSession.user_id == test_user.user_id)
            .where(PracticeSession.completion_status == CompletionStatus.COMPLETED)
        )
        completed = result.scalar()

        completion_rate = (completed / total) * 100
        assert total == 5
        assert completed == 3
        assert completion_rate == 60.0


class TestMultipleUsers:
    """Test session tracking with multiple users."""

    @pytest.mark.asyncio
    async def test_sessions_isolated_by_user(
        self,
        db_session: AsyncSession,
        test_user: User,
        intermediate_user: User,
        test_sequence: Sequence
    ):
        """Test that sessions are properly isolated by user."""
        # Create sessions for both users
        session1 = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        session2 = PracticeSession(
            user_id=intermediate_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=1200,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add_all([session1, session2])
        await db_session.commit()

        # Query each user's sessions
        result = await db_session.execute(
            select(PracticeSession)
            .where(PracticeSession.user_id == test_user.user_id)
        )
        user1_sessions = result.scalars().all()

        result = await db_session.execute(
            select(PracticeSession)
            .where(PracticeSession.user_id == intermediate_user.user_id)
        )
        user2_sessions = result.scalars().all()

        assert len(user1_sessions) == 1
        assert len(user2_sessions) == 1
        assert user1_sessions[0].duration_seconds == 900
        assert user2_sessions[0].duration_seconds == 1200


class TestCascadeDeletes:
    """Test cascade delete behavior."""

    @pytest.mark.asyncio
    async def test_delete_user_deletes_sessions(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test that deleting a user deletes their sessions."""
        # Create session for user
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add(session)
        await db_session.commit()

        session_id = session.session_id

        # Delete user
        await db_session.delete(test_user)
        await db_session.commit()

        # Verify session is deleted
        result = await db_session.execute(
            select(PracticeSession)
            .where(PracticeSession.session_id == session_id)
        )
        deleted_session = result.scalar_one_or_none()

        assert deleted_session is None

    @pytest.mark.asyncio
    async def test_delete_sequence_nullifies_sessions(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence
    ):
        """Test that deleting a sequence sets sequence_id to NULL in sessions."""
        # Create session
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add(session)
        await db_session.commit()

        session_id = session.session_id

        # Delete sequence
        await db_session.delete(test_sequence)
        await db_session.commit()

        # Verify session still exists but sequence_id is NULL
        result = await db_session.execute(
            select(PracticeSession)
            .where(PracticeSession.session_id == session_id)
        )
        updated_session = result.scalar_one()

        assert updated_session is not None
        assert updated_session.sequence_id is None
