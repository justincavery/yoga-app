#!/usr/bin/env python3
"""
Test ControlNet pose generation with Replicate.
Uses pose reference images for better anatomy.
"""

import os
import replicate
from pathlib import Path

# Check API token
if not os.environ.get("REPLICATE_API_TOKEN"):
    print("Error: REPLICATE_API_TOKEN not set")
    exit(1)

print("Testing ControlNet with pose reference...")

# Using a pre-existing yoga pose skeleton image URL
# (In production, you'd extract these from real photos)
pose_reference_url = "https://i.imgur.com/Zo9qN8Y.png"  # Example yoga pose skeleton

output = replicate.run(
    "jagilley/controlnet-pose:0a69b7f85f0b7d6c54c9aeb3f9d1b8e1a6d42e8a9f5e3d1c7b2a8e5f3d1a9c6e",
    input={
        "image": pose_reference_url,
        "prompt": "professional yoga instructor, athletic woman, wearing navy blue yoga outfit, in yoga studio, natural lighting, high quality professional photo",
        "negative_prompt": "blurry, low quality, deformed, disfigured, extra limbs, bad anatomy, poorly drawn",
        "num_samples": 1,
        "image_resolution": "512"
    }
)

print(f"\nGenerated image URL: {output}")
print("\nWith ControlNet, the pose should match the skeleton and have correct anatomy!")
