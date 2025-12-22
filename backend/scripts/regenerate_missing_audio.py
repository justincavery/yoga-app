#!/usr/bin/env python3
"""
Regenerate the 7 missing audio files that failed due to API rate limiting.
"""
import asyncio
import sys
import os
from pathlib import Path
import httpx

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set database URL environment variable
os.environ["DATABASE_URL"] = "postgresql+asyncpg://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev"

from sqlalchemy import text
from app.core.database import AsyncSessionLocal

# ElevenLabs API configuration
ELEVENLABS_API_KEY = "sk_7be646e20c0fc881d2a66fdcf8340c67002c15e3122654b4"
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"

# Voice to use (voice3)
VOICE_ID = "zA6D7RyKdc2EClouEMkP"
VOICE_NAME = "voice3"

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / "content" / "audio" / "poses"

# Missing pose names
MISSING_POSES = [
    "Twisted Flying Crow",
    "Upward Plank Pose",
    "Warrior I",
    "Warrior II",
    "Warrior III",
    "Wide-Legged Forward Bend",
    "Yogic Sleep Pose"
]


async def get_pose_by_name(name: str):
    """Fetch pose with instructions from database by name."""
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
                WHERE name_english = :name
                  AND entry_instructions IS NOT NULL
            """),
            {"name": name}
        )
        row = result.first()
        if row:
            return {
                "id": row[0],
                "name_english": row[1],
                "name_sanskrit": row[2],
                "entry_instructions": row[3],
                "exit_instructions": row[4],
                "holding_cues": row[5],
                "breathing_pattern": row[6],
                "has_side_variation": row[7]
            }
        return None


def format_pose_script(pose: dict) -> str:
    """
    Format pose instructions into a natural script for TTS.
    Uses commas and periods for natural pacing with line breaks for pauses.
    """
    parts = []

    # Introduction
    intro = f"{pose['name_english']}"
    if pose['name_sanskrit']:
        intro += f", or in Sanskrit, {pose['name_sanskrit']}"
    intro += "."
    parts.append(intro)
    parts.append("\n\n")  # Pause after intro

    # Entry instructions
    if pose['entry_instructions']:
        parts.append("To enter this pose.")
        parts.append("\n\n")
        for instruction in pose['entry_instructions']:
            parts.append(instruction)
            parts.append("\n\n")  # Pause between steps

    # Holding cues
    if pose['holding_cues']:
        parts.append("As you hold the pose.")
        parts.append("\n\n")
        parts.append(pose['holding_cues'])
        parts.append("\n\n")

    # Breathing
    if pose['breathing_pattern']:
        parts.append(pose['breathing_pattern'])
        parts.append("\n\n")

    # Exit instructions
    if pose['exit_instructions']:
        parts.append("To release.")
        parts.append("\n\n")
        for instruction in pose['exit_instructions']:
            parts.append(instruction)
            parts.append("\n\n")

    # Side variation note
    if pose['has_side_variation']:
        parts.append("Remember to practice this pose on both sides.")

    # Join all parts
    script = "".join(parts)
    return script


async def generate_audio_elevenlabs(text: str, output_path: Path):
    """Generate audio using ElevenLabs API with optimized settings."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{ELEVENLABS_API_BASE}/text-to-speech/{VOICE_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.55,
                    "similarity_boost": 0.80,
                    "style": 0.2,
                    "use_speaker_boost": True
                }
            }
        )
        response.raise_for_status()

        # Save the audio file
        output_path.write_bytes(response.content)


async def process_pose(pose: dict):
    """Generate audio file for a single pose."""
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Format script
    script = format_pose_script(pose)

    # Generate filename
    filename = pose['name_english'].lower().replace(' ', '-').replace("'", '')
    output_path = OUTPUT_DIR / f"{filename}.mp3"

    print(f"  Generating: {filename}.mp3")

    try:
        await generate_audio_elevenlabs(script, output_path)
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


async def main():
    """Main execution."""
    print("=" * 80)
    print("Regenerating Missing Yoga Pose Audio Files")
    print(f"Using: {VOICE_NAME} ({VOICE_ID})")
    print("=" * 80)
    print()

    # Fetch missing poses
    print("Fetching missing poses from database...")
    poses = []
    for name in MISSING_POSES:
        pose = await get_pose_by_name(name)
        if pose:
            poses.append(pose)
        else:
            print(f"⚠️  Could not find pose: {name}")

    print(f"✅ Found {len(poses)}/{len(MISSING_POSES)} poses")
    print()

    if not poses:
        print("❌ No poses to generate")
        return False

    # Generate audio for each pose
    print(f"Generating audio files...")
    print(f"Settings: Stability 0.55 | Similarity 0.80 | Style 0.2")
    print()

    total_generated = 0
    for i, pose in enumerate(poses, 1):
        print(f"[{i}/{len(poses)}] {pose['name_english']}")
        success = await process_pose(pose)
        if success:
            total_generated += 1

        # Delay to avoid rate limiting
        if i < len(poses):
            await asyncio.sleep(2.0)  # Longer delay to avoid rate limiting

    print()
    print("=" * 80)
    print(f"✅ Regeneration complete!")
    print(f"   Generated: {total_generated}/{len(poses)} files")
    print(f"   Location: {OUTPUT_DIR}")
    print("=" * 80)

    return total_generated == len(poses)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
