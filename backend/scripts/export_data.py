#!/usr/bin/env python3
"""
Export data from SQLite database to JSON for migration to PostgreSQL.
This script exports all user data, poses, sequences, and practice history.

Usage:
    python scripts/export_data.py [output_file]

Example:
    python scripts/export_data.py data_export.json
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

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


def serialize_datetime(obj: Any) -> Any:
    """Convert datetime objects to ISO format strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


async def export_users(session: AsyncSession) -> list[dict]:
    """Export all users."""
    print("Exporting users...")
    result = await session.execute(select(User))
    users = result.scalars().all()

    user_data = []
    for user in users:
        user_data.append({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "hashed_password": user.hashed_password,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": serialize_datetime(user.created_at),
            "updated_at": serialize_datetime(user.updated_at),
        })

    print(f"  Exported {len(user_data)} users")
    return user_data


async def export_poses(session: AsyncSession) -> list[dict]:
    """Export all poses."""
    print("Exporting poses...")
    result = await session.execute(select(Pose))
    poses = result.scalars().all()

    pose_data = []
    for pose in poses:
        pose_data.append({
            "id": pose.id,
            "name": pose.name,
            "sanskrit_name": pose.sanskrit_name,
            "description": pose.description,
            "difficulty": pose.difficulty,
            "category": pose.category,
            "benefits": pose.benefits,
            "instructions": pose.instructions,
            "contraindications": pose.contraindications,
            "duration_seconds": pose.duration_seconds,
            "image_url": pose.image_url,
            "video_url": pose.video_url,
            "is_active": pose.is_active,
            "created_at": serialize_datetime(pose.created_at),
            "updated_at": serialize_datetime(pose.updated_at),
        })

    print(f"  Exported {len(pose_data)} poses")
    return pose_data


async def export_sequences(session: AsyncSession) -> list[dict]:
    """Export all sequences with their poses."""
    print("Exporting sequences...")
    result = await session.execute(select(Sequence))
    sequences = result.scalars().all()

    sequence_data = []
    for sequence in sequences:
        sequence_data.append({
            "id": sequence.id,
            "name": sequence.name,
            "description": sequence.description,
            "difficulty": sequence.difficulty,
            "duration_minutes": sequence.duration_minutes,
            "category": sequence.category,
            "is_active": sequence.is_active,
            "created_by_id": sequence.created_by_id,
            "created_at": serialize_datetime(sequence.created_at),
            "updated_at": serialize_datetime(sequence.updated_at),
            "pose_ids": [pose.id for pose in sequence.poses] if sequence.poses else [],
        })

    print(f"  Exported {len(sequence_data)} sequences")
    return sequence_data


async def export_practice_sessions(session: AsyncSession) -> list[dict]:
    """Export all practice sessions."""
    print("Exporting practice sessions...")
    result = await session.execute(select(PracticeSession))
    sessions = result.scalars().all()

    session_data = []
    for practice_session in sessions:
        session_data.append({
            "id": practice_session.id,
            "user_id": practice_session.user_id,
            "sequence_id": practice_session.sequence_id,
            "started_at": serialize_datetime(practice_session.started_at),
            "ended_at": serialize_datetime(practice_session.ended_at),
            "status": practice_session.status,
            "duration_minutes": practice_session.duration_minutes,
            "notes": practice_session.notes,
            "created_at": serialize_datetime(practice_session.created_at),
        })

    print(f"  Exported {len(session_data)} practice sessions")
    return session_data


async def export_practice_history(session: AsyncSession) -> list[dict]:
    """Export all practice history records."""
    print("Exporting practice history...")
    result = await session.execute(select(PracticeHistory))
    history_records = result.scalars().all()

    history_data = []
    for record in history_records:
        history_data.append({
            "id": record.id,
            "user_id": record.user_id,
            "session_id": record.session_id,
            "pose_id": record.pose_id,
            "completed": record.completed,
            "duration_seconds": record.duration_seconds,
            "notes": record.notes,
            "created_at": serialize_datetime(record.created_at),
        })

    print(f"  Exported {len(history_data)} practice history records")
    return history_data


async def export_all_data(output_file: str = "data_export.json"):
    """Export all data from database to JSON file."""
    print(f"\n=== Starting Data Export ===\n")
    print(f"Output file: {output_file}\n")

    async for session in get_session():
        try:
            # Export all data
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "users": await export_users(session),
                "poses": await export_poses(session),
                "sequences": await export_sequences(session),
                "practice_sessions": await export_practice_sessions(session),
                "practice_history": await export_practice_history(session),
            }

            # Write to file
            print(f"\nWriting data to {output_file}...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            # Summary
            print(f"\n=== Export Complete ===\n")
            print(f"Total users: {len(export_data['users'])}")
            print(f"Total poses: {len(export_data['poses'])}")
            print(f"Total sequences: {len(export_data['sequences'])}")
            print(f"Total practice sessions: {len(export_data['practice_sessions'])}")
            print(f"Total practice history: {len(export_data['practice_history'])}")
            print(f"\nExport saved to: {output_file}")

            break  # Only need one session

        except Exception as error:
            print(f"\nError during export: {error}")
            raise


if __name__ == "__main__":
    # Get output file from command line or use default
    output_file = sys.argv[1] if len(sys.argv) > 1 else "data_export.json"

    # Run export
    asyncio.run(export_all_data(output_file))
