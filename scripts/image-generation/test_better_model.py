#!/usr/bin/env python3
"""Test with a model better at human anatomy."""

import os
import replicate

if not os.environ.get("REPLICATE_API_TOKEN"):
    print("Error: Set REPLICATE_API_TOKEN first")
    exit(1)

print("Testing with FLUX model (better at human anatomy)...")

output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={
        "prompt": "professional yoga instructor in warrior 2 pose, side view, arms extended horizontally, proper yoga form, wearing navy blue yoga outfit, yoga studio, natural window lighting, high quality professional photograph, anatomically correct, perfect form",
        "num_outputs": 1,
        "aspect_ratio": "2:3",
        "output_format": "jpg",
        "output_quality": 90
    }
)

print(f"\nGenerated: {output}")
print("FLUX model should have better human anatomy!")
