"""
Script to automatically import poses from poses.yaml into the database.
Non-interactive version for deployment/automation.

Usage:
    python -m scripts.import_poses_auto [--force]
"""
import asyncio
import yaml
import sys
from pathlib import Path
import argparse

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_database
from app.models.pose import Pose, PoseCategory, DifficultyLevel


# Category mapping from YAML to database enum
CATEGORY_MAP = {
    "standing": PoseCategory.STANDING,
    "seated": PoseCategory.SEATED,
    "balancing": PoseCategory.BALANCING,
    "backbend": PoseCategory.BACKBENDS,
    "forward_bend": PoseCategory.FORWARD_BENDS,
    "twist": PoseCategory.TWISTS,
    "inversion": PoseCategory.INVERSIONS,
    "arm_balance": PoseCategory.ARM_BALANCES,
    "restorative": PoseCategory.RESTORATIVE,
    "hip_opener": PoseCategory.RESTORATIVE,  # Map hip_opener to restorative for now
}


async def import_poses(force_reimport=False):
    """Import poses from YAML file into database."""

    # Initialize database
    print("Initializing database...")
    await init_database()

    # Load YAML file
    yaml_path = Path(__file__).parent.parent.parent / "content" / "poses.yaml"
    print(f"Loading poses from: {yaml_path}")

    if not yaml_path.exists():
        print(f"ERROR: Poses file not found at {yaml_path}")
        return

    with open(yaml_path, "r") as file:
        data = yaml.safe_load(file)

    poses_data = data.get("poses", [])
    print(f"Found {len(poses_data)} poses to import")

    async with AsyncSessionLocal() as session:
        # Check existing poses
        result = await session.execute(select(Pose))
        existing_poses = result.scalars().all()
        existing_count = len(existing_poses)

        if existing_count > 0:
            print(f"Found {existing_count} existing poses in database.")
            if force_reimport:
                print("Force reimport enabled - clearing existing poses...")
                # Delete all existing poses
                for pose in existing_poses:
                    await session.delete(pose)
                await session.commit()
                print("Cleared existing poses.")
            else:
                print("Skipping import to avoid duplicates. Use --force to reimport.")
                return

        # Import poses
        imported_count = 0
        skipped_count = 0

        for pose_data in poses_data:
            try:
                # Map category from YAML format to enum
                yaml_category = pose_data.get("category", "").lower()
                category = CATEGORY_MAP.get(yaml_category)

                if not category:
                    print(f"Warning: Unknown category '{yaml_category}' for pose '{pose_data.get('name_english')}'. Skipping.")
                    skipped_count += 1
                    continue

                # Map difficulty
                difficulty_str = pose_data.get("difficulty_level", "beginner").upper()
                try:
                    difficulty = DifficultyLevel[difficulty_str]
                except KeyError:
                    print(f"Warning: Unknown difficulty '{difficulty_str}' for pose '{pose_data.get('name_english')}'. Using BEGINNER.")
                    difficulty = DifficultyLevel.BEGINNER

                # Prepare benefits (convert list to text)
                benefits = pose_data.get("benefits", [])
                benefits_text = "\n".join(f"• {benefit}" for benefit in benefits) if benefits else None

                # Prepare contraindications (convert list to text)
                contraindications = pose_data.get("contraindications", [])
                contraindications_text = "\n".join(f"• {item}" for item in contraindications) if contraindications else None

                # Create pose object
                pose = Pose(
                    name_english=pose_data.get("name_english"),
                    name_sanskrit=pose_data.get("name_sanskrit"),
                    category=category,
                    difficulty_level=difficulty,
                    description=pose_data.get("description", ""),
                    instructions=pose_data.get("instructions", []),
                    benefits=benefits_text,
                    contraindications=contraindications_text,
                    target_areas=pose_data.get("target_areas", []),
                    image_urls=["https://placeholder.com/300"]  # Placeholder until we have real images
                )

                session.add(pose)
                imported_count += 1
                print(f"✓ Imported: {pose.name_english} ({pose.name_sanskrit})")

            except Exception as error:
                print(f"✗ Error importing pose '{pose_data.get('name_english', 'Unknown')}': {error}")
                skipped_count += 1
                continue

        # Commit all poses
        try:
            await session.commit()
            print(f"\n{'='*60}")
            print(f"Import complete!")
            print(f"Successfully imported: {imported_count} poses")
            if skipped_count > 0:
                print(f"Skipped: {skipped_count} poses")
            print(f"{'='*60}")
        except Exception as error:
            await session.rollback()
            print(f"Error committing to database: {error}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import poses from YAML to database")
    parser.add_argument("--force", action="store_true", help="Force reimport, clearing existing poses")
    args = parser.parse_args()

    asyncio.run(import_poses(force_reimport=args.force))
