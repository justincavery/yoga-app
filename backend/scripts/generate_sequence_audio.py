#!/usr/bin/env python3
"""
Generate TTS audio files for yoga sequences.
Creates guided sequence walkthroughs with timing cues.
Uses Replicate (Cloudflare) with MiniMax Speech-02-HD.

Voices:
- Calm Woman: calm_woman (soothing, peaceful)
- Wise Woman: wise_woman (warm, experienced)
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
MODEL_VERSION = "fdd081f807e655246ef42adbcb3ee9334e7fdc710428684771f90d69992cabb3"

# Voice configuration
VOICES = {
    "calm": "Calm_Woman",
    "wise": "Wise_Woman",
}

# Audio settings for ASMR-style delivery
SPEED = 0.8
PITCH = -2
EMOTION = "calm"

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / "content" / "audio" / "sequences"


async def get_sequence_with_poses(sequence_id: int):
    """Fetch a sequence with all its poses in order."""
    async with AsyncSessionLocal() as session:
        # Get sequence details
        seq_result = await session.execute(
            text("""
                SELECT
                    sequence_id,
                    name,
                    description,
                    difficulty_level,
                    duration_minutes,
                    focus_area
                FROM sequences
                WHERE sequence_id = :seq_id
            """),
            {"seq_id": sequence_id}
        )
        seq_row = seq_result.first()
        if not seq_row:
            return None

        sequence = {
            "id": seq_row[0],
            "name": seq_row[1],
            "description": seq_row[2],
            "difficulty_level": seq_row[3],
            "duration_minutes": seq_row[4],
            "focus_area": seq_row[5],
            "poses": []
        }

        # Get poses in sequence
        poses_result = await session.execute(
            text("""
                SELECT
                    p.name_english,
                    p.name_sanskrit,
                    sp.duration_seconds,
                    sp.position_order
                FROM sequence_poses sp
                JOIN poses p ON sp.pose_id = p.pose_id
                WHERE sp.sequence_id = :seq_id
                ORDER BY sp.position_order
            """),
            {"seq_id": sequence_id}
        )

        for row in poses_result:
            sequence["poses"].append({
                "name_english": row[0],
                "name_sanskrit": row[1],
                "duration": row[2],
                "order": row[3]
            })

        return sequence


def format_sequence_intro(sequence: dict) -> str:
    """Format the sequence introduction."""
    parts = []

    # Welcome
    parts.append(f"Welcome to {sequence['name']}.")
    parts.append("<#1.5#>")

    # Description
    if sequence['description']:
        parts.append(sequence['description'])
        parts.append("<#1.5#>")

    # Duration and level
    parts.append(f"This {sequence['difficulty_level']} level sequence will take approximately {sequence['duration_minutes']} minutes.")
    parts.append("<#1.2#>")

    # Focus
    parts.append(f"We'll be focusing on {sequence['focus_area'].lower()}.")
    parts.append("<#1.5#>")

    # Preparation
    parts.append("Find a comfortable space, grab your mat, and let's begin.")
    parts.append("<#1.0#>")
    parts.append("Take a moment to center yourself.")
    parts.append("<#2.0#>")
    parts.append("When you're ready, we'll move into our first pose.")
    parts.append("<#1.0#>")

    return " ".join(parts)


def format_pose_transition(pose: dict, pose_number: int, total_poses: int) -> str:
    """Format a transition to a pose with timing."""
    parts = []

    # Pose announcement
    if pose_number == 1:
        parts.append(f"Let's begin with {pose['name_english']}")
    else:
        parts.append(f"Next, we'll move into {pose['name_english']}")

    # Sanskrit name if available
    if pose['name_sanskrit']:
        parts.append(f", or {pose['name_sanskrit']}")

    parts.append(".")
    parts.append("<#1.0#>")

    # Duration cue
    minutes = pose['duration'] // 60
    seconds = pose['duration'] % 60

    if minutes > 0 and seconds > 0:
        duration_text = f"{minutes} minute{'s' if minutes > 1 else ''} and {seconds} seconds"
    elif minutes > 0:
        duration_text = f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        duration_text = f"{seconds} seconds"

    parts.append(f"Hold this pose for {duration_text}.")
    parts.append("<#0.8#>")

    # Breathing reminder
    parts.append("Remember to breathe deeply and naturally.")
    parts.append("<#1.5#>")

    return " ".join(parts)


def format_sequence_outro() -> str:
    """Format the sequence closing."""
    parts = []

    parts.append("Well done.")
    parts.append("<#1.5#>")
    parts.append("You've completed this sequence.")
    parts.append("<#1.5#>")
    parts.append("Take a moment to notice how you feel.")
    parts.append("<#2.0#>")
    parts.append("Rest in stillness for as long as you like.")
    parts.append("<#1.5#>")
    parts.append("Namaste.")

    return " ".join(parts)


def format_sequence_script(sequence: dict) -> str:
    """Format the complete sequence script."""
    parts = []

    # Introduction
    parts.append(format_sequence_intro(sequence))

    # Each pose
    for i, pose in enumerate(sequence['poses'], 1):
        parts.append(format_pose_transition(pose, i, len(sequence['poses'])))

    # Closing
    parts.append(format_sequence_outro())

    return " ".join(parts)


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


async def process_sequence(sequence: dict, voice_type: str):
    """Generate audio for a sequence."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Format script
    script = format_sequence_script(sequence)

    # Generate filename
    filename = sequence['name'].lower().replace(' ', '-').replace("'", '')
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
    print("Yoga Sequence Audio Generation (Replicate/Cloudflare)")
    print("=" * 80)
    print()

    # Get all sequence IDs
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT sequence_id, name FROM sequences ORDER BY sequence_id")
        )
        sequence_ids = [(row[0], row[1]) for row in result]

    print(f"Found {len(sequence_ids)} sequences")
    print()

    total_generated = 0
    for voice_type in ["calm", "wise"]:
        print(f"\n📢 Generating audio with {voice_type.title()} Woman voice...")
        print(f"   Voice: {VOICES[voice_type]}")
        print(f"   Speed: {SPEED}x | Pitch: {PITCH} semitones | Emotion: {EMOTION}")
        print()

        for i, (seq_id, seq_name) in enumerate(sequence_ids, 1):
            print(f"[{i}/{len(sequence_ids)}] {seq_name}")

            # Get full sequence data
            sequence = await get_sequence_with_poses(seq_id)
            if sequence:
                success = await process_sequence(sequence, voice_type)
                if success:
                    total_generated += 1

            # Small delay
            if i < len(sequence_ids):
                await asyncio.sleep(0.5)

    print()
    print("=" * 80)
    print(f"✅ Sequence audio generation complete!")
    print(f"   Generated: {total_generated} files")
    print(f"   Location: {OUTPUT_DIR}")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
