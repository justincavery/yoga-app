#!/usr/bin/env python3
"""Initialize database with all tables."""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base
from app.models.user import User
from app.models.pose import Pose
from app.models.sequence import Sequence, SequencePose
from app.models.practice_session import PracticeSession
from app.models.favorites import UserFavorite
from app.models.achievement import Achievement, UserAchievement
from app.models.pose_relationship import PoseRelationship


async def init_database():
    """Create all tables in the database."""
    print("Creating all database tables...")

    async with engine.begin() as conn:
        # Drop all tables (if they exist)
        await conn.run_sync(Base.metadata.drop_all)
        print("Dropped existing tables")

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Created all tables")

    print("Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_database())
