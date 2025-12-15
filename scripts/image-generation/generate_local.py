#!/usr/bin/env python3
"""
Local Stable Diffusion image generation using diffusers library.
Generates yoga pose images with ControlNet pose guidance.

Requirements:
    pip install diffusers transformers accelerate controlnet_aux torch pillow
"""

import os
import sys
import json
import torch
from pathlib import Path
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers import UniPCMultistepScheduler
from PIL import Image
import argparse

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from app.core.config import settings


class LocalPoseGenerator:
    def __init__(self, model_path=None, output_dir="generated_poses"):
        """
        Initialize the local pose generator.

        Args:
            model_path: Path to Stable Diffusion model (default: downloads SD 1.5)
            output_dir: Directory to save generated images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        print("Loading models... (this may take a few minutes on first run)")

        # Load ControlNet OpenPose model
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_openpose",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )

        # Load Stable Diffusion pipeline with ControlNet
        model_id = model_path or "runwayml/stable-diffusion-v1-5"
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            model_id,
            controlnet=controlnet,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            safety_checker=None
        )

        # Optimize for speed
        self.pipe.scheduler = UniPCMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )

        # Move to GPU if available
        if torch.cuda.is_available():
            self.pipe = self.pipe.to("cuda")
            print("Using GPU acceleration")
        else:
            print("Using CPU (this will be slower)")

        # Enable memory optimizations
        self.pipe.enable_attention_slicing()

    def generate_pose_image(
        self,
        pose_name,
        pose_reference_image,
        character_description="professional yoga instructor wearing navy blue yoga outfit",
        num_variations=4,
        seed=None
    ):
        """
        Generate yoga pose images.

        Args:
            pose_name: Name of the yoga pose
            pose_reference_image: Path to pose skeleton/reference image
            character_description: Description of the person/character
            num_variations: Number of image variations to generate
            seed: Random seed for reproducibility

        Returns:
            List of paths to generated images
        """
        # Load pose reference image
        if isinstance(pose_reference_image, str):
            pose_image = Image.open(pose_reference_image)
        else:
            pose_image = pose_reference_image

        # Resize if needed
        pose_image = pose_image.resize((512, 768))

        # Build prompt
        prompt = f"{character_description}, performing {pose_name}, yoga studio, natural window lighting, professional photography, high quality, detailed, 8k"

        negative_prompt = (
            "blurry, low quality, deformed, disfigured, extra limbs, "
            "bad anatomy, poorly drawn hands, mutation, watermark, "
            "signature, text, error, cropped, worst quality"
        )

        print(f"\nGenerating {num_variations} variations for: {pose_name}")
        print(f"Prompt: {prompt}")

        generated_paths = []

        for i in range(num_variations):
            # Set seed for reproducibility
            generator = torch.Generator(device=self.pipe.device)
            if seed is not None:
                generator.manual_seed(seed + i)

            # Generate image
            image = self.pipe(
                prompt,
                negative_prompt=negative_prompt,
                image=pose_image,
                num_inference_steps=20,
                generator=generator,
                controlnet_conditioning_scale=1.0,
            ).images[0]

            # Save image
            safe_pose_name = pose_name.replace(" ", "_").replace("/", "-")
            output_path = self.output_dir / f"{safe_pose_name}_{i+1}.jpg"
            image.save(output_path, quality=95)
            generated_paths.append(str(output_path))

            print(f"  Saved: {output_path}")

        return generated_paths


def get_poses_from_db():
    """Fetch poses from database."""
    import psycopg2
    import psycopg2.extras

    try:
        conn = psycopg2.connect(
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, sanskrit_name FROM poses ORDER BY id")
        poses = cur.fetchall()
        conn.close()
        return poses
    except Exception as e:
        print(f"Error fetching poses from database: {e}")
        print("Make sure the backend database is running.")
        return []


def create_simple_pose_reference(pose_name, output_path):
    """
    Create a simple pose reference image (placeholder).
    In production, use MediaPipe or OpenPose to extract pose from real images.
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (512, 768), color='white')
    draw = ImageDraw.Draw(img)

    # Draw a simple stick figure as placeholder
    # In production, replace this with actual pose detection
    draw.text((256, 384), f"Pose Reference\n{pose_name}",
              fill='black', anchor='mm')

    img.save(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate yoga pose images locally using Stable Diffusion"
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help="Path to custom Stable Diffusion model"
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
        "--variations", type=int, default=4,
        help="Number of variations per pose (default: 4)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--character", type=str,
        default="professional yoga instructor wearing navy blue yoga outfit",
        help="Character description for consistency"
    )

    args = parser.parse_args()

    # Initialize generator
    generator = LocalPoseGenerator(
        model_path=args.model,
        output_dir=args.output
    )

    # Get poses to generate
    if args.poses:
        poses = [{"name": name} for name in args.poses]
    else:
        poses = get_poses_from_db()
        if not poses:
            print("No poses found. Using example poses.")
            poses = [
                {"id": 1, "name": "Downward Dog"},
                {"id": 2, "name": "Warrior 2"},
                {"id": 3, "name": "Tree Pose"},
            ]

    print(f"\nGenerating images for {len(poses)} poses...")
    print(f"Variations per pose: {args.variations}")
    print(f"Output directory: {args.output}\n")

    results = {}

    for pose in poses:
        pose_name = pose["name"]

        # Create/get pose reference image
        # TODO: Replace with actual pose skeleton extraction
        reference_path = Path(args.output) / f"ref_{pose_name.replace(' ', '_')}.jpg"
        if not reference_path.exists():
            create_simple_pose_reference(pose_name, reference_path)

        # Generate images
        generated_paths = generator.generate_pose_image(
            pose_name=pose_name,
            pose_reference_image=str(reference_path),
            character_description=args.character,
            num_variations=args.variations,
            seed=args.seed
        )

        results[pose_name] = generated_paths

    # Save results manifest
    manifest_path = Path(args.output) / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Generation complete!")
    print(f"  Total images: {sum(len(paths) for paths in results.values())}")
    print(f"  Manifest saved: {manifest_path}")
    print(f"\nNext steps:")
    print(f"  1. Review generated images in {args.output}/")
    print(f"  2. Select best variations")
    print(f"  3. Upload to cloud storage")
    print(f"  4. Update database with image URLs")


if __name__ == "__main__":
    main()
