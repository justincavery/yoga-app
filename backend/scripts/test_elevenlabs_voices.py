#!/usr/bin/env python3
"""
Test ElevenLabs voices for yoga pose narration.
Generates audio for Downward Facing Dog with 6 different voices.
"""
import asyncio
import sys
from pathlib import Path
import httpx

# ElevenLabs API configuration
ELEVENLABS_API_KEY = "sk_7be646e20c0fc881d2a66fdcf8340c67002c15e3122654b4"
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"

# Voice IDs to test
VOICES = {
    "voice1": "1cxc5c3E9K6F1wlqOJGV",
    "voice2": "mZ3kbJNnKRWI4YzJXA9j",
    "voice3": "zA6D7RyKdc2EClouEMkP",
    "voice4": "nBoLwpO4PAjQaQwVKPI1",
    "voice5": "56bWURjYFHyYyVf490Dp",
    "voice6": "fgDJOgmENIR82PueQrVs",
}

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / "content" / "audio" / "voice_tests"


def get_test_pose():
    """Get Downward Facing Dog pose (hardcoded for testing)."""
    return {
        "name_english": "Downward Facing Dog",
        "name_sanskrit": "Adho Mukha Svanasana",
        "entry_instructions": [
            "Begin on your hands and knees in a tabletop position",
            "Spread your fingers wide and press firmly through your palms",
            "Tuck your toes under and lift your hips up and back",
            "Straighten your legs as much as comfortable, bringing your heels toward the floor",
            "Let your head hang naturally between your arms"
        ],
        "holding_cues": "Press your chest gently toward your thighs. Keep your shoulders away from your ears. Engage your quadriceps to help lengthen your hamstrings.",
        "breathing_pattern": "Breathe deeply and evenly through your nose. With each exhale, allow your heels to sink a little closer to the mat.",
        "exit_instructions": [
            "Bend your knees slowly",
            "Lower your hips back down to your heels",
            "Rest in child's pose for a few breaths"
        ],
        "has_side_variation": False
    }


def format_pose_script(pose: dict) -> str:
    """
    Format pose instructions into a natural script for TTS.
    Simple and direct - no special pause markers for ElevenLabs.
    """
    parts = []

    # Introduction
    intro = f"{pose['name_english']}"
    if pose['name_sanskrit']:
        intro += f", or in Sanskrit, {pose['name_sanskrit']}"
    intro += "."
    parts.append(intro)

    # Entry instructions
    if pose['entry_instructions']:
        parts.append("To enter this pose.")
        for instruction in pose['entry_instructions']:
            parts.append(instruction)

    # Holding cues
    if pose['holding_cues']:
        parts.append("As you hold the pose.")
        parts.append(pose['holding_cues'])

    # Breathing
    if pose['breathing_pattern']:
        parts.append(pose['breathing_pattern'])

    # Exit instructions
    if pose['exit_instructions']:
        parts.append("To release.")
        for instruction in pose['exit_instructions']:
            parts.append(instruction)

    # Side variation note
    if pose['has_side_variation']:
        parts.append("Remember to practice this pose on both sides.")

    # Join all parts with natural pauses
    script = " ".join(parts)
    return script


async def generate_audio_elevenlabs(text: str, voice_id: str, output_path: Path):
    """Generate audio using ElevenLabs API."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
        )
        response.raise_for_status()

        # Save the audio file
        output_path.write_bytes(response.content)


async def main():
    """Main execution."""
    print("=" * 80)
    print("ElevenLabs Voice Testing - Downward Facing Dog")
    print("=" * 80)
    print()

    # Get test pose
    print("Loading pose instructions...")
    pose = get_test_pose()

    print(f"✅ Pose: {pose['name_english']}")
    if pose['name_sanskrit']:
        print(f"   Sanskrit: {pose['name_sanskrit']}")
    print()

    # Format script
    script = format_pose_script(pose)
    print("Script to narrate:")
    print("-" * 80)
    print(script)
    print("-" * 80)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate audio with each voice
    print(f"Generating audio with {len(VOICES)} voices...")
    print()

    total_generated = 0
    for i, (voice_name, voice_id) in enumerate(VOICES.items(), 1):
        output_path = OUTPUT_DIR / f"downward-dog-{voice_name}.mp3"
        print(f"[{i}/{len(VOICES)}] Generating with {voice_name}...")
        print(f"  Voice ID: {voice_id}")

        try:
            await generate_audio_elevenlabs(script, voice_id, output_path)
            total_generated += 1
            print(f"  ✅ Saved: {output_path.name}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

        # Small delay between requests
        if i < len(VOICES):
            await asyncio.sleep(0.5)

        print()

    print("=" * 80)
    print(f"✅ Generated {total_generated}/{len(VOICES)} test audio files!")
    print(f"   Location: {OUTPUT_DIR}")
    print()
    print("🎧 Listen to each file and pick your favorite voice!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
