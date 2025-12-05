"""
Pytest configuration and shared fixtures for YogaFlow tests.
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_database_session
from app.core.security import hash_password
# Import all models to ensure they're registered with Base
from app.models import *  # noqa: F401, F403
from app.models.user import User, ExperienceLevel
from app.models.pose import Pose, PoseCategory, DifficultyLevel
from app.models.sequence import Sequence, SequencePose, FocusArea, YogaStyle
from app.main import app


# Test database URL - use file-based SQLite for tests to avoid in-memory isolation issues
import tempfile
import os
TEST_DB_FILE = os.path.join(tempfile.gettempdir(), "test_yogaflow.db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    # Remove existing test database if it exists
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()

    # Clean up test database file
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function", autouse=True)
async def override_get_db(db_session: AsyncSession):
    """Override the get_database_session dependency for testing."""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_database_session] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123"),
        name="Test User",
        experience_level=ExperienceLevel.BEGINNER,
        email_verified=True,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def intermediate_user(db_session: AsyncSession) -> User:
    """Create an intermediate level test user."""
    user = User(
        email="intermediate@example.com",
        password_hash=hash_password("TestPassword123"),
        name="Intermediate User",
        experience_level=ExperienceLevel.INTERMEDIATE,
        email_verified=True,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
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
async def test_pose(db_session: AsyncSession) -> Pose:
    """Create a test pose."""
    pose = Pose(
        name_english="Mountain Pose",
        name_sanskrit="Tadasana",
        category=PoseCategory.STANDING,
        difficulty_level=DifficultyLevel.BEGINNER,
        description="A foundational standing pose that improves posture and balance",
        instructions=["Stand with feet together", "Arms at sides", "Engage core"],
        benefits="Improves posture, strengthens legs",
        contraindications="None",
        target_areas=["legs", "core"],
        image_urls=["https://example.com/tadasana.jpg"]
    )
    db_session.add(pose)
    await db_session.commit()
    await db_session.refresh(pose)
    return pose


@pytest.fixture
async def test_poses(db_session: AsyncSession) -> list[Pose]:
    """Create multiple test poses for sequences."""
    poses = [
        Pose(
            name_english="Mountain Pose",
            name_sanskrit="Tadasana",
            category=PoseCategory.STANDING,
            difficulty_level=DifficultyLevel.BEGINNER,
            description="Foundational standing pose",
            instructions=["Stand with feet together"],
            benefits="Improves posture",
            contraindications="None",
            target_areas=["legs"],
            image_urls=["https://example.com/tadasana.jpg"]
        ),
        Pose(
            name_english="Downward Dog",
            name_sanskrit="Adho Mukha Svanasana",
            category=PoseCategory.STANDING,
            difficulty_level=DifficultyLevel.BEGINNER,
            description="Inverted V-shape pose",
            instructions=["Start on hands and knees", "Lift hips up"],
            benefits="Strengthens arms and legs",
            contraindications="Wrist issues",
            target_areas=["arms", "legs", "back"],
            image_urls=["https://example.com/downward-dog.jpg"]
        ),
        Pose(
            name_english="Warrior I",
            name_sanskrit="Virabhadrasana I",
            category=PoseCategory.STANDING,
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            description="Standing warrior pose",
            instructions=["Step back with one foot", "Bend front knee", "Raise arms"],
            benefits="Strengthens legs and core",
            contraindications="Knee issues",
            target_areas=["legs", "core", "arms"],
            image_urls=["https://example.com/warrior1.jpg"]
        )
    ]
    for pose in poses:
        db_session.add(pose)
    await db_session.commit()
    for pose in poses:
        await db_session.refresh(pose)
    return poses


@pytest.fixture
async def test_sequence(db_session: AsyncSession, test_poses: list[Pose]) -> Sequence:
    """Create a test sequence with poses."""
    sequence = Sequence(
        name="Morning Flow",
        description="A gentle morning yoga sequence",
        difficulty_level="beginner",
        duration_minutes=15,
        focus_area=FocusArea.FLEXIBILITY,
        style=YogaStyle.VINYASA,
        is_preset=True,
        created_by=None
    )
    db_session.add(sequence)
    await db_session.flush()

    # Add poses to sequence
    for index, pose in enumerate(test_poses, start=1):
        sequence_pose = SequencePose(
            sequence_id=sequence.sequence_id,
            pose_id=pose.pose_id,
            position_order=index,
            duration_seconds=60 * index  # 60, 120, 180 seconds
        )
        db_session.add(sequence_pose)

    await db_session.commit()
    await db_session.refresh(sequence)
    return sequence


@pytest.fixture
async def test_sequences(db_session: AsyncSession, test_poses: list[Pose]) -> list[Sequence]:
    """Create multiple test sequences for filtering tests."""
    sequences = [
        Sequence(
            name="Beginner Flexibility",
            description="Gentle stretching sequence",
            difficulty_level="beginner",
            duration_minutes=15,
            focus_area=FocusArea.FLEXIBILITY,
            style=YogaStyle.YIN,
            is_preset=True,
            created_by=None
        ),
        Sequence(
            name="Intermediate Strength",
            description="Build strength and power",
            difficulty_level="intermediate",
            duration_minutes=30,
            focus_area=FocusArea.STRENGTH,
            style=YogaStyle.POWER,
            is_preset=True,
            created_by=None
        ),
        Sequence(
            name="Advanced Balance",
            description="Challenge your balance",
            difficulty_level="advanced",
            duration_minutes=45,
            focus_area=FocusArea.BALANCE,
            style=YogaStyle.VINYASA,
            is_preset=True,
            created_by=None
        ),
        Sequence(
            name="Evening Relaxation",
            description="Wind down before bed",
            difficulty_level="beginner",
            duration_minutes=20,
            focus_area=FocusArea.RELAXATION,
            style=YogaStyle.RESTORATIVE,
            is_preset=True,
            created_by=None
        )
    ]
    for sequence in sequences:
        db_session.add(sequence)
    await db_session.commit()
    for sequence in sequences:
        await db_session.refresh(sequence)
    return sequences


@pytest.fixture
async def custom_sequence(db_session: AsyncSession, test_user: User, test_poses: list[Pose]) -> Sequence:
    """Create a custom user sequence."""
    sequence = Sequence(
        name="My Custom Flow",
        description="A custom sequence created by user",
        difficulty_level="intermediate",
        duration_minutes=20,
        focus_area=FocusArea.STRENGTH,
        style=YogaStyle.POWER,
        is_preset=False,
        created_by=test_user.user_id
    )
    db_session.add(sequence)
    await db_session.flush()

    # Add first two poses
    for index, pose in enumerate(test_poses[:2], start=1):
        sequence_pose = SequencePose(
            sequence_id=sequence.sequence_id,
            pose_id=pose.pose_id,
            position_order=index,
            duration_seconds=90 * index
        )
        db_session.add(sequence_pose)

    await db_session.commit()
    await db_session.refresh(sequence)
    return sequence


@pytest.fixture
async def async_client():
    """Provide async HTTP client for API testing."""
    from httpx import AsyncClient, ASGITransport
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def user_token_headers(test_user: User) -> dict:
    """Generate authentication headers for test user."""
    from app.core.security import create_access_token

    token_data = {"sub": test_user.email, "user_id": test_user.user_id}
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def intermediate_user_token_headers(intermediate_user: User) -> dict:
    """Generate authentication headers for intermediate user."""
    from app.core.security import create_access_token

    token_data = {"sub": intermediate_user.email, "user_id": intermediate_user.user_id}
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}
