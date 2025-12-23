#!/usr/bin/env python3
"""
Migrate poses from SQLite to PostgreSQL
"""
import asyncio
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def migrate_poses():
    """Migrate poses from SQLite yogaflow.db to PostgreSQL."""

    # Connect to SQLite
    sqlite_db = Path(__file__).parent / "yogaflow.db"
    conn = sqlite3.connect(str(sqlite_db))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch all poses
    cursor.execute("SELECT * FROM poses")
    poses = cursor.fetchall()

    print(f"Found {len(poses)} poses in SQLite database")

    # Insert into PostgreSQL
    async with AsyncSessionLocal() as session:
        inserted = 0
        for pose in poses:
            # Prepare the insert statement
            insert_sql = text("""
                INSERT INTO poses (
                    pose_id, name_english, name_sanskrit, category, difficulty_level,
                    description, instructions, benefits, contraindications,
                    target_areas, image_urls, created_at, updated_at
                ) VALUES (
                    :pose_id, :name_english, :name_sanskrit, :category, :difficulty_level,
                    :description, :instructions, :benefits, :contraindications,
                    :target_areas, :image_urls, NOW(), NOW()
                )
            """)

            await session.execute(insert_sql, {
                "pose_id": pose["pose_id"],
                "name_english": pose["name_english"],
                "name_sanskrit": pose["name_sanskrit"],
                "category": pose["category"],
                "difficulty_level": pose["difficulty_level"],
                "description": pose["description"],
                "instructions": pose["instructions"],
                "benefits": pose["benefits"],
                "contraindications": pose["contraindications"],
                "target_areas": pose["target_areas"],
                "image_urls": pose["image_urls"]
            })
            inserted += 1

            if inserted % 10 == 0:
                print(f"Inserted {inserted} poses...")

        await session.commit()
        print(f"Successfully migrated {inserted} poses to PostgreSQL")

    conn.close()


if __name__ == "__main__":
    asyncio.run(migrate_poses())
