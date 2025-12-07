#!/usr/bin/env python3
"""
Import data from JSON export into PostgreSQL database.
This script imports all user data, poses, sequences, and practice history.

Usage:
    python scripts/import_data.py <input_file>

Example:
    python scripts/import_data.py data_export.json
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.user import User
from app.models.pose import Pose
from app.models.sequence import Sequence
from app.models.session import PracticeSession
from app.models.practice_history import PracticeHistory


def parse_datetime(date_str: str | None) -> datetime | None:
    """Parse ISO format datetime string."""
    if not date_str:
        return None
    return datetime.fromisoformat(date_str)


async def import_users(session: AsyncSession, users_data: list[dict]) -> dict[int, int]:
    """Import users and return mapping of old ID to new ID."""
    print(f"Importing {len(users_data)} users...")
    id_mapping = {}

    for user_data in users_data:
        old_id = user_data["id"]

        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == user_data["email"])
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"  User {user_data['email']} already exists, skipping")
            id_mapping[old_id] = existing_user.id
            continue

        # Create new user
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=user_data["hashed_password"],
            is_active=user_data["is_active"],
            is_superuser=user_data.get("is_superuser", False),
        )

        # Set timestamps if available
        if user_data.get("created_at"):
            user.created_at = parse_datetime(user_data["created_at"])
        if user_data.get("updated_at"):
            user.updated_at = parse_datetime(user_data["updated_at"])

        session.add(user)
        await session.flush()  # Get ID without committing

        id_mapping[old_id] = user.id

    await session.commit()
    print(f"  Imported {len(id_mapping)} users")
    return id_mapping


async def import_poses(session: AsyncSession, poses_data: list[dict]) -> dict[int, int]:
    """Import poses and return mapping of old ID to new ID."""
    print(f"Importing {len(poses_data)} poses...")
    id_mapping = {}

    for pose_data in poses_data:
        old_id = pose_data["id"]

        # Check if pose already exists
        result = await session.execute(
            select(Pose).where(Pose.name == pose_data["name"])
        )
        existing_pose = result.scalar_one_or_none()

        if existing_pose:
            print(f"  Pose {pose_data['name']} already exists, skipping")
            id_mapping[old_id] = existing_pose.id
            continue

        # Create new pose
        pose = Pose(
            name=pose_data["name"],
            sanskrit_name=pose_data.get("sanskrit_name"),
            description=pose_data.get("description"),
            difficulty=pose_data.get("difficulty"),
            category=pose_data.get("category"),
            benefits=pose_data.get("benefits"),
            instructions=pose_data.get("instructions"),
            contraindications=pose_data.get("contraindications"),
            duration_seconds=pose_data.get("duration_seconds"),
            image_url=pose_data.get("image_url"),
            video_url=pose_data.get("video_url"),
            is_active=pose_data.get("is_active", True),
        )

        # Set timestamps if available
        if pose_data.get("created_at"):
            pose.created_at = parse_datetime(pose_data["created_at"])
        if pose_data.get("updated_at"):
            pose.updated_at = parse_datetime(pose_data["updated_at"])

        session.add(pose)
        await session.flush()

        id_mapping[old_id] = pose.id

    await session.commit()
    print(f"  Imported {len(id_mapping)} poses")
    return id_mapping


async def import_sequences(
    session: AsyncSession,
    sequences_data: list[dict],
    user_id_mapping: dict[int, int],
    pose_id_mapping: dict[int, int],
) -> dict[int, int]:
    """Import sequences and return mapping of old ID to new ID."""
    print(f"Importing {len(sequences_data)} sequences...")
    id_mapping = {}

    for sequence_data in sequences_data:
        old_id = sequence_data["id"]

        # Map user ID
        old_user_id = sequence_data.get("created_by_id")
        new_user_id = user_id_mapping.get(old_user_id) if old_user_id else None

        # Create new sequence
        sequence = Sequence(
            name=sequence_data["name"],
            description=sequence_data.get("description"),
            difficulty=sequence_data.get("difficulty"),
            duration_minutes=sequence_data.get("duration_minutes"),
            category=sequence_data.get("category"),
            is_active=sequence_data.get("is_active", True),
            created_by_id=new_user_id,
        )

        # Set timestamps if available
        if sequence_data.get("created_at"):
            sequence.created_at = parse_datetime(sequence_data["created_at"])
        if sequence_data.get("updated_at"):
            sequence.updated_at = parse_datetime(sequence_data["updated_at"])

        session.add(sequence)
        await session.flush()

        # Add poses to sequence
        if sequence_data.get("pose_ids"):
            for old_pose_id in sequence_data["pose_ids"]:
                new_pose_id = pose_id_mapping.get(old_pose_id)
                if new_pose_id:
                    result = await session.execute(
                        select(Pose).where(Pose.id == new_pose_id)
                    )
                    pose = result.scalar_one_or_none()
                    if pose:
                        sequence.poses.append(pose)

        id_mapping[old_id] = sequence.id

    await session.commit()
    print(f"  Imported {len(id_mapping)} sequences")
    return id_mapping


async def import_practice_sessions(
    session: AsyncSession,
    sessions_data: list[dict],
    user_id_mapping: dict[int, int],
    sequence_id_mapping: dict[int, int],
) -> dict[int, int]:
    """Import practice sessions and return mapping of old ID to new ID."""
    print(f"Importing {len(sessions_data)} practice sessions...")
    id_mapping = {}

    for session_data in sessions_data:
        old_id = session_data["id"]

        # Map user and sequence IDs
        old_user_id = session_data["user_id"]
        old_sequence_id = session_data.get("sequence_id")

        new_user_id = user_id_mapping.get(old_user_id)
        new_sequence_id = sequence_id_mapping.get(old_sequence_id) if old_sequence_id else None

        if not new_user_id:
            print(f"  Skipping session {old_id}: user not found")
            continue

        # Create new practice session
        practice_session = PracticeSession(
            user_id=new_user_id,
            sequence_id=new_sequence_id,
            started_at=parse_datetime(session_data.get("started_at")),
            ended_at=parse_datetime(session_data.get("ended_at")),
            status=session_data.get("status", "completed"),
            duration_minutes=session_data.get("duration_minutes"),
            notes=session_data.get("notes"),
        )

        # Set timestamps if available
        if session_data.get("created_at"):
            practice_session.created_at = parse_datetime(session_data["created_at"])

        session.add(practice_session)
        await session.flush()

        id_mapping[old_id] = practice_session.id

    await session.commit()
    print(f"  Imported {len(id_mapping)} practice sessions")
    return id_mapping


async def import_practice_history(
    session: AsyncSession,
    history_data: list[dict],
    user_id_mapping: dict[int, int],
    session_id_mapping: dict[int, int],
    pose_id_mapping: dict[int, int],
):
    """Import practice history records."""
    print(f"Importing {len(history_data)} practice history records...")
    imported = 0

    for record_data in history_data:
        # Map IDs
        old_user_id = record_data["user_id"]
        old_session_id = record_data.get("session_id")
        old_pose_id = record_data.get("pose_id")

        new_user_id = user_id_mapping.get(old_user_id)
        new_session_id = session_id_mapping.get(old_session_id) if old_session_id else None
        new_pose_id = pose_id_mapping.get(old_pose_id) if old_pose_id else None

        if not new_user_id:
            continue

        # Create new practice history record
        history = PracticeHistory(
            user_id=new_user_id,
            session_id=new_session_id,
            pose_id=new_pose_id,
            completed=record_data.get("completed", True),
            duration_seconds=record_data.get("duration_seconds"),
            notes=record_data.get("notes"),
        )

        # Set timestamps if available
        if record_data.get("created_at"):
            history.created_at = parse_datetime(record_data["created_at"])

        session.add(history)
        imported += 1

    await session.commit()
    print(f"  Imported {imported} practice history records")


async def import_all_data(input_file: str):
    """Import all data from JSON file into database."""
    print(f"\n=== Starting Data Import ===\n")
    print(f"Input file: {input_file}\n")

    # Read data file
    print("Reading data file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Export timestamp: {data['export_timestamp']}\n")

    async for db_session in get_session():
        try:
            # Import in order (to maintain relationships)
            user_mapping = await import_users(db_session, data["users"])
            pose_mapping = await import_poses(db_session, data["poses"])
            sequence_mapping = await import_sequences(
                db_session, data["sequences"], user_mapping, pose_mapping
            )
            session_mapping = await import_practice_sessions(
                db_session, data["practice_sessions"], user_mapping, sequence_mapping
            )
            await import_practice_history(
                db_session,
                data["practice_history"],
                user_mapping,
                session_mapping,
                pose_mapping,
            )

            # Summary
            print(f"\n=== Import Complete ===\n")
            print(f"Users: {len(user_mapping)}")
            print(f"Poses: {len(pose_mapping)}")
            print(f"Sequences: {len(sequence_mapping)}")
            print(f"Practice sessions: {len(session_mapping)}")
            print(f"Practice history: {len(data['practice_history'])}")

            break  # Only need one session

        except Exception as error:
            print(f"\nError during import: {error}")
            await db_session.rollback()
            raise


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_data.py <input_file>")
        print("Example: python scripts/import_data.py data_export.json")
        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    # Run import
    asyncio.run(import_all_data(input_file))
