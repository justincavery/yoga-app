#!/bin/bash
# Quick inline seed - run on server
# Usage: ssh root@SERVER "bash -s" < seed-inline.sh

cd /opt/yogaflow

# Copy content into container
docker cp content yogaflow-backend:/app/

# Create and run inline Python script
docker exec yogaflow-backend bash -c 'cat > /tmp/seed.py << "PYEOF"
import asyncio
import yaml
import sys
from pathlib import Path

sys.path.insert(0, "/app")

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_database
from app.models.pose import Pose, PoseCategory, DifficultyLevel

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
    "hip_opener": PoseCategory.RESTORATIVE,
}

async def import_poses():
    await init_database()

    yaml_path = Path("/app/content/poses.yaml")
    print(f"Loading from: {yaml_path}")

    with open(yaml_path, "r") as file:
        data = yaml.safe_load(file)

    poses_data = data.get("poses", [])
    print(f"Found {len(poses_data)} poses")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Pose))
        existing = len(result.scalars().all())

        if existing > 0:
            print(f"Database has {existing} poses - skipping")
            return

        imported = 0
        for pose_data in poses_data:
            try:
                category = CATEGORY_MAP.get(pose_data.get("category", "").lower())
                if not category:
                    continue

                difficulty_str = pose_data.get("difficulty_level", "beginner").upper()
                try:
                    difficulty = DifficultyLevel[difficulty_str]
                except KeyError:
                    difficulty = DifficultyLevel.BEGINNER

                benefits = pose_data.get("benefits", [])
                benefits_text = "\n".join(f"• {b}" for b in benefits) if benefits else None

                contraindications = pose_data.get("contraindications", [])
                contraindications_text = "\n".join(f"• {c}" for c in contraindications) if contraindications else None

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
                    image_urls=["https://placeholder.com/300"]
                )

                session.add(pose)
                imported += 1
                print(f"✓ {pose.name_english}")

            except Exception as e:
                print(f"✗ Error: {e}")
                continue

        await session.commit()
        print(f"\nImported {imported} poses!")

if __name__ == "__main__":
    asyncio.run(import_poses())
PYEOF
python /tmp/seed.py'

# Verify
echo ""
echo "Verifying..."
POSES=$(curl -s http://localhost:8000/api/v1/poses | jq -r '.total' 2>/dev/null)
echo "Poses in database: $POSES"

if [ "$POSES" -gt 0 ]; then
    echo "✅ SUCCESS!"
else
    echo "❌ FAILED"
fi
