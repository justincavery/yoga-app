#!/usr/bin/env python3
"""
Automated Gemini Image Generation Script for Yoga Poses
Generates images from MIDJOURNEY_SIMPLE_PROMPTS.md using Google's Gemini API
"""

import os
import re
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# Configuration
API_KEY = "AIzaSyB3dFFtrAYYXVdePiWTSbrN0eRKWxxojck"
PROMPTS_FILE = "MIDJOURNEY_SIMPLE_PROMPTS.md"
OUTPUT_DIR = "../../content/images/poses"
LOG_FILE = "gemini_generation_log.json"
DETAILED_LOG_FILE = "gemini_generation_detailed.log"

# Model configuration
MODEL_FLASH = "gemini-2.5-flash-image"
MODEL_PRO = "gemini-3-pro-image-preview"
PRO_MODEL_COUNT = 10  # First 10 poses use pro model

# Rate limiting - 1 per minute to be safe (20/min limit)
RATE_LIMIT_SECONDS = 60

# Retry configuration
MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds between retries

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DETAILED_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GeminiImageGenerator:
    """Handles image generation using Google's Gemini API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.generation_log = []
        self.start_time = datetime.now()

    def strip_midjourney_params(self, prompt: str) -> str:
        """Remove Midjourney-specific parameters from prompt"""
        # Remove --ar, --style, --v parameters
        cleaned = re.sub(r'\s*--\w+\s+[\w\d\-:.]+', '', prompt)
        return cleaned.strip()

    def modify_prompt_for_safety(self, prompt: str, attempt: int) -> str:
        """Modify prompt to avoid content policy violations"""
        modifications = [
            # Original
            prompt,
            # Add explicit yoga/fitness context
            f"fitness instructor demonstrating yoga exercise, {prompt}, athletic training photo",
            # Emphasize professional/educational context
            f"professional yoga instruction, {prompt}, educational fitness photography",
            # Add more clothing details
            f"{prompt}, wearing full athletic workout attire, professional fitness photo",
            # Emphasize studio/professional setting
            f"yoga fitness professional, {prompt}, professional studio lighting, athletic training",
            # Add age/professional context
            f"adult fitness professional, {prompt}, professional yoga instruction photo",
            # More conservative clothing
            f"{prompt}, wearing long yoga pants and athletic top, professional fitness photography",
            # Emphasize the exercise aspect
            f"athletic exercise demonstration, {prompt}, fitness training photo, yoga workout",
            # Ultra professional
            f"certified yoga instructor, {prompt}, professional fitness education, athletic demonstration",
            # Final attempt - very clinical
            f"anatomical yoga position demonstration, {prompt}, medical/fitness educational reference, professional"
        ]

        # Return the modification for this attempt
        if attempt < len(modifications):
            result = modifications[attempt]
            if attempt > 0:
                logger.info(f"  → Modification #{attempt}: Added safety context")
            return result

        # If we've exhausted modifications, add random variations
        extra_mods = [
            "professional athletic training",
            "fitness education photo",
            "exercise instruction demonstration",
            "health and wellness photography",
            "athletic performance demonstration"
        ]
        mod = extra_mods[attempt % len(extra_mods)]
        return f"{mod}, {prompt}"

    def generate_image(self, prompt: str, model_name: str, pose_name: str, attempt: int = 0) -> Optional[bytes]:
        """Generate image using Gemini API"""

        try:
            logger.info(f"  → Sending request to {model_name}")
            logger.debug(f"  → Prompt: {prompt[:100]}...")

            # Create model instance
            model = genai.GenerativeModel(model_name)

            # Generate image
            response = model.generate_content(prompt)

            # Extract image from response
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data is not None:
                        logger.info(f"  ✓ Successfully generated image")
                        return part.inline_data.data

                    elif part.text is not None:
                        # Sometimes the model returns text instead of image
                        logger.warning(f"  ⚠ Model returned text: {part.text[:100]}")

            logger.error(f"  ✗ No image data in response")
            return None

        except Exception as e:
            error_msg = str(e)
            logger.error(f"  ✗ Exception during generation: {error_msg}")

            # Check for specific error types
            if "content policy" in error_msg.lower() or "safety" in error_msg.lower():
                logger.warning(f"  ⚠ Content policy violation (attempt {attempt + 1})")
            elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                logger.warning(f"  ⚠ Rate limit hit, waiting extra time...")
                time.sleep(30)

            return None

    def save_image(self, image_data: bytes, filename: str) -> bool:
        """Save image data to file"""
        try:
            output_path = Path(OUTPUT_DIR) / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(image_data)

            logger.info(f"  ✓ Saved to {output_path}")

            # Verify it's a valid image
            try:
                img = Image.open(output_path)
                logger.info(f"  ✓ Verified: {img.size[0]}x{img.size[1]} {img.format}")
            except Exception as e:
                logger.warning(f"  ⚠ Could not verify image: {e}")

            return True

        except Exception as e:
            logger.error(f"  ✗ Failed to save image: {str(e)}")
            return False

    def parse_prompts_file(self) -> List[Tuple[str, str]]:
        """Parse MIDJOURNEY_SIMPLE_PROMPTS.md and extract pose names and prompts"""
        poses = []

        with open(PROMPTS_FILE, 'r') as f:
            content = f.read()

        # Find all pose sections using regex
        # Pattern: ### NUMBER. POSE NAME followed by ``` prompt ```
        pattern = r'###\s+\d+\.\s+([^\n]+)\s*\n```\s*\n([^`]+)\n```'
        matches = re.findall(pattern, content)

        for pose_name, prompt in matches:
            pose_name = pose_name.strip()
            prompt = prompt.strip()

            # Strip Midjourney parameters
            cleaned_prompt = self.strip_midjourney_params(prompt)

            poses.append((pose_name, cleaned_prompt))
            logger.info(f"Parsed: {pose_name}")

        logger.info(f"\nFound {len(poses)} poses to generate")
        return poses

    def generate_all_poses(self):
        """Main function to generate all pose images"""
        logger.info("="*80)
        logger.info("Starting Gemini Yoga Pose Image Generation")
        logger.info("="*80)

        # Parse prompts
        logger.info("\n1. Parsing prompts file...")
        poses = self.parse_prompts_file()

        if not poses:
            logger.error("No poses found in prompts file!")
            return

        # Generate images
        logger.info(f"\n2. Generating {len(poses)} images...")
        logger.info(f"   - First {PRO_MODEL_COUNT} using {MODEL_PRO}")
        logger.info(f"   - Remaining using {MODEL_FLASH}")
        logger.info(f"   - Rate limit: 1 image per {RATE_LIMIT_SECONDS} seconds")
        logger.info(f"   - Max retries per pose: {MAX_RETRIES}")

        total_poses = len(poses)
        successful = 0
        failed = 0

        for idx, (pose_name, prompt) in enumerate(poses, 1):
            # Determine which model to use
            model = MODEL_PRO if idx <= PRO_MODEL_COUNT else MODEL_FLASH
            model_name = "PRO" if idx <= PRO_MODEL_COUNT else "FLASH"

            # Create filename (e.g., "Mountain Pose" -> "mountain-pose.png")
            filename = pose_name.lower().replace("'", "").replace(" ", "-") + ".png"

            logger.info(f"\n[{idx}/{total_poses}] {pose_name}")
            logger.info(f"  Model: {model_name}")
            logger.info(f"  Filename: {filename}")

            # Track this generation attempt
            attempt_log = {
                "pose_number": idx,
                "pose_name": pose_name,
                "filename": filename,
                "model": model,
                "timestamp": datetime.now().isoformat(),
                "attempts": []
            }

            # Try generating with retries
            image_data = None
            for attempt in range(MAX_RETRIES):
                # Modify prompt based on attempt number
                modified_prompt = self.modify_prompt_for_safety(prompt, attempt)

                attempt_info = {
                    "attempt_number": attempt + 1,
                    "prompt": modified_prompt,
                    "timestamp": datetime.now().isoformat()
                }

                # Generate image
                image_data = self.generate_image(modified_prompt, model, pose_name, attempt)

                if image_data:
                    attempt_info["status"] = "success"
                    attempt_log["attempts"].append(attempt_info)
                    break
                else:
                    attempt_info["status"] = "failed"
                    attempt_log["attempts"].append(attempt_info)

                    if attempt < MAX_RETRIES - 1:
                        logger.info(f"  → Retrying with modified prompt (attempt {attempt + 2}/{MAX_RETRIES})...")
                        time.sleep(RETRY_DELAY)

            # Save image if successful
            if image_data:
                if self.save_image(image_data, filename):
                    successful += 1
                    attempt_log["final_status"] = "success"
                    logger.info(f"  ✓ SUCCESS [{successful}/{total_poses}]")
                else:
                    failed += 1
                    attempt_log["final_status"] = "save_failed"
                    logger.error(f"  ✗ FAILED TO SAVE [{failed}/{total_poses}]")
            else:
                failed += 1
                attempt_log["final_status"] = "generation_failed"
                logger.error(f"  ✗ FAILED after {MAX_RETRIES} attempts [{failed}/{total_poses}]")

            # Add to generation log
            self.generation_log.append(attempt_log)

            # Save log after each pose
            self.save_log()

            # Rate limiting - wait before next image (except for last one)
            if idx < total_poses:
                logger.info(f"  ⏳ Waiting {RATE_LIMIT_SECONDS} seconds (rate limiting)...")
                time.sleep(RATE_LIMIT_SECONDS)

        # Final summary
        logger.info("\n" + "="*80)
        logger.info("GENERATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Total poses: {total_poses}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {(successful/total_poses)*100:.1f}%")

        elapsed = datetime.now() - self.start_time
        logger.info(f"Total time: {elapsed}")
        logger.info(f"Log saved to: {LOG_FILE}")
        logger.info(f"Detailed log: {DETAILED_LOG_FILE}")
        logger.info("="*80)

        self.save_log()

    def save_log(self):
        """Save generation log to JSON file"""
        log_data = {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "configuration": {
                "model_flash": MODEL_FLASH,
                "model_pro": MODEL_PRO,
                "pro_model_count": PRO_MODEL_COUNT,
                "rate_limit_seconds": RATE_LIMIT_SECONDS,
                "max_retries": MAX_RETRIES
            },
            "summary": {
                "total": len(self.generation_log),
                "successful": len([x for x in self.generation_log if x.get("final_status") == "success"]),
                "failed": len([x for x in self.generation_log if x.get("final_status") != "success"])
            },
            "generations": self.generation_log
        }

        with open(LOG_FILE, 'w') as f:
            json.dump(log_data, f, indent=2)


def main():
    """Main entry point"""
    logger.info("Initializing Gemini Image Generator...")

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Verify prompts file exists
    if not Path(PROMPTS_FILE).exists():
        logger.error(f"Prompts file not found: {PROMPTS_FILE}")
        return

    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = GeminiImageGenerator(API_KEY)

    # Run generation
    try:
        generator.generate_all_poses()
    except KeyboardInterrupt:
        logger.info("\n\nGeneration interrupted by user")
        generator.save_log()
    except Exception as e:
        logger.error(f"\n\nUnexpected error: {str(e)}", exc_info=True)
        generator.save_log()


if __name__ == "__main__":
    main()
