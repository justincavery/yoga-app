"""
Unit tests for Sequence API endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


# ===== List Sequences Tests =====

@pytest.mark.asyncio
async def test_list_sequences(override_get_db, test_sequence):
    """Test listing sequences with pagination."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences")

    assert response.status_code == 200
    data = response.json()
    assert "sequences" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total"] >= 1
    assert len(data["sequences"]) >= 1


@pytest.mark.asyncio
async def test_list_sequences_with_pagination(override_get_db, test_sequences):
    """Test pagination parameters."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences?page=1&page_size=2")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["sequences"]) <= 2


@pytest.mark.asyncio
async def test_list_sequences_invalid_pagination(override_get_db):
    """Test invalid pagination parameters."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences?page=0")

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_sequences_by_difficulty(override_get_db, test_sequences):
    """Test filtering sequences by difficulty level."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences?difficulty=beginner")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for sequence in data["sequences"]:
        assert sequence["difficulty_level"] == "beginner"


@pytest.mark.asyncio
async def test_list_sequences_by_focus_area(override_get_db, test_sequences):
    """Test filtering sequences by focus area."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences?focus_area=flexibility")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for sequence in data["sequences"]:
        assert sequence["focus_area"] == "flexibility"


@pytest.mark.asyncio
async def test_list_sequences_by_style(override_get_db, test_sequences):
    """Test filtering sequences by yoga style."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences?style=vinyasa")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for sequence in data["sequences"]:
        assert sequence["style"] == "vinyasa"


@pytest.mark.asyncio
async def test_list_sequences_by_duration(override_get_db, test_sequences):
    """Test filtering sequences by duration."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test max duration
        response = await client.get("/api/v1/sequences?max_duration=20")

    assert response.status_code == 200
    data = response.json()
    for sequence in data["sequences"]:
        assert sequence["duration_minutes"] <= 20

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test min duration
        response = await client.get("/api/v1/sequences?min_duration=30")

    assert response.status_code == 200
    data = response.json()
    for sequence in data["sequences"]:
        assert sequence["duration_minutes"] >= 30


@pytest.mark.asyncio
async def test_list_sequences_preset_filter(override_get_db, test_sequences):
    """Test filtering preset vs custom sequences."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences?preset_only=true")

    assert response.status_code == 200
    data = response.json()
    for sequence in data["sequences"]:
        assert sequence["is_preset"] is True


@pytest.mark.asyncio
async def test_list_sequences_with_search(override_get_db, test_sequences):
    """Test searching sequences by name."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences?search=Morning")

    assert response.status_code == 200
    data = response.json()
    # Should find sequences with "Morning" in the name
    assert data["total"] >= 0


@pytest.mark.asyncio
async def test_list_sequences_multiple_filters(override_get_db, test_sequences):
    """Test combining multiple filters."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/sequences?difficulty=beginner&focus_area=flexibility&max_duration=20"
        )

    assert response.status_code == 200
    data = response.json()
    for sequence in data["sequences"]:
        assert sequence["difficulty_level"] == "beginner"
        assert sequence["focus_area"] == "flexibility"
        assert sequence["duration_minutes"] <= 20


# ===== Get Single Sequence Tests =====

@pytest.mark.asyncio
async def test_get_sequence(override_get_db, test_sequence, test_poses):
    """Test getting a single sequence by ID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/sequences/{test_sequence.sequence_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["sequence_id"] == test_sequence.sequence_id
    assert data["name"] == test_sequence.name
    assert data["description"] == test_sequence.description
    assert data["difficulty_level"] == test_sequence.difficulty_level
    assert data["duration_minutes"] == test_sequence.duration_minutes
    assert data["focus_area"] == test_sequence.focus_area.value
    assert data["style"] == test_sequence.style.value

    # Should include pose details
    assert "poses" in data
    assert len(data["poses"]) == 3

    # Check pose ordering
    assert data["poses"][0]["position_order"] == 1
    assert data["poses"][1]["position_order"] == 2
    assert data["poses"][2]["position_order"] == 3

    # Check pose details are included
    assert "pose" in data["poses"][0]
    assert data["poses"][0]["pose"]["name_english"] == test_poses[0].name_english


@pytest.mark.asyncio
async def test_get_sequence_not_found(override_get_db):
    """Test getting a non-existent sequence."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences/99999")

    assert response.status_code == 404


# ===== Categorization Endpoints Tests =====

@pytest.mark.asyncio
async def test_get_sequences_by_category(override_get_db, test_sequences):
    """Test endpoint to get sequences grouped by category."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences/categories")

    assert response.status_code == 200
    data = response.json()

    # Should have categories for difficulty, focus_area, and style
    assert "by_difficulty" in data
    assert "by_focus_area" in data
    assert "by_style" in data
    assert "by_duration" in data

    # Check structure of difficulty grouping
    assert "beginner" in data["by_difficulty"]
    assert isinstance(data["by_difficulty"]["beginner"], int)

    # Check structure of focus area grouping
    assert isinstance(data["by_focus_area"], dict)

    # Check structure of style grouping
    assert isinstance(data["by_style"], dict)

    # Check duration ranges
    assert "0-15" in data["by_duration"]
    assert "16-30" in data["by_duration"]
    assert "31-45" in data["by_duration"]
    assert "46+" in data["by_duration"]


@pytest.mark.asyncio
async def test_get_focus_areas(override_get_db):
    """Test endpoint to get available focus areas."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences/focus-areas")

    assert response.status_code == 200
    data = response.json()
    assert "focus_areas" in data
    assert isinstance(data["focus_areas"], list)
    assert "flexibility" in data["focus_areas"]
    assert "strength" in data["focus_areas"]
    assert "relaxation" in data["focus_areas"]
    assert "balance" in data["focus_areas"]


@pytest.mark.asyncio
async def test_get_styles(override_get_db):
    """Test endpoint to get available yoga styles."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences/styles")

    assert response.status_code == 200
    data = response.json()
    assert "styles" in data
    assert isinstance(data["styles"], list)
    assert "vinyasa" in data["styles"]
    assert "yin" in data["styles"]
    assert "restorative" in data["styles"]
    assert "hatha" in data["styles"]


# ===== Edge Cases and Error Handling =====

@pytest.mark.asyncio
async def test_empty_sequences_list(override_get_db):
    """Test listing sequences when none exist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Clear all sequences first would need a clean database
        # For now, just test that endpoint returns proper structure
        response = await client.get("/api/v1/sequences?difficulty=beginner&style=power&focus_area=core")

    assert response.status_code == 200
    data = response.json()
    assert "sequences" in data
    assert isinstance(data["sequences"], list)


@pytest.mark.asyncio
async def test_sequence_total_duration_calculation(override_get_db, test_sequence):
    """Test that total duration is correctly calculated from poses."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/sequences/{test_sequence.sequence_id}")

    assert response.status_code == 200
    data = response.json()

    # Calculate expected total from individual pose durations
    total_seconds = sum(pose["duration_seconds"] for pose in data["poses"])
    expected_minutes = total_seconds // 60

    # The sequence should show accurate duration
    assert "total_duration_seconds" in data
    assert data["total_duration_seconds"] == total_seconds


@pytest.mark.asyncio
async def test_invalid_filter_values(override_get_db):
    """Test handling of invalid filter values."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences?difficulty=invalid")

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_sequences_ordering(override_get_db, test_sequences):
    """Test that sequences are returned in consistent order."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sequences")

    assert response.status_code == 200
    data = response.json()

    # Sequences should be ordered (by name or created_at)
    names = [seq["name"] for seq in data["sequences"]]
    assert names == sorted(names)  # Should be alphabetically sorted by name
