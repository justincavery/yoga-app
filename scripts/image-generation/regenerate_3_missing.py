#!/usr/bin/env python3
"""
Regenerate the 3 missing poses that failed to save
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional
import google.generativeai as genai
from PIL import Image
import io

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

# Only the 3 missing poses
MISSING_POSES = {
    "firefly-pose.jpg": """Blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, performing Firefly Pose (Tittibhasana). Arms straight supporting body weight, legs extended wide to the sides parallel to ground, hips lifted off floor, balancing on hands, core engaged, advanced arm balance pose. Professional yoga photography, clean white background, proper form demonstration.""",

    "eagle-pose.jpg": """Blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, performing Eagle Pose (Garudasana). Standing on one leg, other leg wrapped around standing leg, arms wrapped together with elbows bent at chest level, palms together, knees bent in slight squat, balanced standing twist pose. Professional yoga photography, clean white background, proper form demonstration.""",

    "feathered-peacock-pose.jpg": """Blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, performing Feathered Peacock Pose (Pincha Mayurasana). Forearm stand, forearms on mat parallel, body inverted vertical, legs together extended upward, core engaged, advanced inversion balance. Professional yoga photography, clean white background, proper form demonstration."""
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

        # Extract image - check all possible locations
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data

                    # Check if it's bytes or needs conversion
                    if isinstance(image_data, bytes):
                        logger.info(f"✓ Generated {filename} ({len(image_data)} bytes)")
                        return image_data
                    else:
                        logger.error(f"✗ Image data is not bytes: {type(image_data)}")
                        return None

        logger.error(f"✗ No image data in response for {filename}")

        # Debug: print response structure
        logger.debug(f"Response candidates: {len(response.candidates)}")
        for i, cand in enumerate(response.candidates):
            logger.debug(f"  Candidate {i}: {len(cand.content.parts)} parts")
            for j, part in enumerate(cand.content.parts):
                logger.debug(f"    Part {j}: inline_data={part.inline_data is not None}, text={part.text is not None}")

        return None

    except Exception as e:
        logger.error(f"✗ Error generating {filename}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def save_image(image_data: bytes, filename: str) -> bool:
    """Save image and create thumbnail"""
    try:
        output_path = Path(OUTPUT_DIR) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Verify image_data is bytes
        if not isinstance(image_data, bytes):
            logger.error(f"✗ Cannot save {filename}: image_data is {type(image_data)}, not bytes")
            return False

        # Save full-size image
        with open(output_path, 'wb') as f:
            bytes_written = f.write(image_data)
            logger.info(f"✓ Saved: {output_path} ({bytes_written} bytes)")

        # Verify file exists and is readable
        if not output_path.exists():
            logger.error(f"✗ File was not created: {output_path}")
            return False

        # Create thumbnail
        try:
            with Image.open(output_path) as img:
                logger.info(f"  Original size: {img.size[0]}x{img.size[1]} {img.format}")

                if img.mode != 'RGB':
                    img = img.convert('RGB')

                img.thumbnail((400, 400), Image.Resampling.LANCZOS)

                thumb_filename = filename.replace('.jpg', '-thumb.jpg')
                thumb_path = output_path.parent / thumb_filename

                img.save(thumb_path, 'JPEG', quality=85, optimize=True)
                logger.info(f"✓ Thumbnail: {thumb_path} ({img.size[0]}x{img.size[1]})")
        except Exception as thumb_error:
            logger.error(f"✗ Failed to create thumbnail: {thumb_error}")
            # Don't fail the whole save if thumbnail fails
            return True

        return True

    except Exception as e:
        logger.error(f"✗ Failed to save {filename}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Generate the 3 missing pose images"""
    logger.info("="*80)
    logger.info("Regenerating 3 Missing Pose Images")
    logger.info("="*80)

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    success_count = 0
    failed_count = 0

    for idx, (filename, prompt) in enumerate(MISSING_POSES.items(), 1):
        logger.info(f"\n[{idx}/3] {filename}")

        # Generate image
        image_data = generate_image(prompt, filename)

        if image_data and isinstance(image_data, bytes):
            if save_image(image_data, filename):
                success_count += 1
            else:
                failed_count += 1
        else:
            failed_count += 1
            if image_data:
                logger.error(f"  Image data type: {type(image_data)}")

        # Rate limiting (except for last one)
        if idx < len(MISSING_POSES):
            logger.info(f"⏳ Waiting {RATE_LIMIT_SECONDS} seconds (rate limiting)...")
            time.sleep(RATE_LIMIT_SECONDS)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("REGENERATION COMPLETE")
    logger.info("="*80)
    logger.info(f"Success: {success_count}/3")
    logger.info(f"Failed: {failed_count}/3")
    logger.info("="*80)

    return success_count == 3


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
