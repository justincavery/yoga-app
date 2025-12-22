#!/usr/bin/env python3
"""
Generate TTS audio files for yoga pose instructions.
Uses Replicate (Cloudflare) with MiniMax Speech-02-HD for high-quality, natural-sounding voices.

Voices:
- Calm Woman: calm_woman (soothing, peaceful)
- Wise Woman: wise_woman (warm, experienced)
"""
import asyncio
import sys
import os
from pathlib import Path
import time
import httpx

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal

# Replicate API configuration
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
REPLICATE_API_BASE = "https://api.replicate.com/v1"
MODEL_VERSION = "fdd081f807e655246ef42adbcb3ee9334e7fdc710428684771f90d69992cabb3"

# Voice configuration - using MiniMax Speech-02-HD voices
VOICES = {
    "calm": "Calm_Woman",      # Calm, soothing female voice
    "wise": "Wise_Woman",      # Warm, experienced female voice
}

# Audio settings for ASMR-style delivery
SPEED = 0.8        # Slower speech (0.8x speed) for relaxation
PITCH = -2         # Slightly lower pitch (-2 semitones) for calmness
EMOTION = "calm"   # Calm emotional tone

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / "content" / "audio" / "poses"


async def get_all_poses():
    """Fetch all poses with instructions from database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    pose_id,
                    name_english,
                    name_sanskrit,
                    entry_instructions,
                    exit_instructions,
                    holding_cues,
                    breathing_pattern,
                    has_side_variation
                FROM poses
                WHERE entry_instructions IS NOT NULL
                ORDER BY pose_id
            """)
        )
        poses = []
        for row in result:
            poses.append({
                "id": row[0],
                "name_english": row[1],
                "name_sanskrit": row[2],
                "entry_instructions": row[3],
                "exit_instructions": row[4],
                "holding_cues": row[5],
                "breathing_pattern": row[6],
                "has_side_variation": row[7]
            })
        return poses


def format_pose_script(pose: dict, voice_type: str = "calm") -> str:
    """
    Format pose instructions into a natural, ASMR-style script.
    Uses Replicate's pause markers: <#seconds#>

    Structure:
    1. Gentle introduction with Sanskrit name
    2. Step-by-step entry instructions
    3. Holding cues with breathing
    4. Exit instructions
    """
    script_parts = []

    # Introduction
    intro = f"{pose['name_english']}"
    if pose['name_sanskrit']:
        intro += f", or in Sanskrit, {pose['name_sanskrit']}"
    intro += "."
    script_parts.append(intro)
    script_parts.append("<#1.5#>")  # 1.5 second pause

    # Entry instructions
    if pose['entry_instructions']:
        script_parts.append("To enter this pose.")
        script_parts.append("<#0.8#>")
        for instruction in pose['entry_instructions']:
            script_parts.append(instruction)
            script_parts.append("<#1.2#>")  # Pause between steps for ASMR effect

    # Holding cues
    if pose['holding_cues']:
        script_parts.append("As you hold the pose.")
        script_parts.append("<#0.8#>")
        script_parts.append(pose['holding_cues'])
        script_parts.append("<#1.0#>")

    # Breathing
    if pose['breathing_pattern']:
        script_parts.append(pose['breathing_pattern'])
        script_parts.append("<#1.0#>")

    # Exit instructions
    if pose['exit_instructions']:
        script_parts.append("To release.")
        script_parts.append("<#0.8#>")
        for instruction in pose['exit_instructions']:
            script_parts.append(instruction)
            script_parts.append("<#1.0#>")

    # Side variation note
    if pose['has_side_variation']:
        script_parts.append("<#0.5#>")
        script_parts.append("Remember to practice this pose on both sides.")

    # Join all parts
    script = " ".join(script_parts)
    return script


async def generate_audio_replicate(text: str, output_path: Path, voice: str):
    """Generate audio using Replicate MiniMax Speech-02-HD via HTTP API."""
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Create prediction
        response = await client.post(
            f"{REPLICATE_API_BASE}/predictions",
            headers={
                "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "version": MODEL_VERSION,
                "input": {
                    "text": text,
                    "voice_id": voice,
                    "emotion": EMOTION,
                    "speed": SPEED,
                    "pitch": PITCH,
                    "volume": 1.0,
                    "audio_format": "mp3",
                    "sample_rate": 32000,
                    "bitrate": 128000,
                    "channel": "mono"
                }
            }
        )
        response.raise_for_status()
        prediction = response.json()
        prediction_id = prediction["id"]

        # Poll for completion
        while True:
            response = await client.get(
                f"{REPLICATE_API_BASE}/predictions/{prediction_id}",
                headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"}
            )
            response.raise_for_status()
            prediction = response.json()

            status = prediction["status"]
            if status == "succeeded":
                break
            elif status == "failed":
                raise Exception(f"Prediction failed: {prediction.get('error')}")
            elif status == "canceled":
                raise Exception("Prediction was canceled")

            # Wait before polling again
            await asyncio.sleep(1.0)

        # Download the audio file
        output_url = prediction["output"]
        response = await client.get(output_url)
        response.raise_for_status()

        output_path.write_bytes(response.content)


async def process_pose(pose: dict, voice_type: str = "calm"):
    """Generate audio files for a single pose."""
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Format script
    script = format_pose_script(pose, voice_type)

    # Generate filename
    filename = pose['name_english'].lower().replace(' ', '-').replace("'", '')
    output_path = OUTPUT_DIR / f"{filename}-{voice_type}.mp3"

    print(f"  Generating: {filename}-{voice_type}.mp3")

    try:
        voice = VOICES[voice_type]
        await generate_audio_replicate(script, output_path, voice)
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


async def main():
    """Main execution."""
    print("=" * 80)
    print("Yoga Pose Audio Generation (Replicate/Cloudflare)")
    print("=" * 80)
    print()

    # Fetch all poses
    print("Fetching poses from database...")
    poses = await get_all_poses()
    print(f"Found {len(poses)} poses with instructions")
    print()

    # Generate audio for each pose in both voices
    total_generated = 0
    for voice_type in ["calm", "wise"]:
        print(f"\n📢 Generating audio with {voice_type.title()} Woman voice...")
        print(f"   Voice: {VOICES[voice_type]}")
        print(f"   Speed: {SPEED}x | Pitch: {PITCH} semitones | Emotion: {EMOTION}")
        print()

        for i, pose in enumerate(poses, 1):
            print(f"[{i}/{len(poses)}] {pose['name_english']}")
            success = await process_pose(pose, voice_type)
            if success:
                total_generated += 1

            # Small delay to avoid rate limiting
            if i < len(poses):
                await asyncio.sleep(0.5)

    print()
    print("=" * 80)
    print(f"✅ Audio generation complete!")
    print(f"   Generated: {total_generated} files")
    print(f"   Location: {OUTPUT_DIR}")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
