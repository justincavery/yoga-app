#!/usr/bin/env python3
"""
Generate yoga pose images using ControlNet with local pose skeletons.

This script converts local skeleton images to base64 and uses them with
Replicate's ControlNet model for accurate pose generation.
"""

import os
import sys
import base64
import replicate
from pathlib import Path
import json
from PIL import Image
from io import BytesIO
import requests

# Check API token
if not os.environ.get("REPLICATE_API_TOKEN"):
    print("Error: REPLICATE_API_TOKEN not set")
    sys.exit(1)

def image_to_data_url(image_path):
    """Convert local image to data URL for Replicate."""
    with open(image_path, 'rb') as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_data}"

def generate_with_controlnet(pose_name, skeleton_path, output_dir="controlnet_generated"):
    """Generate yoga pose image using ControlNet."""

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"\nGenerating: {pose_name}")
    print(f"Using skeleton: {skeleton_path}")

    # Convert skeleton to data URL
    skeleton_data_url = image_to_data_url(skeleton_path)

    # Character description
    character = "fit brunette woman yoga instructor, 35 years old, wearing gray yoga outfit"

    # Build prompt
    prompt = (
        f"{character}, performing {pose_name} yoga pose, "
        f"full body view, proper yoga form, "
        f"yoga studio, natural lighting, "
        f"professional instructional photo, high quality"
    )

    print(f"Prompt: {prompt[:80]}...")

    try:
        # Use ControlNet Pose model
        output = replicate.run(
            "jagilley/controlnet-pose",
            input={
                "image": skeleton_data_url,
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, deformed, extra limbs, missing limbs, bad anatomy",
                "num_samples": 4,
                "image_resolution": "512",
                "ddim_steps": 20,
                "scale": 9.0,
                "eta": 0.0
            }
        )

        # Download and save generated images
        saved_paths = []
        for i, image_url in enumerate(output):
            print(f"  Downloading image {i+1}/4...")

            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))

            safe_name = pose_name.replace(" ", "_").replace("'", "")
            output_path = output_dir / f"{safe_name}_{i+1}.jpg"
            img.save(output_path, quality=95)
            saved_paths.append(str(output_path))

            print(f"    Saved: {output_path}")

        return saved_paths

    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("="*60)
    print("ControlNet Pose Generation")
    print("="*60)

    skeleton_dir = Path("pose_skeletons")

    if not skeleton_dir.exists():
        print("Error: pose_skeletons/ directory not found")
        print("Run: python setup_controlnet.py first")
        sys.exit(1)

    # Find all skeleton images
    skeletons = list(skeleton_dir.glob("*_simple.jpg"))

    if not skeletons:
        print("Error: No skeleton images found in pose_skeletons/")
        sys.exit(1)

    print(f"\nFound {len(skeletons)} pose skeletons")
    print(f"Generating 4 variations per pose")
    print(f"Estimated cost: ${len(skeletons) * 4 * 0.005:.2f}\n")

    results = {}

    for skeleton_path in skeletons:
        # Extract pose name from filename
        # e.g., "Warrior_2_simple.jpg" -> "Warrior 2"
        pose_name = skeleton_path.stem.replace("_simple", "").replace("_", " ")

        # Generate images
        generated_paths = generate_with_controlnet(pose_name, skeleton_path)
        results[pose_name] = generated_paths

    # Save manifest
    manifest_path = Path("controlnet_generated/manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*60)
    print("✓ Generation complete!")
    print("="*60)
    print(f"Total images: {sum(len(paths) for paths in results.values())}")
    print(f"Output directory: controlnet_generated/")
    print(f"Manifest: {manifest_path}")
    print("\nReview the images and pick the best ones!")

if __name__ == "__main__":
    main()
