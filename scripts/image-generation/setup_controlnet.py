#!/usr/bin/env python3
"""
Set up ControlNet pose generation by creating or finding pose reference images.

This script will:
1. Download sample yoga pose images from free sources
2. Extract pose skeletons using MediaPipe
3. Save skeletons for use with ControlNet

Requirements:
    pip install mediapipe opencv-python pillow requests
"""

import os
import cv2
import mediapipe as mp
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
import json

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)


def download_image(url, save_path):
    """Download image from URL."""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.save(save_path)
    return save_path


def extract_pose_skeleton(image_path, output_path):
    """Extract pose skeleton from image using MediaPipe."""
    # Read image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Failed to load image: {image_path}")
        return None

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process with MediaPipe
    results = pose.process(image_rgb)

    if not results.pose_landmarks:
        print(f"No pose detected in: {image_path}")
        return None

    # Create blank canvas (white background)
    h, w = image.shape[:2]
    skeleton_image = 255 * np.ones((h, w, 3), dtype=np.uint8)

    # Draw the pose skeleton
    mp_drawing.draw_landmarks(
        skeleton_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=2),
    )

    # Save skeleton
    cv2.imwrite(str(output_path), skeleton_image)
    print(f"Saved skeleton: {output_path}")
    return output_path


def create_simple_pose_skeleton(pose_name, output_path, width=512, height=768):
    """
    Create a simple hand-drawn style pose skeleton.
    This is a placeholder - in production, use actual pose references.
    """
    import numpy as np

    # Create white background
    img = 255 * np.ones((height, width, 3), dtype=np.uint8)

    # Define some basic stick figure poses
    # Format: (x, y) normalized coordinates
    poses = {
        "Downward Dog": [
            # Head, shoulders, elbows, wrists, hips, knees, ankles
            [(0.5, 0.3), (0.4, 0.35), (0.3, 0.25), (0.2, 0.15)],  # Left arm
            [(0.5, 0.3), (0.6, 0.35), (0.7, 0.25), (0.8, 0.15)],  # Right arm
            [(0.5, 0.3), (0.4, 0.5), (0.3, 0.7), (0.2, 0.85)],    # Left leg
            [(0.5, 0.3), (0.6, 0.5), (0.7, 0.7), (0.8, 0.85)],    # Right leg
        ],
        "Warrior 2": [
            # Standing pose with arms extended
            [(0.5, 0.2), (0.4, 0.3), (0.2, 0.3), (0.1, 0.3)],     # Left arm
            [(0.5, 0.2), (0.6, 0.3), (0.8, 0.3), (0.9, 0.3)],     # Right arm
            [(0.5, 0.2), (0.4, 0.5), (0.3, 0.75), (0.25, 0.95)],  # Left leg (bent)
            [(0.5, 0.2), (0.6, 0.5), (0.7, 0.8), (0.75, 0.95)],   # Right leg
        ],
    }

    if pose_name not in poses:
        # Default simple standing pose
        pose_lines = [
            [(0.5, 0.2), (0.5, 0.5)],  # Spine
            [(0.5, 0.2), (0.3, 0.4)],  # Left arm
            [(0.5, 0.2), (0.7, 0.4)],  # Right arm
            [(0.5, 0.5), (0.4, 0.9)],  # Left leg
            [(0.5, 0.5), (0.6, 0.9)],  # Right leg
        ]
    else:
        pose_lines = poses[pose_name]

    # Draw lines
    for limb in pose_lines:
        for i in range(len(limb) - 1):
            pt1 = (int(limb[i][0] * width), int(limb[i][1] * height))
            pt2 = (int(limb[i+1][0] * width), int(limb[i+1][1] * height))
            cv2.line(img, pt1, pt2, (0, 0, 0), 3)
            cv2.circle(img, pt1, 5, (0, 0, 0), -1)
            cv2.circle(img, pt2, 5, (0, 0, 0), -1)

    cv2.imwrite(str(output_path), img)
    return output_path


# Free yoga pose image sources (Creative Commons / royalty-free)
YOGA_POSE_URLS = {
    "Downward Dog": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800",
    "Warrior 2": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=800",
    "Tree Pose": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800",
    # Add more as needed
}


def main():
    import numpy as np  # Import here for the simple skeleton creation

    print("Setting up ControlNet pose references...\n")

    # Create directories
    reference_dir = Path("pose_references")
    skeleton_dir = Path("pose_skeletons")
    reference_dir.mkdir(exist_ok=True)
    skeleton_dir.mkdir(exist_ok=True)

    created_skeletons = {}

    # Method 1: Download and extract from real photos (best quality)
    print("Method 1: Extracting poses from real yoga photos...")
    for pose_name, url in YOGA_POSE_URLS.items():
        try:
            print(f"\nProcessing {pose_name}...")

            # Download reference image
            ref_path = reference_dir / f"{pose_name.replace(' ', '_')}.jpg"
            if not ref_path.exists():
                print(f"  Downloading reference image...")
                download_image(url, ref_path)

            # Extract skeleton
            skeleton_path = skeleton_dir / f"{pose_name.replace(' ', '_')}.jpg"
            if not skeleton_path.exists():
                print(f"  Extracting pose skeleton...")
                result = extract_pose_skeleton(ref_path, skeleton_path)
                if result:
                    created_skeletons[pose_name] = str(skeleton_path)
        except Exception as e:
            print(f"  Error processing {pose_name}: {e}")

    # Method 2: Create simple stick figures for poses without references
    print("\n\nMethod 2: Creating simple stick figure poses...")
    common_poses = [
        "Downward Dog", "Warrior 2", "Warrior 1", "Tree Pose",
        "Triangle Pose", "Child's Pose", "Mountain Pose", "Plank Pose"
    ]

    for pose_name in common_poses:
        skeleton_path = skeleton_dir / f"{pose_name.replace(' ', '_')}_simple.jpg"
        if pose_name not in created_skeletons and not skeleton_path.exists():
            print(f"  Creating simple skeleton for {pose_name}...")
            create_simple_pose_skeleton(pose_name, skeleton_path)
            created_skeletons[f"{pose_name} (simple)"] = str(skeleton_path)

    # Save manifest
    manifest = {
        "pose_skeletons": created_skeletons,
        "instructions": "Use these skeleton images with ControlNet for accurate pose generation"
    }

    with open(skeleton_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "="*60)
    print("✓ Setup complete!")
    print("="*60)
    print(f"Pose skeletons saved to: {skeleton_dir}/")
    print(f"Total skeletons created: {len(created_skeletons)}")
    print("\nNext steps:")
    print("1. Review the pose skeletons")
    print("2. Upload them to a public URL (imgur, cloudflare, etc.)")
    print("3. Use with generate_replicate.py --pose-reference-url")
    print("\nOr run: python generate_with_controlnet.py")


if __name__ == "__main__":
    main()
