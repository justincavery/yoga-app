"""
Unit tests for Pose API endpoints.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pose import Pose, PoseCategory, DifficultyLevel
from app.models.user import User
from app.core.security import hash_password


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123"),
        name="Test User",
        email_verified=True,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """Create an admin test user."""
    user = User(
        email="admin@admin.yogaflow.com",
        password_hash=hash_password("AdminPassword123"),
        name="Admin User",
        email_verified=True,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_pose(db_session: AsyncSession):
    """Create a test pose."""
    pose = Pose(
        name_english="Test Pose",
        name_sanskrit="Test Asana",
        category=PoseCategory.STANDING,
        difficulty_level=DifficultyLevel.BEGINNER,
        description="A test pose for unit testing",
        instructions=["Step 1", "Step 2", "Step 3"],
        benefits="Test benefits",
        contraindications="Test contraindications",
        target_areas=["legs", "core"],
        image_urls=["https://example.com/test.jpg"]
    )
    db_session.add(pose)
    await db_session.commit()
    await db_session.refresh(pose)
    return pose


@pytest.mark.asyncio
async def test_list_poses(test_pose, async_client):
    """Test listing poses with pagination."""
    response = await async_client.get("/api/v1/poses")

    assert response.status_code == 200
    data = response.json()
    assert "poses" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_poses_with_search(test_pose, async_client):
    """Test searching poses by name."""
    response = await async_client.get("/api/v1/poses?search=Test")

    assert response.status_code == 200
    data = response.json()
    assert len(data["poses"]) >= 1
    assert "Test" in data["poses"][0]["name_english"]


@pytest.mark.asyncio
async def test_list_poses_with_filters(test_pose, async_client):
    """Test filtering poses by difficulty."""
    # Use async_client fixture
    response = await async_client.get("/api/v1/poses?difficulty=beginner")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for pose in data["poses"]:
        assert pose["difficulty_level"] == "beginner"


@pytest.mark.asyncio
async def test_get_pose(test_pose, async_client):
    """Test getting a single pose by ID."""
    # Use async_client fixture
    response = await async_client.get(f"/api/v1/poses/{test_pose.pose_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["pose_id"] == test_pose.pose_id
    assert data["name_english"] == test_pose.name_english


@pytest.mark.asyncio
async def test_get_pose_not_found(async_client):
    """Test getting a non-existent pose."""
    # Use async_client fixture
    response = await async_client.get("/api/v1/poses/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_pose_without_auth(async_client):
    """Test creating a pose without authentication."""
    # Use async_client fixture
    response = await async_client.post(
            "/api/v1/poses",
            json={
                "name_english": "New Pose",
                "name_sanskrit": "New Asana",
                "category": "standing",
                "difficulty_level": "beginner",
                "description": "A new test pose",
                "instructions": ["Step 1", "Step 2"],
                "image_urls": ["https://example.com/image.jpg"]
            }
        )

    assert response.status_code == 401  # Unauthorized without auth


@pytest.mark.asyncio
async def test_pagination(async_client):
    """Test pagination parameters."""
    # Use async_client fixture
    response = await async_client.get("/api/v1/poses?page=1&page_size=5")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["poses"]) <= 5


@pytest.mark.asyncio
async def test_invalid_pagination(async_client):
    """Test invalid pagination parameters."""
    # Use async_client fixture
    response = await async_client.get("/api/v1/poses?page=0")

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_category_filter(test_pose, async_client):
    """Test filtering by category."""
    # Use async_client fixture
    response = await async_client.get("/api/v1/poses?category=standing")

    assert response.status_code == 200
    data = response.json()
    for pose in data["poses"]:
        assert pose["category"] == "standing"


@pytest.mark.asyncio
async def test_offset_limit_pagination(test_pose, async_client):
    """Test offset-based pagination for infinite scroll."""
    # Test with offset=0, limit=10
    response = await async_client.get("/api/v1/poses?offset=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert "poses" in data
    assert "total" in data
    assert len(data["poses"]) <= 10

    # Check for X-Total-Count header
    assert "x-total-count" in response.headers
    assert int(response.headers["x-total-count"]) >= 1


@pytest.mark.asyncio
async def test_offset_pagination_skip(async_client, db_session: AsyncSession):
    """Test offset pagination with multiple poses."""
    # Create multiple test poses
    poses = []
    for index in range(5):
        pose = Pose(
            name_english=f"Test Pose {index}",
            name_sanskrit=f"Test Asana {index}",
            category=PoseCategory.STANDING,
            difficulty_level=DifficultyLevel.BEGINNER,
            description=f"Test pose {index}",
            instructions=["Step 1", "Step 2"],
            image_urls=["https://example.com/test.jpg"]
        )
        db_session.add(pose)
        poses.append(pose)

    await db_session.commit()

    # Get first 2 poses
    response1 = await async_client.get("/api/v1/poses?offset=0&limit=2")
    assert response1.status_code == 200
    data1 = response1.json()

    # Get next 2 poses
    response2 = await async_client.get("/api/v1/poses?offset=2&limit=2")
    assert response2.status_code == 200
    data2 = response2.json()

    # Verify no overlap
    pose_ids_1 = {p["pose_id"] for p in data1["poses"]}
    pose_ids_2 = {p["pose_id"] for p in data2["poses"]}
    assert len(pose_ids_1.intersection(pose_ids_2)) == 0


@pytest.mark.asyncio
async def test_get_related_poses(async_client, db_session: AsyncSession):
    """Test getting related poses for a specific pose."""
    # Create test poses with relationships
    # Base pose
    base_pose = Pose(
        name_english="Mountain Pose",
        name_sanskrit="Tadasana",
        category=PoseCategory.STANDING,
        difficulty_level=DifficultyLevel.BEGINNER,
        description="Standing pose",
        instructions=["Step 1", "Step 2"],
        image_urls=["https://example.com/test.jpg"]
    )
    db_session.add(base_pose)

    # Similar pose (same category, same difficulty)
    similar_pose = Pose(
        name_english="Tree Pose",
        name_sanskrit="Vrksasana",
        category=PoseCategory.STANDING,
        difficulty_level=DifficultyLevel.BEGINNER,
        description="Standing balance pose",
        instructions=["Step 1", "Step 2"],
        image_urls=["https://example.com/test2.jpg"]
    )
    db_session.add(similar_pose)

    # Progression pose (higher difficulty)
    progression_pose = Pose(
        name_english="Warrior Pose",
        name_sanskrit="Virabhadrasana",
        category=PoseCategory.STANDING,
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        description="Standing warrior pose",
        instructions=["Step 1", "Step 2"],
        image_urls=["https://example.com/test3.jpg"]
    )
    db_session.add(progression_pose)

    await db_session.commit()
    await db_session.refresh(base_pose)

    # Test related poses endpoint
    response = await async_client.get(f"/api/v1/poses/{base_pose.pose_id}/related")

    assert response.status_code == 200
    data = response.json()
    assert "similar" in data
    assert "progressions" in data
    assert isinstance(data["similar"], list)
    assert isinstance(data["progressions"], list)


@pytest.mark.asyncio
async def test_get_related_poses_not_found(async_client):
    """Test getting related poses for non-existent pose."""
    response = await async_client.get("/api/v1/poses/99999/related")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_backward_compatible_pagination(test_pose, async_client):
    """Test that old page/page_size parameters still work."""
    # Test traditional pagination
    response = await async_client.get("/api/v1/poses?page=1&page_size=20")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert "poses" in data
    assert "total" in data
