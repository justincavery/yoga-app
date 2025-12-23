#!/usr/bin/env python3
"""
Targeted regeneration script for poses that need fixes
Based on feedback from IMAGE_FEEDBACK.md
"""

import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from PIL import Image

# Configuration
API_KEY = "AIzaSyB3dFFtrAYYXVdePiWTSbrN0eRKWxxojck"
OUTPUT_DIR = "../../content/images/poses"
MODEL = "gemini-2.5-flash-image"  # Using FLASH model for regenerations
LOG_FILE = "regeneration_log.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("regeneration_detailed.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Poses to regenerate with improved prompts based on feedback
POSES_TO_FIX = {
    "chaturanga": {
        "filename": "chaturanga.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing yoga leggings, in chaturanga pose, body lowered close to and parallel to the mat, elbows bent at 90 degrees pointing back towards hips, arms tight to ribs like bottom of a push-up, body in straight line from head to heels hovering just above the floor, side view, full body visible, yoga studio, natural lighting, professional photo"
    },
    "bridge-pose": {
        "filename": "bridge-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, in bridge pose, lying flat on her back on the mat, knees bent with feet flat on floor, hips lifted high creating a straight diagonal line from shoulders on the floor up to knees then down to feet, arms flat on mat by her sides, side view showing the bridge shape clearly, full body visible, yoga studio, natural lighting, professional photo"
    },
    "wheel-pose": {
        "filename": "wheel-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing yoga leggings, in full wheel pose backbend, hands and feet planted on mat, body arched upward in deep backbend forming a wheel shape, hips and chest lifted high, head hanging down between arms, like halfway through a back flip, side view, full body visible, yoga studio, natural lighting, professional photo"
    },
    "seated-spinal-twist": {
        "filename": "seated-spinal-twist.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing yoga leggings, in seated spinal twist, sitting on mat with right leg extended, left foot crossed over and placed on the outside of right knee, torso twisted to the left, right elbow pressing against outside of left knee, left hand behind for support, full body visible, yoga studio, natural lighting, professional photo"
    },
    "boat-pose": {
        "filename": "boat-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing yoga leggings, in boat pose, sitting on yoga mat on the floor, balanced on sit bones, legs lifted and extended at 45 degrees, arms reaching forward parallel to legs, forming V-shape, torso and legs creating a boat shape, clearly grounded on the mat, full body visible, yoga studio, natural lighting, professional photo"
    },
    "crow-pose": {
        "filename": "crow-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing yoga leggings, in crow pose, hands planted on mat shoulder-width apart, elbows bent, knees pressed firmly into the backs of upper arms, body leaning forward over hands, feet lifted off ground, balanced on hands in arm balance, full body visible, yoga studio, natural lighting, professional photo"
    },
    "camel-pose": {
        "filename": "camel-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing yoga leggings, in deep camel pose, kneeling upright on mat, leaning back in deep backbend, hands reaching back to firmly grip ankles, chest lifted and open, head tilted back, thighs perpendicular to floor, full body visible, yoga studio, natural lighting, professional photo"
    },
    "bow-pose": {
        "filename": "bow-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing yoga leggings, in bow pose, lying on her belly on the mat, hands holding both ankles behind her, chest and thighs lifted up off the mat creating a bow shape with the body, weight balanced on the abdomen, side view, full body visible, yoga studio, natural lighting, professional photo"
    },
    "plow-pose": {
        "filename": "plow-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, in plow pose, lying on her shoulders with legs extended over head, toes touching the floor behind her head, legs straight, hips above shoulders, hands supporting lower back or flat on mat, side view, full body visible, yoga studio, natural lighting, professional photo"
    },
    "bound-angle-pose": {
        "filename": "bound-angle-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing yoga leggings, in bound angle pose, sitting on mat with soles of feet pressed together in front, knees dropped out to sides, hands holding feet, upright posture, one person with two feet only, full body visible, yoga studio, natural lighting, professional photo"
    }
}


class RegenerationProcessor:
    """Handles regeneration of specific poses"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(MODEL)
        self.results = []
        self.start_time = datetime.now()

    def generate_image(self, prompt: str, pose_name: str) -> tuple[bool, bytes]:
        """Generate a single image"""
        try:
            logger.info(f"  → Generating with improved prompt...")
            response = self.model.generate_content(prompt)

            # Extract image
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data is not None:
                        logger.info(f"  ✓ Successfully generated")
                        return True, part.inline_data.data
                    elif part.text is not None:
                        logger.warning(f"  ⚠ Model returned text: {part.text[:100]}")

            logger.error(f"  ✗ No image in response")
            return False, None

        except Exception as e:
            logger.error(f"  ✗ Error: {str(e)}")
            return False, None

    def save_image(self, image_data: bytes, filename: str) -> bool:
        """Save image with backup of original"""
        try:
            output_path = Path(OUTPUT_DIR) / filename

            # Backup original if it exists
            if output_path.exists():
                backup_path = output_path.with_suffix('.backup.png')
                output_path.rename(backup_path)
                logger.info(f"  ℹ Backed up original to {backup_path.name}")

            # Save new image
            with open(output_path, 'wb') as f:
                f.write(image_data)

            logger.info(f"  ✓ Saved successfully")

            # Optional verification (non-fatal)
            try:
                img = Image.open(output_path)
                logger.info(f"  ✓ Verified: {img.size[0]}x{img.size[1]} {img.format}")
            except Exception as ve:
                logger.warning(f"  ⚠ Verification warning: {str(ve)} (file saved anyway)")

            return True

        except Exception as e:
            logger.error(f"  ✗ Save failed: {str(e)}")
            return False

    def regenerate_all(self):
        """Regenerate all poses that need fixes"""
        logger.info("="*80)
        logger.info("Starting Targeted Regeneration")
        logger.info("="*80)
        logger.info(f"Model: {MODEL}")
        logger.info(f"Poses to regenerate: {len(POSES_TO_FIX)}")
        logger.info("")

        successful = 0
        failed = 0

        for idx, (pose_key, pose_data) in enumerate(POSES_TO_FIX.items(), 1):
            pose_name = pose_key.replace("-", " ").title()
            filename = pose_data["filename"]
            prompt = pose_data["prompt"]

            logger.info(f"[{idx}/{len(POSES_TO_FIX)}] {pose_name}")
            logger.info(f"  File: {filename}")

            result = {
                "pose_name": pose_name,
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt
            }

            # Generate
            success, image_data = self.generate_image(prompt, pose_name)

            if success and image_data is not None:
                # Save
                if self.save_image(image_data, filename):
                    successful += 1
                    result["status"] = "success"
                    logger.info(f"  ✓ SUCCESS [{successful}/{len(POSES_TO_FIX)}]")
                else:
                    failed += 1
                    result["status"] = "save_failed"
                    logger.error(f"  ✗ SAVE FAILED")
            else:
                failed += 1
                result["status"] = "generation_failed"
                logger.error(f"  ✗ GENERATION FAILED")

            self.results.append(result)

            # Rate limiting
            if idx < len(POSES_TO_FIX):
                logger.info(f"  ⏳ Waiting 60 seconds...")
                logger.info("")
                time.sleep(60)

        # Summary
        logger.info("="*80)
        logger.info("REGENERATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Total: {len(POSES_TO_FIX)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {(successful/len(POSES_TO_FIX)*100):.1f}%")
        logger.info(f"Time: {datetime.now() - self.start_time}")
        logger.info("="*80)

        # Save log
        self.save_log()

    def save_log(self):
        """Save results to JSON"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "model": MODEL,
            "total": len(POSES_TO_FIX),
            "successful": len([r for r in self.results if r["status"] == "success"]),
            "failed": len([r for r in self.results if r["status"] != "success"]),
            "results": self.results
        }

        with open(LOG_FILE, 'w') as f:
            json.dump(log_data, f, indent=2)

        logger.info(f"Log saved to: {LOG_FILE}")


def main():
    """Main entry point"""
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Confirm with user
    print("\nAbout to regenerate these 10 poses:")
    for i, pose_key in enumerate(POSES_TO_FIX.keys(), 1):
        print(f"  {i}. {pose_key.replace('-', ' ').title()}")

    print(f"\nEstimated time: ~10-12 minutes")
    print(f"Originals will be backed up as *.backup.png")
    print("")

    # Run regeneration
    processor = RegenerationProcessor(API_KEY)
    processor.regenerate_all()


if __name__ == "__main__":
    main()
