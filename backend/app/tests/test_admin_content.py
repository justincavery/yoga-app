"""
Integration tests for Admin Content Management API endpoints.
Tests admin CRUD operations for poses and sequences.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pose import Pose, PoseCategory, DifficultyLevel
from app.models.sequence import Sequence, SequencePose, FocusArea, YogaStyle
from app.models.user import User


@pytest.fixture
async def admin_token_headers(admin_user: User) -> dict:
    """Generate authentication headers for admin user."""
    from app.core.security import create_access_token

    token_data = {"sub": admin_user.email, "user_id": admin_user.user_id}
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def non_admin_token_headers(test_user: User) -> dict:
    """Generate authentication headers for non-admin user."""
    from app.core.security import create_access_token

    token_data = {"sub": test_user.email, "user_id": test_user.user_id}
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}


# ===== ADMIN POSE TESTS =====

@pytest.mark.asyncio
async def test_admin_create_pose_success(
    async_client: AsyncClient,
    admin_token_headers: dict,
    db_session: AsyncSession
):
    """Test admin can create a new pose."""
    pose_data = {
        "name_english": "Admin Created Pose",
        "name_sanskrit": "Admin Asana",
        "category": "standing",
        "difficulty_level": "beginner",
        "description": "A pose created by admin",
        "instructions": ["Step 1", "Step 2", "Step 3"],
        "benefits": "Great benefits",
        "contraindications": "Be careful with...",
        "target_areas": ["legs", "core"],
        "image_urls": ["https://example.com/admin-pose.jpg"]
    }

    response = await async_client.post(
        "/api/v1/poses",
        json=pose_data,
        headers=admin_token_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name_english"] == pose_data["name_english"]
    assert data["name_sanskrit"] == pose_data["name_sanskrit"]
    assert data["category"] == pose_data["category"]
    assert "pose_id" in data
    assert "created_at" in data

    # Verify in database
    result = await db_session.execute(
        select(Pose).where(Pose.name_english == pose_data["name_english"])
    )
    pose = result.scalar_one_or_none()
    assert pose is not None
    assert pose.name_english == pose_data["name_english"]


@pytest.mark.asyncio
async def test_admin_create_pose_without_auth(async_client: AsyncClient):
    """Test creating pose without authentication fails."""
    pose_data = {
        "name_english": "Unauthorized Pose",
        "category": "standing",
        "difficulty_level": "beginner",
        "description": "Should not be created",
        "instructions": ["Step 1"],
        "image_urls": ["https://example.com/test.jpg"]
    }

    response = await async_client.post("/api/v1/poses", json=pose_data)
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_admin_create_pose_non_admin_user(
    async_client: AsyncClient,
    non_admin_token_headers: dict
):
    """Test non-admin user cannot create poses."""
    pose_data = {
        "name_english": "Non-Admin Pose",
        "category": "standing",
        "difficulty_level": "beginner",
        "description": "Should not be created",
        "instructions": ["Step 1"],
        "image_urls": ["https://example.com/test.jpg"]
    }

    response = await async_client.post(
        "/api/v1/poses",
        json=pose_data,
        headers=non_admin_token_headers
    )
    assert response.status_code == 403  # Not authorized (non-admin)


@pytest.mark.asyncio
async def test_admin_create_pose_validation_error(
    async_client: AsyncClient,
    admin_token_headers: dict
):
    """Test pose creation with invalid data fails validation."""
    pose_data = {
        "name_english": "",  # Invalid: empty string
        "category": "invalid_category",
        "difficulty_level": "beginner",
        "description": "Test",
        "instructions": [],  # Invalid: empty array
        "image_urls": []  # Invalid: no images
    }

    response = await async_client.post(
        "/api/v1/poses",
        json=pose_data,
        headers=admin_token_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_admin_update_pose_success(
    async_client: AsyncClient,
    admin_token_headers: dict,
    test_pose: Pose,
    db_session: AsyncSession
):
    """Test admin can update an existing pose."""
    update_data = {
        "name_english": "Updated Pose Name",
        "description": "Updated description",
        "benefits": "Updated benefits"
    }

    response = await async_client.put(
        f"/api/v1/poses/{test_pose.pose_id}",
        json=update_data,
        headers=admin_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name_english"] == update_data["name_english"]
    assert data["description"] == update_data["description"]
    assert data["benefits"] == update_data["benefits"]

    # Verify in database
    await db_session.refresh(test_pose)
    assert test_pose.name_english == update_data["name_english"]


@pytest.mark.asyncio
async def test_admin_update_pose_partial(
    async_client: AsyncClient,
    admin_token_headers: dict,
    test_pose: Pose
):
    """Test admin can partially update a pose."""
    original_description = test_pose.description
    update_data = {"name_english": "Partially Updated Pose"}

    response = await async_client.put(
        f"/api/v1/poses/{test_pose.pose_id}",
        json=update_data,
        headers=admin_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name_english"] == update_data["name_english"]
    assert data["description"] == original_description  # Should remain unchanged


@pytest.mark.asyncio
async def test_admin_update_pose_not_found(
    async_client: AsyncClient,
    admin_token_headers: dict
):
    """Test updating non-existent pose returns 404."""
    update_data = {"name_english": "Updated Name"}

    response = await async_client.put(
        "/api/v1/poses/99999",
        json=update_data,
        headers=admin_token_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_update_pose_without_auth(
    async_client: AsyncClient,
    test_pose: Pose
):
    """Test updating pose without authentication fails."""
    update_data = {"name_english": "Should Not Update"}

    response = await async_client.put(
        f"/api/v1/poses/{test_pose.pose_id}",
        json=update_data
    )
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_admin_update_pose_non_admin_user(
    async_client: AsyncClient,
    non_admin_token_headers: dict,
    test_pose: Pose
):
    """Test non-admin user cannot update poses."""
    update_data = {"name_english": "Non-Admin Update"}

    response = await async_client.put(
        f"/api/v1/poses/{test_pose.pose_id}",
        json=update_data,
        headers=non_admin_token_headers
    )
    assert response.status_code == 403  # Not authorized (non-admin)


@pytest.mark.asyncio
async def test_admin_delete_pose_success(
    async_client: AsyncClient,
    admin_token_headers: dict,
    test_pose: Pose,
    db_session: AsyncSession
):
    """Test admin can delete a pose."""
    pose_id = test_pose.pose_id

    response = await async_client.delete(
        f"/api/v1/poses/{pose_id}",
        headers=admin_token_headers
    )

    assert response.status_code == 204

    # Verify pose is deleted from database
    result = await db_session.execute(
        select(Pose).where(Pose.pose_id == pose_id)
    )
    pose = result.scalar_one_or_none()
    assert pose is None


@pytest.mark.asyncio
async def test_admin_delete_pose_not_found(
    async_client: AsyncClient,
    admin_token_headers: dict
):
    """Test deleting non-existent pose returns 404."""
    response = await async_client.delete(
        "/api/v1/poses/99999",
        headers=admin_token_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_delete_pose_without_auth(
    async_client: AsyncClient,
    test_pose: Pose
):
    """Test deleting pose without authentication fails."""
    response = await async_client.delete(f"/api/v1/poses/{test_pose.pose_id}")
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_admin_delete_pose_non_admin_user(
    async_client: AsyncClient,
    non_admin_token_headers: dict,
    test_pose: Pose
):
    """Test non-admin user cannot delete poses."""
    response = await async_client.delete(
        f"/api/v1/poses/{test_pose.pose_id}",
        headers=non_admin_token_headers
    )
    assert response.status_code == 403  # Not authorized (non-admin)


# ===== ADMIN SEQUENCE TESTS =====

@pytest.mark.asyncio
async def test_admin_create_sequence_success(
    async_client: AsyncClient,
    admin_token_headers: dict,
    test_poses: list[Pose],
    db_session: AsyncSession
):
    """Test admin can create a new sequence."""
    sequence_data = {
        "name": "Admin Created Sequence",
        "description": "A sequence created by admin",
        "difficulty_level": "intermediate",
        "duration_minutes": 30,
        "focus_area": "strength",
        "style": "vinyasa",
        "is_preset": True,
        "poses": [
            {"pose_id": test_poses[0].pose_id, "position_order": 1, "duration_seconds": 60},
            {"pose_id": test_poses[1].pose_id, "position_order": 2, "duration_seconds": 90},
            {"pose_id": test_poses[2].pose_id, "position_order": 3, "duration_seconds": 120}
        ]
    }

    response = await async_client.post(
        "/api/v1/admin/sequences",
        json=sequence_data,
        headers=admin_token_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sequence_data["name"]
    assert data["difficulty_level"] == sequence_data["difficulty_level"]
    assert data["is_preset"] == True
    assert len(data["poses"]) == 3
    assert "sequence_id" in data

    # Verify in database
    result = await db_session.execute(
        select(Sequence).where(Sequence.name == sequence_data["name"])
    )
    sequence = result.scalar_one_or_none()
    assert sequence is not None
    assert sequence.name == sequence_data["name"]


@pytest.mark.asyncio
async def test_admin_create_sequence_without_auth(
    async_client: AsyncClient,
    test_poses: list[Pose]
):
    """Test creating sequence without authentication fails."""
    sequence_data = {
        "name": "Unauthorized Sequence",
        "difficulty_level": "beginner",
        "duration_minutes": 15,
        "focus_area": "flexibility",
        "style": "yin",
        "poses": [
            {"pose_id": test_poses[0].pose_id, "position_order": 1, "duration_seconds": 60}
        ]
    }

    response = await async_client.post("/api/v1/admin/sequences", json=sequence_data)
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_admin_create_sequence_non_admin_user(
    async_client: AsyncClient,
    non_admin_token_headers: dict,
    test_poses: list[Pose]
):
    """Test non-admin user cannot create preset sequences."""
    sequence_data = {
        "name": "Non-Admin Sequence",
        "difficulty_level": "beginner",
        "duration_minutes": 15,
        "focus_area": "flexibility",
        "style": "yin",
        "is_preset": True,
        "poses": [
            {"pose_id": test_poses[0].pose_id, "position_order": 1, "duration_seconds": 60}
        ]
    }

    response = await async_client.post(
        "/api/v1/admin/sequences",
        json=sequence_data,
        headers=non_admin_token_headers
    )
    assert response.status_code == 403  # Not authorized (non-admin)


@pytest.mark.asyncio
async def test_admin_create_sequence_validation_error(
    async_client: AsyncClient,
    admin_token_headers: dict
):
    """Test sequence creation with invalid data fails validation."""
    sequence_data = {
        "name": "",  # Invalid: empty string
        "difficulty_level": "beginner",
        "duration_minutes": 15,
        "focus_area": "flexibility",
        "style": "yin",
        "poses": []  # Invalid: no poses
    }

    response = await async_client.post(
        "/api/v1/admin/sequences",
        json=sequence_data,
        headers=admin_token_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_admin_create_sequence_invalid_pose_id(
    async_client: AsyncClient,
    admin_token_headers: dict
):
    """Test sequence creation with non-existent pose ID fails."""
    sequence_data = {
        "name": "Invalid Pose Sequence",
        "difficulty_level": "beginner",
        "duration_minutes": 15,
        "focus_area": "flexibility",
        "style": "yin",
        "poses": [
            {"pose_id": 99999, "position_order": 1, "duration_seconds": 60}
        ]
    }

    response = await async_client.post(
        "/api/v1/admin/sequences",
        json=sequence_data,
        headers=admin_token_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_update_sequence_success(
    async_client: AsyncClient,
    admin_token_headers: dict,
    test_sequence: Sequence,
    db_session: AsyncSession
):
    """Test admin can update an existing sequence."""
    update_data = {
        "name": "Updated Sequence Name",
        "description": "Updated description",
        "duration_minutes": 25
    }

    response = await async_client.put(
        f"/api/v1/admin/sequences/{test_sequence.sequence_id}",
        json=update_data,
        headers=admin_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["duration_minutes"] == update_data["duration_minutes"]

    # Verify in database
    await db_session.refresh(test_sequence)
    assert test_sequence.name == update_data["name"]


@pytest.mark.asyncio
async def test_admin_update_sequence_with_poses(
    async_client: AsyncClient,
    admin_token_headers: dict,
    test_sequence: Sequence,
    test_poses: list[Pose],
    db_session: AsyncSession
):
    """Test admin can update sequence poses."""
    update_data = {
        "name": "Updated with New Poses",
        "poses": [
            {"pose_id": test_poses[0].pose_id, "position_order": 1, "duration_seconds": 45},
            {"pose_id": test_poses[1].pose_id, "position_order": 2, "duration_seconds": 75}
        ]
    }

    response = await async_client.put(
        f"/api/v1/admin/sequences/{test_sequence.sequence_id}",
        json=update_data,
        headers=admin_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["poses"]) == 2
    assert data["poses"][0]["duration_seconds"] == 45


@pytest.mark.asyncio
async def test_admin_update_sequence_partial(
    async_client: AsyncClient,
    admin_token_headers: dict,
    test_sequence: Sequence
):
    """Test admin can partially update a sequence."""
    original_focus = test_sequence.focus_area
    update_data = {"name": "Partially Updated Sequence"}

    response = await async_client.put(
        f"/api/v1/admin/sequences/{test_sequence.sequence_id}",
        json=update_data,
        headers=admin_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["focus_area"] == original_focus.value


@pytest.mark.asyncio
async def test_admin_update_sequence_not_found(
    async_client: AsyncClient,
    admin_token_headers: dict
):
    """Test updating non-existent sequence returns 404."""
    update_data = {"name": "Updated Name"}

    response = await async_client.put(
        "/api/v1/admin/sequences/99999",
        json=update_data,
        headers=admin_token_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_update_sequence_without_auth(
    async_client: AsyncClient,
    test_sequence: Sequence
):
    """Test updating sequence without authentication fails."""
    update_data = {"name": "Should Not Update"}

    response = await async_client.put(
        f"/api/v1/admin/sequences/{test_sequence.sequence_id}",
        json=update_data
    )
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_admin_update_sequence_non_admin_user(
    async_client: AsyncClient,
    non_admin_token_headers: dict,
    test_sequence: Sequence
):
    """Test non-admin user cannot update preset sequences."""
    update_data = {"name": "Non-Admin Update"}

    response = await async_client.put(
        f"/api/v1/admin/sequences/{test_sequence.sequence_id}",
        json=update_data,
        headers=non_admin_token_headers
    )
    assert response.status_code == 403  # Not authorized (non-admin)


@pytest.mark.asyncio
async def test_admin_delete_sequence_success(
    async_client: AsyncClient,
    admin_token_headers: dict,
    test_sequence: Sequence,
    db_session: AsyncSession
):
    """Test admin can delete a sequence."""
    sequence_id = test_sequence.sequence_id

    response = await async_client.delete(
        f"/api/v1/admin/sequences/{sequence_id}",
        headers=admin_token_headers
    )

    assert response.status_code == 204

    # Verify sequence is deleted from database
    result = await db_session.execute(
        select(Sequence).where(Sequence.sequence_id == sequence_id)
    )
    sequence = result.scalar_one_or_none()
    assert sequence is None

    # Verify cascade deletion of sequence_poses
    result = await db_session.execute(
        select(SequencePose).where(SequencePose.sequence_id == sequence_id)
    )
    poses = result.scalars().all()
    assert len(poses) == 0


@pytest.mark.asyncio
async def test_admin_delete_sequence_not_found(
    async_client: AsyncClient,
    admin_token_headers: dict
):
    """Test deleting non-existent sequence returns 404."""
    response = await async_client.delete(
        "/api/v1/admin/sequences/99999",
        headers=admin_token_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_delete_sequence_without_auth(
    async_client: AsyncClient,
    test_sequence: Sequence
):
    """Test deleting sequence without authentication fails."""
    response = await async_client.delete(
        f"/api/v1/admin/sequences/{test_sequence.sequence_id}"
    )
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_admin_delete_sequence_non_admin_user(
    async_client: AsyncClient,
    non_admin_token_headers: dict,
    test_sequence: Sequence
):
    """Test non-admin user cannot delete sequences."""
    response = await async_client.delete(
        f"/api/v1/admin/sequences/{test_sequence.sequence_id}",
        headers=non_admin_token_headers
    )
    assert response.status_code == 403  # Not authorized (non-admin)
