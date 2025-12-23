#!/usr/bin/env python3
"""
PRO model regeneration with improved prompts from Iyengar/Vinyasa sources
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
MODEL = "gemini-3-pro-image-preview"  # Using PRO model
LOG_FILE = "regeneration_pro_log.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("regeneration_pro_detailed.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Improved prompts based on Iyengar/Vinyasa sources
POSES_TO_FIX = {
    "chaturanga": {
        "filename": "chaturanga.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, in Chaturanga Dandasana four-limbed staff pose, body lowered parallel to floor, shoulders shifted forward in front of wrists, elbows bent at 90 degrees pointing straight back along ribcage, arms hugging sides of body, body forming straight plank from head to heels hovering just above mat, core engaged, side view, full body visible, yoga studio, natural lighting, professional photo"
    },
    "bridge-pose": {
        "filename": "bridge-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, in Setu Bandha Sarvangasana bridge pose, lying on back on mat with shoulders and head on floor, feet hip-width apart parallel and flat on mat, knees bent directly over ankles, hips lifted high creating smooth diagonal line from shoulders through hips to knees, inner thighs rolling inward, chest lifting toward chin, shoulders rolled under, arms pressing into mat parallel alongside body, side view showing bridge arch clearly, full body visible, yoga studio, natural lighting, professional photo"
    },
    "wheel-pose": {
        "filename": "wheel-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, in Urdhva Dhanurasana full wheel pose, hands and feet planted firmly on mat, body arched in deep backbend forming upward bow shape, elbows over wrists, feet parallel with knees over ankles, hips and chest lifted high creating smooth spinal curve, head hanging naturally between arms, shoulder blades drawn onto back, side view, full body visible, yoga studio, natural lighting, professional photo"
    },
    "boat-pose": {
        "filename": "boat-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, in Navasana full boat pose, sitting on yoga mat balanced on tripod of sitting bones and tailbone, torso lifted with flat back at 45 degrees, legs lifted and extended creating V-shape with torso, arms reaching forward parallel to floor alongside legs, chest lifted with shoulders back, spine straight not rounded, clearly grounded on mat, full body visible, yoga studio, natural lighting, professional photo"
    },
    "crow-pose": {
        "filename": "crow-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, in Bakasana crow pose arm balance, hands planted shoulder-width apart on mat, elbows bent with upper arms creating shelf, shins or knees pressing firmly into backs of upper arms, body weight shifted forward over hands, hips lifted high, feet lifted completely off ground, core engaged, balanced on hands, front three-quarter view, full body visible, yoga studio, natural lighting, professional photo"
    },
    "bound-angle-pose": {
        "filename": "bound-angle-pose.jpg",
        "prompt": "blonde yoga instructor, 25-30 years old, wearing grey yoga leggings, in Baddha Konasana bound angle pose, sitting upright on mat, soles of both feet pressed together in front of pelvis, knees dropped out to sides resting naturally, hands gently holding feet, spine lifted and straight, pelvis neutral, sitting evenly on sit bones, shoulders relaxed, one person with only two feet visible, full body visible, yoga studio, natural lighting, professional photo"
    }
}


class ProRegenerationProcessor:
    """Handles PRO model regeneration"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(MODEL)
        self.results = []
        self.start_time = datetime.now()

    def generate_image(self, prompt: str, pose_name: str) -> tuple[bool, bytes]:
        """Generate a single image"""
        try:
            logger.info(f"  → Generating with PRO model...")
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
                backup_path = output_path.with_suffix('.pro-backup.jpg')
                import shutil
                shutil.copy2(output_path, backup_path)
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
        logger.info("Starting PRO Model Regeneration")
        logger.info("="*80)
        logger.info(f"Model: {MODEL}")
        logger.info(f"Poses to regenerate: {len(POSES_TO_FIX)}")
        logger.info(f"Using improved prompts from Iyengar/Vinyasa sources")
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

            if success and image_data is not None and len(image_data) > 0:
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

    # Info
    print("\nPRO Model Regeneration with Improved Prompts")
    print("=" * 50)
    print("\nPoses to regenerate:")
    for i, pose_key in enumerate(POSES_TO_FIX.keys(), 1):
        print(f"  {i}. {pose_key.replace('-', ' ').title()}")

    print(f"\nModel: {MODEL}")
    print(f"Estimated time: ~6-7 minutes")
    print(f"Originals backed up as *.pro-backup.jpg")
    print(f"Prompts based on Iyengar/Vinyasa sources")
    print("")

    # Run regeneration
    processor = ProRegenerationProcessor(API_KEY)
    processor.regenerate_all()


if __name__ == "__main__":
    main()
