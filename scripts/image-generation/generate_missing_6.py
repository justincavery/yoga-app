#!/usr/bin/env python3
"""
Generate images for the 6 missing poses using Gemini API
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional
import google.generativeai as genai
from PIL import Image

# Configuration
API_KEY = "AIzaSyB3dFFtrAYYXVdePiWTSbrN0eRKWxxojck"
OUTPUT_DIR = "../../content/images/poses"
MODEL = "gemini-2.5-flash-image"
RATE_LIMIT_SECONDS = 60

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Missing poses with prompts from MISSING_POSES_PROMPTS.md
MISSING_POSES = {
    "firefly-pose.jpg": """Blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, performing Firefly Pose (Tittibhasana). Arms straight supporting body weight, legs extended wide to the sides parallel to ground, hips lifted off floor, balancing on hands, core engaged, advanced arm balance pose. Professional yoga photography, clean white background, proper form demonstration.""",

    "extended-puppy-pose.jpg": """Blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, performing Extended Puppy Pose (Uttana Shishosana). On hands and knees, walking hands forward, chest melting toward ground, arms extended, forehead or chin resting on mat, hips high over knees, spine lengthened, gentle heart opener. Professional yoga photography, clean white background, proper form demonstration.""",

    "eagle-pose.jpg": """Blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, performing Eagle Pose (Garudasana). Standing on one leg, other leg wrapped around standing leg, arms wrapped together with elbows bent at chest level, palms together, knees bent in slight squat, balanced standing twist pose. Professional yoga photography, clean white background, proper form demonstration.""",

    "eight-angle-pose.jpg": """Blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, performing Eight Angle Pose (Astavakrasana). Advanced arm balance, body parallel to ground, legs hooked around one arm, both legs extended to side, other arm supporting, core tight, challenging twist and balance. Professional yoga photography, clean white background, proper form demonstration.""",

    "feathered-peacock-pose.jpg": """Blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, performing Feathered Peacock Pose (Pincha Mayurasana). Forearm stand, forearms on mat parallel, body inverted vertical, legs together extended upward, core engaged, advanced inversion balance. Professional yoga photography, clean white background, proper form demonstration.""",

    "destroyer-of-the-universe-pose.jpg": """Blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, performing Destroyer of the Universe Pose (Bhairavasana). Advanced pose combining splits and backbend, one leg extended forward, other leg extended back and up toward head, hands on ground or catching back foot, deep hip opener with extreme flexibility. Professional yoga photography, clean white background, proper form demonstration."""
}


def generate_image(prompt: str, filename: str) -> Optional[bytes]:
    """Generate image using Gemini API"""
    try:
        logger.info(f"Generating: {filename}")

        # Configure and create model
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(MODEL)

        # Add safety context
        safe_prompt = f"professional yoga instruction, {prompt}, athletic training photo"

        # Generate image
        response = model.generate_content(safe_prompt)

        # Extract image
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data is not None:
                    logger.info(f"✓ Generated {filename}")
                    return part.inline_data.data

        logger.error(f"✗ No image data in response for {filename}")
        return None

    except Exception as e:
        logger.error(f"✗ Error generating {filename}: {str(e)}")
        return None


def save_image(image_data: bytes, filename: str) -> bool:
    """Save image and create thumbnail"""
    try:
        output_path = Path(OUTPUT_DIR) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save full-size image
        with open(output_path, 'wb') as f:
            f.write(image_data)

        logger.info(f"✓ Saved: {output_path}")

        # Create thumbnail
        with Image.open(output_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')

            img.thumbnail((400, 400), Image.Resampling.LANCZOS)

            thumb_filename = filename.replace('.jpg', '-thumb.jpg')
            thumb_path = output_path.parent / thumb_filename

            img.save(thumb_path, 'JPEG', quality=85, optimize=True)
            logger.info(f"✓ Thumbnail: {thumb_path}")

        return True

    except Exception as e:
        logger.error(f"✗ Failed to save {filename}: {str(e)}")
        return False


def main():
    """Generate all 6 missing pose images"""
    logger.info("="*80)
    logger.info("Generating 6 Missing Pose Images")
    logger.info("="*80)

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    success_count = 0
    failed_count = 0

    for idx, (filename, prompt) in enumerate(MISSING_POSES.items(), 1):
        logger.info(f"\n[{idx}/6] {filename}")

        # Generate image
        image_data = generate_image(prompt, filename)

        if image_data:
            if save_image(image_data, filename):
                success_count += 1
            else:
                failed_count += 1
        else:
            failed_count += 1

        # Rate limiting (except for last one)
        if idx < len(MISSING_POSES):
            logger.info(f"⏳ Waiting {RATE_LIMIT_SECONDS} seconds (rate limiting)...")
            time.sleep(RATE_LIMIT_SECONDS)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("GENERATION COMPLETE")
    logger.info("="*80)
    logger.info(f"Success: {success_count}/6")
    logger.info(f"Failed: {failed_count}/6")
    logger.info("="*80)


if __name__ == "__main__":
    main()
