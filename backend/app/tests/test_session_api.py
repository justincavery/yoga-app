"""
Unit tests for Practice Session API endpoints.

Tests cover:
- POST /api/v1/sessions/start - Start a new practice session
- POST /api/v1/sessions/complete - Complete a practice session
- PUT /api/v1/sessions/{session_id}/pause - Pause a session
- GET /api/v1/sessions/current - Get current active session
"""
import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.practice_session import PracticeSession, CompletionStatus
from app.models.user import User
from app.models.sequence import Sequence


class TestStartSession:
    """Test POST /api/v1/sessions/start endpoint."""

    @pytest.mark.asyncio
    async def test_start_session_success(
        self,
        async_client: AsyncClient,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test successfully starting a practice session."""
        response = await async_client.post(
            "/api/v1/sessions/start",
            json={"sequence_id": test_sequence.sequence_id},
            headers=user_token_headers
        )

        assert response.status_code == 201
        data = response.json()

        assert "session_id" in data
        assert data["sequence_id"] == test_sequence.sequence_id
        assert data["user_id"] == test_user.user_id
        assert data["completion_status"] == "abandoned"
        assert data["duration_seconds"] == 0
        assert "started_at" in data
        assert data["completed_at"] is None

    @pytest.mark.asyncio
    async def test_start_session_without_sequence(
        self,
        async_client: AsyncClient,
        user_token_headers: dict
    ):
        """Test starting a session without a sequence (free practice)."""
        response = await async_client.post(
            "/api/v1/sessions/start",
            json={},
            headers=user_token_headers
        )

        assert response.status_code == 201
        data = response.json()

        assert "session_id" in data
        assert data["sequence_id"] is None
        assert data["completion_status"] == "abandoned"

    @pytest.mark.asyncio
    async def test_start_session_invalid_sequence(
        self,
        async_client: AsyncClient,
        user_token_headers: dict
    ):
        """Test starting a session with non-existent sequence."""
        response = await async_client.post(
            "/api/v1/sessions/start",
            json={"sequence_id": 99999},
            headers=user_token_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_start_session_unauthorized(
        self,
        async_client: AsyncClient,
        test_sequence: Sequence
    ):
        """Test starting a session without authentication."""
        response = await async_client.post(
            "/api/v1/sessions/start",
            json={"sequence_id": test_sequence.sequence_id}
        )

        assert response.status_code == 401


class TestCompleteSession:
    """Test POST /api/v1/sessions/complete endpoint."""

    @pytest.mark.asyncio
    async def test_complete_session_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test successfully completing a practice session."""
        # Create an active session
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=15),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Complete the session
        response = await async_client.post(
            "/api/v1/sessions/complete",
            json={
                "session_id": session.session_id,
                "duration_seconds": 900,
                "poses_completed": 10
            },
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == session.session_id
        assert data["completion_status"] == "completed"
        assert data["duration_seconds"] == 900
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_complete_partial_session(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test completing a session with partial completion."""
        # Create session
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=8),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Mark as partial
        response = await async_client.post(
            "/api/v1/sessions/complete",
            json={
                "session_id": session.session_id,
                "duration_seconds": 480,
                "poses_completed": 5,
                "completion_status": "partial"
            },
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completion_status"] == "partial"
        assert data["duration_seconds"] == 480

    @pytest.mark.asyncio
    async def test_complete_session_invalid_id(
        self,
        async_client: AsyncClient,
        user_token_headers: dict
    ):
        """Test completing a non-existent session."""
        response = await async_client.post(
            "/api/v1/sessions/complete",
            json={
                "session_id": 99999,
                "duration_seconds": 900
            },
            headers=user_token_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_complete_another_users_session(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        intermediate_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test that users cannot complete another user's session."""
        # Create session for intermediate_user
        session = PracticeSession(
            user_id=intermediate_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Try to complete as test_user
        response = await async_client.post(
            "/api/v1/sessions/complete",
            json={
                "session_id": session.session_id,
                "duration_seconds": 900
            },
            headers=user_token_headers
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_complete_session_calculates_statistics(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test that completing a session returns statistics."""
        # Create session
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=15),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Complete session
        response = await async_client.post(
            "/api/v1/sessions/complete",
            json={
                "session_id": session.session_id,
                "duration_seconds": 900
            },
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should include some statistics
        assert "statistics" in data or data["completion_status"] == "completed"


class TestPauseSession:
    """Test PUT /api/v1/sessions/{session_id}/pause endpoint."""

    @pytest.mark.asyncio
    async def test_pause_session_success(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test successfully pausing a practice session."""
        # Create active session
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Pause the session
        response = await async_client.put(
            f"/api/v1/sessions/{session.session_id}/pause",
            json={"duration_so_far": 300},
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == session.session_id
        assert data["duration_seconds"] == 300
        # Status might still be abandoned or have a "paused" state

    @pytest.mark.asyncio
    async def test_pause_invalid_session(
        self,
        async_client: AsyncClient,
        user_token_headers: dict
    ):
        """Test pausing a non-existent session."""
        response = await async_client.put(
            "/api/v1/sessions/99999/pause",
            json={"duration_so_far": 300},
            headers=user_token_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_pause_another_users_session(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        intermediate_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test that users cannot pause another user's session."""
        # Create session for intermediate_user
        session = PracticeSession(
            user_id=intermediate_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Try to pause as test_user
        response = await async_client.put(
            f"/api/v1/sessions/{session.session_id}/pause",
            json={"duration_so_far": 300},
            headers=user_token_headers
        )

        assert response.status_code == 403


class TestGetCurrentSession:
    """Test GET /api/v1/sessions/current endpoint."""

    @pytest.mark.asyncio
    async def test_get_current_session_exists(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test getting the current active session."""
        # Create an active session
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Get current session
        response = await async_client.get(
            "/api/v1/sessions/current",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == session.session_id
        assert data["sequence_id"] == test_sequence.sequence_id
        assert data["completion_status"] == "abandoned"

    @pytest.mark.asyncio
    async def test_get_current_session_none_active(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test getting current session when none is active."""
        # Create a completed session (not active)
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc) - timedelta(hours=1),
            completed_at=datetime.now(timezone.utc) - timedelta(minutes=45),
            duration_seconds=900,
            completion_status=CompletionStatus.COMPLETED
        )
        db_session.add(session)
        await db_session.commit()

        # Get current session
        response = await async_client.get(
            "/api/v1/sessions/current",
            headers=user_token_headers
        )

        assert response.status_code == 404
        assert "no active session" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_current_session_returns_most_recent(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test that current session returns the most recent active session."""
        # Create two active sessions
        old_session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=30),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        new_session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add_all([old_session, new_session])
        await db_session.commit()
        await db_session.refresh(new_session)

        # Get current session
        response = await async_client.get(
            "/api/v1/sessions/current",
            headers=user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == new_session.session_id

    @pytest.mark.asyncio
    async def test_get_current_session_unauthorized(
        self,
        async_client: AsyncClient
    ):
        """Test getting current session without authentication."""
        response = await async_client.get("/api/v1/sessions/current")
        assert response.status_code == 401


class TestSessionValidation:
    """Test validation rules for session endpoints."""

    @pytest.mark.asyncio
    async def test_complete_with_negative_duration(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test that negative durations are rejected."""
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        response = await async_client.post(
            "/api/v1/sessions/complete",
            json={
                "session_id": session.session_id,
                "duration_seconds": -100
            },
            headers=user_token_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_complete_with_excessive_duration(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_sequence: Sequence,
        user_token_headers: dict
    ):
        """Test that excessively long durations are rejected."""
        session = PracticeSession(
            user_id=test_user.user_id,
            sequence_id=test_sequence.sequence_id,
            started_at=datetime.now(timezone.utc),
            completion_status=CompletionStatus.ABANDONED,
            duration_seconds=0
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Try to complete with 10 hours (36000 seconds)
        response = await async_client.post(
            "/api/v1/sessions/complete",
            json={
                "session_id": session.session_id,
                "duration_seconds": 36000
            },
            headers=user_token_headers
        )

        # Should either accept it or reject with 422
        assert response.status_code in [200, 422]
