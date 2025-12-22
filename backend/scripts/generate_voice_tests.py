#!/usr/bin/env python3
"""
Generate test audio using voice cloning from user's voice sample.
Creates variations using different segments of the source audio.
"""
import asyncio
import sys
import os
from pathlib import Path
import httpx
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal

# Replicate API configuration
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
REPLICATE_API_BASE = "https://api.replicate.com/v1"

# XTTS-V2 model version
XTTS_MODEL_VERSION = "684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e"

# Paths
VOICE_SAMPLE = Path(__file__).parent.parent.parent / "content" / "voice_samples" / "yoga-audio-voice.mp3"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "content" / "audio" / "voice_tests"
SEGMENTS_DIR = OUTPUT_DIR / "segments"


def format_natural_script(pose: dict) -> str:
    """Format pose instructions naturally - quick transition to instructions."""
    parts = []

    # Simple, direct introduction
    if pose['name_sanskrit']:
        intro = f"{pose['name_english']}, {pose['name_sanskrit']}."
    else:
        intro = f"{pose['name_english']}."

    parts.append(intro)

    # Jump right into instructions
    if pose['entry_instructions']:
        for instruction in pose['entry_instructions']:
            parts.append(instruction)

    # Holding cues
    if pose['holding_cues']:
        parts.append(pose['holding_cues'])

    # Breathing
    if pose['breathing_pattern']:
        parts.append(pose['breathing_pattern'])

    # Exit
    if pose['exit_instructions']:
        for instruction in pose['exit_instructions']:
            parts.append(instruction)

    # Side variation
    if pose['has_side_variation']:
        parts.append("Practice on both sides.")

    return " ".join(parts)


async def get_test_pose():
    """Get Downward Facing Dog as our test pose."""
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


def extract_audio_segments(source_file: Path, num_segments: int = 10) -> list:
    """Extract multiple segments from source audio for variation."""
    SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)

    # Get duration
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', str(source_file)],
        capture_output=True,
        text=True
    )

    duration = float(result.stdout.strip())
    print(f"Source audio duration: {duration:.1f} seconds")

    segments = []
    segment_length = 12  # seconds per segment

    # Extract segments evenly distributed throughout the audio
    step = (duration - segment_length) / (num_segments - 1) if num_segments > 1 else 0

    for i in range(num_segments):
        start_time = i * step
        output_file = SEGMENTS_DIR / f"segment_{i+1:02d}.mp3"

        subprocess.run([
            'ffmpeg', '-i', str(source_file),
            '-ss', str(start_time),
            '-t', str(segment_length),
            '-acodec', 'libmp3lame',
            '-y',  # overwrite
            str(output_file)
        ], capture_output=True, check=True)

        segments.append(output_file)
        print(f"  Extracted segment {i+1}/{num_segments} (starting at {start_time:.1f}s)")

    return segments


async def upload_file_to_replicate(file_path: Path) -> str:
    """Upload file to Replicate and return the URL."""
    async with httpx.AsyncClient(timeout=300.0) as client:
        with open(file_path, 'rb') as f:
            files = {'content': (file_path.name, f, 'audio/mpeg')}

            response = await client.post(
                f"{REPLICATE_API_BASE}/files",
                headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"},
                files=files
            )
            response.raise_for_status()
            result = response.json()

            # Return the URL for the uploaded file
            return result['urls']['get']


async def generate_with_xtts(text: str, speaker_url: str, output_path: Path):
    """Generate audio using XTTS-V2 voice cloning."""
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Create prediction
        response = await client.post(
            f"{REPLICATE_API_BASE}/predictions",
            headers={
                "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "version": XTTS_MODEL_VERSION,
                "input": {
                    "text": text,
                    "speaker": speaker_url,
                    "language": "en",
                    "cleanup_voice": True
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
                error_msg = prediction.get('error', 'Unknown error')
                raise Exception(f"Prediction failed: {error_msg}")
            elif status == "canceled":
                raise Exception("Prediction was canceled")

            await asyncio.sleep(1.0)

        # Download the audio file
        output_url = prediction["output"]
        response = await client.get(output_url)
        response.raise_for_status()
        output_path.write_bytes(response.content)


async def main():
    """Main execution."""
    print("=" * 80)
    print("Voice Clone Testing - Downward Facing Dog")
    print("=" * 80)
    print()

    # Check voice sample exists
    if not VOICE_SAMPLE.exists():
        print(f"❌ Voice sample not found: {VOICE_SAMPLE}")
        return False

    print(f"✅ Found voice sample: {VOICE_SAMPLE.name}")
    print()

    # Get test pose
    print("Fetching test pose...")
    pose = await get_test_pose()
    if not pose:
        print("❌ Could not find Downward Facing Dog pose")
        return False

    print(f"✅ Using pose: {pose['name_english']}")
    print()

    # Format script
    script = format_natural_script(pose)
    print("Script to generate:")
    print("-" * 80)
    print(script[:200] + "...")
    print("-" * 80)
    print()

    # Extract segments
    print("Extracting voice segments...")
    segments = extract_audio_segments(VOICE_SAMPLE, num_segments=10)
    print(f"✅ Extracted {len(segments)} segments")
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate audio with each segment
    print("Uploading segments and generating test audio...")
    print("(This will take several minutes - each variation takes ~10-15 seconds)")
    print()

    total_generated = 0
    for i, segment in enumerate(segments, 1):
        output_path = OUTPUT_DIR / f"downward-dog-variation-{i:02d}.mp3"
        print(f"[{i}/{len(segments)}] Processing segment {i}...")

        try:
            # Upload segment to Replicate
            print(f"  Uploading segment...")
            speaker_url = await upload_file_to_replicate(segment)
            print(f"  ✅ Uploaded")

            # Generate audio
            print(f"  Generating audio...")
            await generate_with_xtts(script, speaker_url, output_path)
            total_generated += 1
            print(f"  ✅ Saved: {output_path.name}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

        # Small delay
        if i < len(segments):
            await asyncio.sleep(0.5)

    print()
    print("=" * 80)
    print(f"✅ Generated {total_generated} test audio files!")
    print(f"   Location: {OUTPUT_DIR}")
    print()
    print("NEXT STEP: Listen to the variations and let me know which one(s) you like!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
