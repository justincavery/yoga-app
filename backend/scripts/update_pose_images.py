"""
Update pose images in database with new optimized JPEG files.
Maps image filenames to pose names and updates image_urls.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal, init_database
from app.models.pose import Pose

# Mapping of image filenames to pose English names from database
# Matched to exact pose names in database (IDs 1-80)
IMAGE_POSE_MAPPING = {
    "mountain-pose.jpg": "Mountain Pose",  # ID 1
    "childs-pose.jpg": "Child's Pose",  # ID 2
    "downward-facing-dog.jpg": "Downward Facing Dog",  # ID 3
    "cat-pose.jpg": "Cat-Cow Pose",  # ID 4
    "cow-pose.jpg": "Cat-Cow Pose",  # ID 4 (alternative)
    "corpse-pose.jpg": "Corpse Pose",  # ID 5
    "easy-pose.jpg": "Easy Pose",  # ID 6
    "standing-forward-fold.jpg": "Standing Forward Bend",  # ID 7
    "warrior-1.jpg": "Warrior I",  # ID 8
    "bridge-pose.jpg": "Bridge Pose",  # ID 9
    "tree-pose.jpg": "Tree Pose",  # ID 10
    "warrior-2.jpg": "Warrior II",  # ID 11
    "triangle-pose.jpg": "Triangle Pose",  # ID 12
    "extended-side-angle.jpg": "Extended Side Angle Pose",  # ID 13
    "seated-forward-bend.jpg": "Seated Forward Bend",  # ID 14
    "boat-pose.jpg": "Boat Pose",  # ID 15
    "cobra-pose.jpg": "Cobra Pose",  # ID 16
    "camel-pose.jpg": "Camel Pose",  # ID 17
    "seated-spinal-twist.jpg": "Seated Spinal Twist",  # ID 18
    "dolphin-pose.jpg": "Dolphin Pose",  # ID 19
    "pigeon-pose.jpg": "Pigeon Pose",  # ID 20
    "crow-pose.jpg": "Crow Pose",  # ID 21
    "headstand.jpg": "Headstand",  # ID 22
    "wheel-pose.jpg": "Wheel Pose",  # ID 23
    "side-plank.jpg": "Side Plank",  # ID 24
    "bound-angle-pose.jpg": "Bound Angle Pose",  # ID 28
    "plow-pose.jpg": "Plow Pose",  # ID 29
    "shoulder-stand.jpg": "Shoulder Stand",  # ID 30
    "legs-up-the-wall.jpg": "Legs Up the Wall",  # ID 33
    "happy-baby.jpg": "Happy Baby Pose",  # ID 34
    "garland-pose.jpg": "Garland Pose",  # ID 39
    "locust-pose.jpg": "Locust Pose",  # ID 40
    "wide-legged-forward-fold.jpg": "Wide-Legged Forward Bend",  # ID 41
    "reclining-hand-to-big-toe.jpg": "Reclining Hand to Big Toe Pose",  # ID 44
    "low-lunge.jpg": "Low Lunge",  # ID 45
    "revolved-triangle.jpg": "Revolved Triangle Pose",  # ID 46
    "half-moon.jpg": "Half Moon Pose",  # ID 47
    "warrior-3.jpg": "Warrior III",  # ID 48
    "standing-split.jpg": "Standing Split",  # ID 50
    "bow-pose.jpg": "Bow Pose",  # ID 52
    "lizard-pose.jpg": "Lizard Pose",  # ID 53
    "reverse-warrior.jpg": "Reverse Warrior",  # ID 54
    "fish-pose.jpg": "Fish Pose",  # ID 55
    "handstand.jpg": "Handstand",  # ID 65
    # Note: The following images don't have exact matches in current database:
    # - chair-pose.jpg (no Chair Pose in DB)
    # - chaturanga.jpg (no Chaturanga in DB)
    # - plank-pose.jpg (no Plank Pose in DB)
    # - forearm-plank.jpg (no Forearm Plank in DB)
    # - upward-facing-dog.jpg (no Upward Facing Dog in DB, Cobra is different)
    # - high-lunge.jpg (no High Lunge in DB, Low Lunge exists)
}

# CDN base URL (will be handled by backend CDN service)
CDN_BASE = "/images/poses"


async def update_pose_images():
    """Update database with new image URLs."""

    # Initialize database
    await init_database()

    async with AsyncSessionLocal() as session:
        # Get all poses
        result = await session.execute(select(Pose))
        all_poses = result.scalars().all()

        print(f"Found {len(all_poses)} poses in database\n")

        updated_count = 0
        not_found_count = 0

        # Update poses with matching images
        for filename, pose_name in IMAGE_POSE_MAPPING.items():
            # Find pose by English name
            result = await session.execute(
                select(Pose).where(Pose.name_english == pose_name)
            )
            pose = result.scalar_one_or_none()

            if pose:
                # Update image URLs with both full-size and thumbnail
                image_urls = [
                    f"{CDN_BASE}/{filename}",
                ]

                pose.image_urls = image_urls
                print(f"✓ Updated: {pose_name}")
                print(f"  Image: {filename}")
                updated_count += 1
            else:
                print(f"✗ Not found in database: {pose_name}")
                not_found_count += 1

        # Commit changes
        await session.commit()

        print(f"\n{'='*60}")
        print(f"Updated {updated_count} poses with new images")
        if not_found_count > 0:
            print(f"Not found: {not_found_count} poses")
        print(f"{'='*60}")

        # Show sample of updated poses
        if updated_count > 0:
            print("\nSample updated pose:")
            result = await session.execute(
                select(Pose).where(Pose.name_english == "Mountain Pose")
            )
            sample = result.scalar_one_or_none()
            if sample:
                print(f"  Name: {sample.name_english}")
                print(f"  Images: {sample.image_urls}")


async def list_all_poses():
    """List all poses in database to help with mapping."""
    await init_database()

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Pose).order_by(Pose.pose_id))
        all_poses = result.scalars().all()

        print("\nAll poses in database:")
        print(f"{'='*60}")
        for pose in all_poses:
            print(f"ID {pose.pose_id}: {pose.name_english} ({pose.name_sanskrit or 'N/A'})")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update pose images in database")
    parser.add_argument("--list", action="store_true", help="List all poses in database")
    args = parser.parse_args()

    if args.list:
        asyncio.run(list_all_poses())
    else:
        asyncio.run(update_pose_images())
