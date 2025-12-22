#!/usr/bin/env python3
"""
Generate test audio with different voices for a single pose.
Creates 20 variations so user can pick their favorite.
"""
import asyncio
import sys
import os
from pathlib import Path
import httpx

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal

# Replicate API configuration
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
REPLICATE_API_BASE = "https://api.replicate.com/v1"

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / "content" / "audio" / "voice_tests"


# Natural script variations - less formulaic
INTRO_VARIATIONS = [
    "{pose_name}. {first_instruction}",
    "Let's move into {pose_name}. {first_instruction}",
    "{pose_name}, or {sanskrit}. {first_instruction}",
    "Now, {pose_name}. {first_instruction}",
    "{pose_name}. Start by {first_instruction}",
]


def format_natural_script(pose: dict) -> str:
    """
    Format pose instructions naturally - quick transition to instructions.
    No repetitive patterns, flows naturally.
    """
    parts = []

    # Quick intro - pick a natural variation
    first_inst = pose['entry_instructions'][0] if pose['entry_instructions'] else "finding your position"

    # Simple, direct introduction
    if pose['name_sanskrit']:
        intro = f"{pose['name_english']}, {pose['name_sanskrit']}."
    else:
        intro = f"{pose['name_english']}."

    parts.append(intro)
    parts.append("<#0.5#>")  # Brief pause

    # Jump right into instructions - skip "To enter this pose"
    if pose['entry_instructions']:
        for i, instruction in enumerate(pose['entry_instructions']):
            parts.append(instruction)
            # Vary pause lengths for naturalness
            if i < len(pose['entry_instructions']) - 1:
                parts.append("<#0.8#>")
            else:
                parts.append("<#1.0#>")

    # Holding cues - natural transition
    if pose['holding_cues']:
        parts.append(pose['holding_cues'])
        parts.append("<#0.8#>")

    # Breathing - brief mention
    if pose['breathing_pattern']:
        parts.append(pose['breathing_pattern'])
        parts.append("<#0.8#>")

    # Exit - simple and direct
    if pose['exit_instructions']:
        for instruction in pose['exit_instructions']:
            parts.append(instruction)
            parts.append("<#0.8#>")

    # Side variation - only if needed
    if pose['has_side_variation']:
        parts.append("Practice on both sides.")

    return " ".join(parts)


async def get_test_pose():
    """Get Downward Facing Dog as our test pose - it's well-known and has good instructions."""
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
                WHERE name_english = 'Downward Facing Dog'
                LIMIT 1
            """)
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


# Voice sample URLs - we'll need to find or create these
# For now, this is a placeholder showing the approach
VOICE_PROFILES = [
    {"name": "aussie_sunshine_coast_1", "description": "Sunshine Coast Australian female", "sample_url": None},
    {"name": "aussie_sunshine_coast_2", "description": "Sunshine Coast Australian female (variant)", "sample_url": None},
    {"name": "aussie_perth_1", "description": "Perth Australian female", "sample_url": None},
    {"name": "aussie_perth_2", "description": "Perth Australian female (variant)", "sample_url": None},
    {"name": "aussie_melbourne", "description": "Melbourne Australian female", "sample_url": None},
    {"name": "aussie_sydney", "description": "Sydney Australian female", "sample_url": None},
    {"name": "french_english_1", "description": "South of France light accent (English)", "sample_url": None},
    {"name": "french_english_2", "description": "South of France light accent (English, variant)", "sample_url": None},
    {"name": "california_1", "description": "California female", "sample_url": None},
    {"name": "california_2", "description": "California female (variant)", "sample_url": None},
    {"name": "california_marin", "description": "Marin County California", "sample_url": None},
    {"name": "california_la", "description": "Los Angeles California", "sample_url": None},
    # Additional natural, soothing voices
    {"name": "pacific_northwest", "description": "Pacific Northwest (Seattle/Portland)", "sample_url": None},
    {"name": "british_soft", "description": "Soft British English", "sample_url": None},
    {"name": "kiwi_auckland", "description": "Auckland New Zealand", "sample_url": None},
    {"name": "canadian_west", "description": "Western Canadian", "sample_url": None},
    {"name": "irish_soft", "description": "Soft Irish accent", "sample_url": None},
    {"name": "scandinavian_english", "description": "Scandinavian speaking English", "sample_url": None},
    {"name": "aussie_gold_coast", "description": "Gold Coast Australian", "sample_url": None},
    {"name": "california_bay_area", "description": "Bay Area California", "sample_url": None},
]


async def main():
    """Main execution."""
    print("=" * 80)
    print("Voice Testing - Find Your Perfect Yoga Voice")
    print("=" * 80)
    print()
    print("⚠️  SETUP REQUIRED:")
    print()
    print("This script uses XTTS-V2 for voice cloning, which requires:")
    print("  • 6-second audio samples for each voice")
    print("  • Samples in wav, mp3, m4a, ogg, or flv format")
    print()
    print("OPTIONS:")
    print("  1. Provide your own voice samples (recommended)")
    print("  2. Use free voice datasets (Speech Accent Archive, VCTK)")
    print("  3. Switch to ElevenLabs API (has pre-made yoga instructor voices)")
    print()
    print("NEXT STEPS:")
    print("  • Collect 20 voice samples with desired accents")
    print("  • Place them in: content/voice_samples/")
    print("  • Update VOICE_PROFILES with file paths")
    print()
    print("=" * 80)

    # Get test pose
    print("\nFetching test pose...")
    pose = await get_test_pose()
    if not pose:
        print("❌ Could not find Downward Facing Dog pose")
        return False

    print(f"✅ Using pose: {pose['name_english']}")
    print()

    # Format script
    script = format_natural_script(pose)
    print("Script preview:")
    print("-" * 80)
    print(script[:200] + "...")
    print("-" * 80)
    print()

    print("📋 Voice profiles configured: 20")
    print()
    print("Would you like to:")
    print("  A) Provide voice sample URLs/files")
    print("  B) Use a different TTS service (e.g., ElevenLabs)")
    print("  C) Search for free voice samples online")
    print()

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
