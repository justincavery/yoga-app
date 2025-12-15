#!/usr/bin/env python3
"""
Generate yoga pose images using Replicate API.
Fast, cloud-based generation with pay-per-use pricing.

Requirements:
    pip install replicate pillow requests
    export REPLICATE_API_TOKEN=your_token_here

Get your API token: https://replicate.com/account/api-tokens
"""

import os
import sys
import json
import time
import replicate
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
import argparse

# Try to import backend settings, but make it optional
try:
    sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))
    from app.core.config import settings
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    # Fallback settings
    class Settings:
        POSTGRES_USER = os.getenv("POSTGRES_USER", "yogaflow")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
        POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        POSTGRES_DB = os.getenv("POSTGRES_DB", "yogaflow")
    settings = Settings()


class ReplicatePoseGenerator:
    def __init__(self, output_dir="generated_poses"):
        """
        Initialize Replicate API generator.

        Args:
            output_dir: Directory to save generated images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Check for API token
        if not os.environ.get("REPLICATE_API_TOKEN"):
            raise ValueError(
                "REPLICATE_API_TOKEN not found in environment.\n"
                "Get your token at: https://replicate.com/account/api-tokens\n"
                "Then run: export REPLICATE_API_TOKEN=your_token_here"
            )

        print("Replicate API initialized ✓")

    def _get_pose_instructions(self, pose_name):
        """Get specific instructions for common yoga poses."""
        pose_details = {
            "Downward Dog": "side view, hands and feet on mat, hips lifted high, forming inverted V-shape, head between arms",
            "Warrior 2": "side view, legs wide apart, front knee bent at 90 degrees, arms extended horizontally, gazing forward",
            "Warrior 1": "front view, back foot turned out, front knee bent, arms raised overhead, chest open",
            "Warrior 3": "side view, standing on one leg, other leg extended back parallel to floor, arms forward, body in straight line",
            "Tree Pose": "front view, standing on one leg, other foot pressed to inner thigh, hands in prayer position at chest or overhead",
            "Triangle Pose": "side view, legs wide, front arm reaching down to shin, back arm extended up, triangle shape",
            "Child's Pose": "side view, kneeling, sitting back on heels, arms extended forward on mat, forehead resting down",
            "Mountain Pose": "front view, standing tall, feet together, arms at sides or overhead, perfect posture",
            "Plank Pose": "side view, hands under shoulders, body in straight line from head to heels, core engaged",
            "Cobra Pose": "side view, lying prone, chest lifted, arms straight, looking up, hips on mat",
            "Chair Pose": "front view, standing, knees bent as if sitting, arms raised overhead, weight in heels",
            "Bridge Pose": "side view, lying on back, knees bent, hips lifted high, feet flat on mat",
            "Pigeon Pose": "side view, front leg bent, back leg extended, hips square, chest lifted",
            "Cat Pose": "side view, on hands and knees, spine rounded up, head down",
            "Cow Pose": "side view, on hands and knees, spine arched down, head lifted",
            "Extended Side Angle": "side view, front knee bent, front arm reaching down to mat, back arm extended overhead",
            "Half Moon": "side view, balancing on one leg, other leg extended back parallel to floor, top arm reaching up",
            "Boat Pose": "front view, sitting, legs lifted and extended, arms reaching forward, V-shape body",
            "Corpse Pose": "lying flat on back, arms at sides, palms up, legs slightly apart, completely relaxed",
            "Camel Pose": "front view, kneeling, leaning back, hands reaching to heels, chest open, backbend",
            "Bow Pose": "side view, lying on belly, holding ankles, chest and thighs lifted, creating bow shape",
            "Fish Pose": "side view, lying on back, chest lifted, head tilted back, legs extended",
            "Seated Forward Fold": "side view, sitting with legs extended, folding forward over legs, reaching for feet",
            "Crow Pose": "front view, balancing on hands, knees resting on upper arms, feet lifted off ground",
            "Locust Pose": "side view, lying on belly, chest and legs lifted off mat, arms extended back"
        }

        return pose_details.get(pose_name, "proper form, full body visible")

    def generate_pose_image(
        self,
        pose_name,
        character_description="fit brunette woman yoga instructor, 35 years old, athletic build, wearing gray yoga leggings and gray yoga top",
        num_variations=4,
        width=768,
        height=1024,
        pose_reference_url=None
    ):
        """
        Generate yoga pose images using Replicate.

        Args:
            pose_name: Name of the yoga pose
            character_description: Description of the person/character
            num_variations: Number of variations to generate
            width: Image width
            height: Image height
            pose_reference_url: Optional URL to pose reference image (for ControlNet)

        Returns:
            List of paths to downloaded images
        """
        # Get pose-specific instructions
        pose_instructions = self._get_pose_instructions(pose_name)

        # Simplified prompt - focus on pose accuracy
        prompt = (
            f"professional yoga instructor wearing full yoga outfit, "
            f"demonstrating {pose_name} yoga pose, "
            f"{pose_instructions}, "
            f"full body photograph, entire body visible from head to feet, "
            f"correct yoga form and alignment, "
            f"yoga studio with wooden floor, clean background, "
            f"educational yoga instruction photo, fitness photography"
        )

        negative_prompt = (
            "blurry, low quality, deformed, disfigured, extra limbs, missing limbs, "
            "bad anatomy, poorly drawn hands, poorly drawn feet, mutation, "
            "watermark, signature, text, cropped, cut off, partial body, "
            "close-up, zoomed in, incorrect pose, wrong pose, "
            "multiple people, duplicated body parts, skeleton, bones, x-ray"
        )

        print(f"\nGenerating {num_variations} variations for: {pose_name}")
        print(f"Prompt: {prompt[:80]}...")

        generated_paths = []

        # Use FLUX 1.1 Pro Ultra for highest quality and best anatomy
        model = "black-forest-labs/flux-1.1-pro-ultra"

        # Build enhanced prompt with anatomy emphasis (avoiding words that trigger literal skeletons)
        enhanced_prompt = (
            f"{prompt}, "
            f"anatomically correct, proper human anatomy, correct body proportions, "
            f"realistic human body, accurate limb placement, "
            f"professional photography, ultra detailed, ultra high quality"
        )

        # Map dimensions to FLUX aspect ratios
        if width == 768 and height == 1024:
            aspect_ratio = "2:3"
        elif width == 1024 and height == 768:
            aspect_ratio = "3:2"
        elif width == height:
            aspect_ratio = "1:1"
        else:
            # Default to portrait for yoga poses
            aspect_ratio = "2:3"

        input_params = {
            "prompt": enhanced_prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": "jpg",
            "output_quality": 90,
            "safety_tolerance": 6,  # Maximum tolerance for yoga poses (prevent false NSFW flags)
        }

        # If pose reference provided, use ControlNet model instead
        if pose_reference_url:
            model = "jagilley/controlnet-pose:0a69b7f85f0b7d6c54c9aeb3f9d1b8e1a6d42e8a9f5e3d1c7b2a8e5f3d1a9c6e"
            input_params = {
                "image": pose_reference_url,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_samples": num_variations,
                "image_resolution": "512"
            }

        try:
            # FLUX generates one image at a time, so loop for variations
            for i in range(num_variations):
                print(f"  Generating variation {i+1}/{num_variations}...")

                # Run prediction
                output = replicate.run(model, input=input_params)

                # FLUX returns a single URL or FileOutput
                if isinstance(output, list):
                    image_url = output[0]
                else:
                    image_url = str(output)

                print(f"  Downloading image...")

                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))

                # Save image
                safe_pose_name = pose_name.replace(" ", "_").replace("/", "-")
                output_path = self.output_dir / f"{safe_pose_name}_{i+1}.jpg"
                img.save(output_path, quality=95)
                generated_paths.append(str(output_path))

                print(f"    Saved: {output_path}")

        except Exception as e:
            print(f"  Error generating {pose_name}: {e}")
            import traceback
            traceback.print_exc()

        return generated_paths


def get_poses_from_db():
    """Fetch poses from database."""
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("psycopg2 not installed. Using example poses.")
        return []

    try:
        conn = psycopg2.connect(
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, sanskrit_name, description FROM poses ORDER BY id")
        poses = cur.fetchall()
        conn.close()
        return poses
    except Exception as e:
        print(f"Database connection error: {e}")
        print("Using example poses instead.")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Generate yoga pose images using Replicate API"
    )
    parser.add_argument(
        "--output", type=str, default="generated_poses",
        help="Output directory for generated images"
    )
    parser.add_argument(
        "--poses", type=str, nargs="+",
        help="Specific pose names to generate (default: all from DB)"
    )
    parser.add_argument(
        "--variations", type=int, default=6,
        help="Number of variations per pose (default: 6)"
    )
    parser.add_argument(
        "--character", type=str,
        default="fit brunette woman yoga instructor, 35 years old, athletic build, wearing gray yoga leggings and gray yoga top",
        help="Character description for consistency"
    )
    parser.add_argument(
        "--width", type=int, default=768,
        help="Image width (default: 768)"
    )
    parser.add_argument(
        "--height", type=int, default=1024,
        help="Image height (default: 1024)"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit number of poses to generate (for testing)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="Delay between API calls in seconds (default: 0.5)"
    )

    args = parser.parse_args()

    # Initialize generator
    generator = ReplicatePoseGenerator(output_dir=args.output)

    # Get poses to generate
    if args.poses:
        poses = [{"name": name} for name in args.poses]
    else:
        poses = get_poses_from_db()
        if not poses:
            print("No poses found in database. Using example poses.")
            poses = [
                {"id": 1, "name": "Downward Dog"},
                {"id": 2, "name": "Warrior 2"},
                {"id": 3, "name": "Tree Pose"},
                {"id": 4, "name": "Child's Pose"},
                {"id": 5, "name": "Mountain Pose"},
            ]

    # Limit for testing
    if args.limit:
        poses = poses[:args.limit]

    print(f"\nGenerating images for {len(poses)} poses...")
    print(f"Variations per pose: {args.variations}")
    print(f"Output directory: {args.output}")
    print(f"Estimated cost: ${len(poses) * args.variations * 0.005:.2f}\n")

    results = {}
    total_generated = 0
    start_time = time.time()

    for i, pose in enumerate(poses, 1):
        pose_name = pose["name"]
        print(f"\n[{i}/{len(poses)}] Processing: {pose_name}")

        # Generate images
        generated_paths = generator.generate_pose_image(
            pose_name=pose_name,
            character_description=args.character,
            num_variations=args.variations,
            width=args.width,
            height=args.height
        )

        results[pose_name] = {
            "paths": generated_paths,
            "count": len(generated_paths)
        }
        total_generated += len(generated_paths)

        # Rate limiting
        if i < len(poses):
            time.sleep(args.delay)

    elapsed = time.time() - start_time

    # Save results manifest
    manifest_path = Path(args.output) / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✓ Generation complete!")
    print(f"{'='*60}")
    print(f"  Total images: {total_generated}")
    print(f"  Time elapsed: {elapsed:.1f} seconds")
    print(f"  Average: {elapsed/len(poses):.1f} seconds per pose")
    print(f"  Manifest: {manifest_path}")
    print(f"\nNext steps:")
    print(f"  1. Review images: open {args.output}/")
    print(f"  2. Select best variations")
    print(f"  3. Run upload script to cloud storage")
    print(f"  4. Update database with URLs")


if __name__ == "__main__":
    main()
