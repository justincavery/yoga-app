#!/usr/bin/env python3
"""
Test ElevenLabs voices with a meditation script.
Generates audio for the same meditation with voice2 and voice3.
"""
import asyncio
from pathlib import Path
import httpx

# ElevenLabs API configuration
ELEVENLABS_API_KEY = "sk_7be646e20c0fc881d2a66fdcf8340c67002c15e3122654b4"
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"

# Voices to test
VOICES = {
    "voice2": "mZ3kbJNnKRWI4YzJXA9j",
    "voice3": "zA6D7RyKdc2EClouEMkP",
}

# Script and output paths
SCRIPT_PATH = Path(__file__).parent / "meditation_script.txt"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "content" / "audio" / "voice_tests"


async def generate_audio_elevenlabs(text: str, voice_id: str, output_path: Path):
    """Generate audio using ElevenLabs API with ASMR-optimized settings."""
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",  # Original model for natural quality
                "voice_settings": {
                    "stability": 0.55,  # Balanced - smooth but with some variation
                    "similarity_boost": 0.80,  # High similarity for consistent voice
                    "style": 0.2,  # Subtle style for gentle warmth
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
    print("ElevenLabs Voice Testing - 5 Minute Meditation")
    print("=" * 80)
    print()

    # Read meditation script
    print("Loading meditation script...")
    if not SCRIPT_PATH.exists():
        print(f"❌ Could not find meditation script at {SCRIPT_PATH}")
        return False

    meditation_text = SCRIPT_PATH.read_text()
    word_count = len(meditation_text.split())
    print(f"✅ Script loaded: {word_count} words")
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate audio with each voice
    print(f"Generating meditation audio with {len(VOICES)} voices...")
    print("(This will take a minute or two - longer scripts take more time)")
    print()

    total_generated = 0
    for i, (voice_name, voice_id) in enumerate(VOICES.items(), 1):
        output_path = OUTPUT_DIR / f"meditation-{voice_name}.mp3"
        print(f"[{i}/{len(VOICES)}] Generating with {voice_name}...")
        print(f"  Voice ID: {voice_id}")

        try:
            await generate_audio_elevenlabs(meditation_text, voice_id, output_path)
            total_generated += 1
            print(f"  ✅ Saved: {output_path.name}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

        # Small delay between requests
        if i < len(VOICES):
            await asyncio.sleep(0.5)

        print()

    print("=" * 80)
    print(f"✅ Generated {total_generated}/{len(VOICES)} meditation audio files!")
    print(f"   Location: {OUTPUT_DIR}")
    print()
    print("🎧 Listen to each meditation and notice:")
    print("   - Natural pacing and pauses")
    print("   - Voice warmth and soothing quality")
    print("   - Which one gives you tingles!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    import sys
    sys.exit(0 if success else 1)
