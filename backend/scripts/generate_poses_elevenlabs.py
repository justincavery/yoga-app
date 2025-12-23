#!/usr/bin/env python3
"""
Generate TTS audio files for all yoga poses using ElevenLabs.
Uses voice3 (zA6D7RyKdc2EClouEMkP) with optimized ASMR settings.
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
                ORDER BY name_english
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
    print("Yoga Pose Audio Generation - ElevenLabs")
    print(f"Using: {VOICE_NAME} ({VOICE_ID})")
    print("=" * 80)
    print()

    # Fetch all poses
    print("Fetching poses from database...")
    poses = await get_all_poses()
    print(f"✅ Found {len(poses)} poses with instructions")
    print()

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

        # Small delay to avoid rate limiting
        if i < len(poses):
            await asyncio.sleep(0.3)

    print()
    print("=" * 80)
    print(f"✅ Audio generation complete!")
    print(f"   Generated: {total_generated}/{len(poses)} files")
    print(f"   Location: {OUTPUT_DIR}")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
