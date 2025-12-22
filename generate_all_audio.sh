#!/bin/bash
# Generate all TTS audio files for poses and sequences
# Uses Replicate (Cloudflare) with MiniMax Speech-02-HD

set -e

echo "========================================================================"
echo "YogaFlow Audio Generation (Replicate/Cloudflare)"
echo "========================================================================"
echo ""

# Ensure we're using PostgreSQL
export DATABASE_URL="postgresql+asyncpg://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev"

# Set Replicate API token (set this environment variable before running)
# export REPLICATE_API_TOKEN="your_token_here"

# Activate virtual environment
source venv/bin/activate

echo "🎤 Generating pose audio files..."
echo "   (80 poses × 2 voices = 160 files)"
echo ""
cd backend/scripts
python generate_pose_audio.py

echo ""
echo "🎤 Generating sequence audio files..."
echo "   (15 sequences × 2 voices = 30 files)"
echo ""
python generate_sequence_audio.py

echo ""
echo "========================================================================"
echo "✅ Audio generation complete!"
echo "========================================================================"
echo ""
echo "📂 Audio files location:"
echo "   Poses:     content/audio/poses/"
echo "   Sequences: content/audio/sequences/"
echo ""
echo "🎧 Voice types generated:"
echo "   - Calm Woman (soothing, peaceful)"
echo "   - Wise Woman (warm, experienced)"
echo ""
echo "🎛️  Audio settings:"
echo "   - Speed: 0.8x (slower for ASMR)"
echo "   - Pitch: -2 semitones (lower for calmness)"
echo "   - Emotion: calm"
echo ""
