"""
Integration tests for Practice History API endpoints.

Tests GET /api/v1/history, /api/v1/stats, and /api/v1/calendar endpoints.
"""
import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.sequence import Sequence
from app.models.practice_session import PracticeSession, CompletionStatus


class TestHistoryEndpoint:
    """Test GET /api/v1/history endpoint."""

    @pytest.mark.asyncio
    async def test_get_history_empty(
        self,
        async_client: AsyncClient,
        test_user: User,
        user_token_headers: dict
    ):
        """Test getting history when user has no sessions."""
        response = await async_client.get(
            "/api/v1/history",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total_pages"] == 0

    @pytest.mark.asyncio
    async def test_get_history_basic(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test getting basic practice history."""
        # Create test sessions
        now = datetime.utcnow()
        for i in range(3):
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=now - timedelta(days=i),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/history",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 3
        assert data["total"] == 3
        # Should be ordered by most recent first
        sessions = data["sessions"]
        assert sessions[0]["started_at"] > sessions[1]["started_at"]

    @pytest.mark.asyncio
    async def test_get_history_pagination(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test history pagination."""
        # Create 25 sessions
        now = datetime.utcnow()
        for i in range(25):
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=now - timedelta(hours=i),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        # Test first page
        response = await async_client.get(
            "/api/v1/history?page=1&page_size=10",
            headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 3

        # Test second page
        response = await async_client.get(
            "/api/v1/history?page=2&page_size=10",
            headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 10
        assert data["page"] == 2

    @pytest.mark.asyncio
    async def test_get_history_date_filtering(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test filtering history by date range."""
        now = datetime.utcnow()

        # Create sessions at different times
        old_session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=now - timedelta(days=30),
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

        # Filter to last 7 days
        start_date = (now - timedelta(days=7)).isoformat()
        response = await async_client.get(
            f"/api/v1/history?start_date={start_date}",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 1
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_get_history_status_filtering(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test filtering history by completion status."""
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
        db_session.add_all([completed, partial])
        await db_session.commit()

        # Filter to only completed
        response = await async_client.get(
            "/api/v1/history?status=completed",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["completion_status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_history_includes_sequence_details(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test that history includes sequence details."""
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add(session)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/history",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        session_data = data["sessions"][0]
        assert "sequence_name" in session_data
        assert "sequence_difficulty" in session_data
        assert "sequence_focus_area" in session_data
        assert session_data["sequence_name"] == test_sequence.name

    @pytest.mark.asyncio
    async def test_get_history_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that history endpoint requires authentication."""
        response = await async_client.get("/api/v1/history")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_history_user_isolation(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        intermediate_user: User,
        test_sequence: Sequence,
        user_token_headers: dict,
        intermediate_user_token_headers: dict
    ):
        """Test that users can only see their own history."""
        # Create session for test_user
        session1 = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        # Create session for intermediate_user
        session2 = PracticeSession(
            user_id=intermediate_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=1200,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add_all([session1, session2])
        await db_session.commit()

        # Test user should only see their own session
        response = await async_client.get(
            "/api/v1/history",
            headers=user_token_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["user_id"] == test_user.user_id


class TestStatsEndpoint:
    """Test GET /api/v1/stats endpoint."""

    @pytest.mark.asyncio
    async def test_get_stats_empty(
        self,
        async_client: AsyncClient,
        test_user: User,
        user_token_headers: dict
    ):
        """Test getting stats when user has no sessions."""
        response = await async_client.get(
            "/api/v1/stats",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 0
        assert data["total_practice_time_seconds"] == 0
        assert data["total_practice_time_hours"] == 0.0
        assert data["average_session_duration_minutes"] == 0.0
        assert data["current_streak_days"] == 0
        assert data["completion_rate_percentage"] == 0.0
        assert data["sessions_last_30_days"] == 0
        assert data["most_practiced_sequences"] == []

    @pytest.mark.asyncio
    async def test_get_stats_comprehensive(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        custom_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test comprehensive statistics calculation."""
        now = datetime.utcnow()

        # Create varied sessions
        sessions_data = [
            (now - timedelta(days=0), 900, CompletionStatus.COMPLETED, test_sequence.sequence_id),
            (now - timedelta(days=1), 1200, CompletionStatus.COMPLETED, test_sequence.sequence_id),
            (now - timedelta(days=2), 600, CompletionStatus.COMPLETED, custom_sequence.sequence_id),
            (now - timedelta(days=40), 900, CompletionStatus.COMPLETED, test_sequence.sequence_id),
            (now - timedelta(days=1), 300, CompletionStatus.ABANDONED, test_sequence.sequence_id),
        ]

        for started_at, duration, status, seq_id in sessions_data:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=seq_id,
                started_at=started_at,
                duration_seconds=duration,
                completion_status=status
            )
            db_session.add(session)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/stats",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_sessions"] == 4  # 4 completed
        assert data["total_practice_time_seconds"] == 3600  # 60 minutes
        assert data["total_practice_time_hours"] == 1.0
        assert data["average_session_duration_minutes"] == 15.0
        assert data["current_streak_days"] == 3  # last 3 days
        assert data["completion_rate_percentage"] == 80.0  # 4/5 = 80%
        assert data["sessions_last_30_days"] == 3  # excludes the 40-day old one

    @pytest.mark.asyncio
    async def test_get_stats_most_practiced_sequences(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        custom_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test most practiced sequences in stats."""
        # Create sessions - more for test_sequence
        for i in range(3):
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=datetime.utcnow(),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)

        # One for custom_sequence
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=custom_sequence.sequence_id,
            started_at=datetime.utcnow(),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add(session)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/stats",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        sequences = data["most_practiced_sequences"]
        assert len(sequences) == 2
        # test_sequence should be first (3 practices)
        assert sequences[0]["sequence_id"] == test_sequence.sequence_id
        assert sequences[0]["practice_count"] == 3
        # custom_sequence should be second (1 practice)
        assert sequences[1]["sequence_id"] == custom_sequence.sequence_id
        assert sequences[1]["practice_count"] == 1

    @pytest.mark.asyncio
    async def test_get_stats_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that stats endpoint requires authentication."""
        response = await async_client.get("/api/v1/stats")
        assert response.status_code == 401


class TestCalendarEndpoint:
    """Test GET /api/v1/calendar endpoint."""

    @pytest.mark.asyncio
    async def test_get_calendar_empty(
        self,
        async_client: AsyncClient,
        test_user: User,
        user_token_headers: dict
    ):
        """Test getting calendar when user has no sessions."""
        response = await async_client.get(
            "/api/v1/calendar",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["months"] == []
        assert data["total_days_practiced"] == 0

    @pytest.mark.asyncio
    async def test_get_calendar_basic(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test basic calendar data."""
        now = datetime.utcnow()

        # Create sessions on different days
        for days_ago in [0, 0, 1, 2]:  # 2 on today, 1 on yesterday, 1 two days ago
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=now - timedelta(days=days_ago),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/calendar",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_days_practiced"] == 3  # 3 different days
        assert len(data["months"]) >= 1  # at least current month

        # Check current month data
        current_month = data["months"][0]
        assert current_month["year"] == now.year
        assert current_month["month"] == now.month
        assert len(current_month["days"]) == 3  # 3 days with sessions

    @pytest.mark.asyncio
    async def test_get_calendar_date_range(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test calendar with date range filtering."""
        now = datetime.utcnow()

        # Create sessions over a 3-month period
        for days_ago in [0, 35, 70]:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=now - timedelta(days=days_ago),
                duration_seconds=900,
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        # Get calendar for last 60 days
        start_date = (now - timedelta(days=60)).isoformat()
        end_date = now.isoformat()

        response = await async_client.get(
            f"/api/v1/calendar?start_date={start_date}&end_date={end_date}",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should only include sessions from last 60 days (excludes 70-day old session)
        assert data["total_days_practiced"] == 2

    @pytest.mark.asyncio
    async def test_get_calendar_multiple_sessions_per_day(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test that calendar correctly handles multiple sessions per day."""
        now = datetime.utcnow()

        # Create 3 sessions on the same day with different durations
        for hour in [8, 12, 18]:
            session = PracticeSession(
                user_id=test_user.user_id,
                sequence_id=test_sequence.sequence_id,
                started_at=now.replace(hour=hour, minute=0, second=0),
                duration_seconds=600,  # 10 minutes each
                completion_status=CompletionStatus.COMPLETED
            )
            db_session.add(session)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/calendar",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should have 1 day with 3 sessions
        assert data["total_days_practiced"] == 1
        day_data = data["months"][0]["days"][0]
        assert day_data["session_count"] == 3
        assert day_data["total_duration_seconds"] == 1800  # 30 minutes total

    @pytest.mark.asyncio
    async def test_get_calendar_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that calendar endpoint requires authentication."""
        response = await async_client.get("/api/v1/calendar")
        assert response.status_code == 401
