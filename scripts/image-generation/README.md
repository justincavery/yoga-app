# Yoga Pose Image Generation

Scripts and guides for generating yoga pose images using AI, both locally and via cloud services.

## Quick Start

### Option 1: Replicate API (Fastest - Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export REPLICATE_API_TOKEN=your_token_here

# Generate images for all poses
python generate_replicate.py --variations 4

# Or generate specific poses
python generate_replicate.py --poses "Downward Dog" "Warrior 2" --variations 2
```

**Cost:** ~$0.005 per image (~$1 for 200 images)

### Option 2: Local Stable Diffusion

```bash
# Install dependencies (including torch, diffusers)
pip install -r requirements.txt
pip install torch diffusers transformers accelerate controlnet-aux

# Generate images
python generate_local.py --variations 4

# Use custom model
python generate_local.py --model path/to/model.safetensors
```

**Requirements:** 16GB+ RAM, GPU recommended (6GB+ VRAM)

## Documentation

- **[Local Generation Guide](../../docs/IMAGE_GENERATION_LOCAL.md)** - Complete setup for Stable Diffusion with ControlNet
- **[Service Guide](../../docs/IMAGE_GENERATION_SERVICES.md)** - Using Replicate, Midjourney, Leonardo.ai, etc.
- **[prompts.json](./prompts.json)** - Pre-configured prompts and templates

## Scripts

### generate_replicate.py
Cloud-based generation using Replicate API. Fast, high-quality, pay-per-use.

**Usage:**
```bash
python generate_replicate.py \
  --output ./generated_poses \
  --variations 4 \
  --character "professional yoga instructor wearing navy blue outfit" \
  --limit 5  # Test with 5 poses first
```

**Arguments:**
- `--output` - Output directory (default: `generated_poses`)
- `--poses` - Specific pose names (default: all from DB)
- `--variations` - Images per pose (default: 4)
- `--character` - Character description for consistency
- `--width` - Image width (default: 768)
- `--height` - Image height (default: 1024)
- `--limit` - Limit number of poses (for testing)

### generate_local.py
Local generation using Stable Diffusion + ControlNet. Full control, one-time setup.

**Usage:**
```bash
python generate_local.py \
  --output ./generated_poses \
  --variations 4 \
  --model runwayml/stable-diffusion-v1-5 \
  --seed 42
```

**Arguments:**
- `--model` - Custom SD model path
- `--output` - Output directory
- `--poses` - Specific pose names
- `--variations` - Images per pose (default: 4)
- `--character` - Character description
- `--seed` - Random seed for reproducibility

## Workflow

### 1. Test Generation (5-10 poses)

```bash
# Test with Replicate (fastest)
python generate_replicate.py --limit 5 --variations 2

# Review output
open generated_poses/
```

### 2. Full Batch Generation

```bash
# Generate all poses from database
python generate_replicate.py --variations 4

# Or locally (slower but free after setup)
python generate_local.py --variations 4
```

### 3. Review and Select

```bash
# Images saved in generated_poses/
# manifest.json contains all generated paths
cat generated_poses/manifest.json
```

### 4. Upload to Cloud Storage

```bash
# Upload to your storage (AWS S3, Cloudflare R2, etc.)
# Example for AWS S3:
aws s3 sync generated_poses/ s3://your-bucket/poses/ --exclude "*.json"
```

### 5. Update Database

```python
# Update poses with new image URLs
import psycopg2
import json

conn = psycopg2.connect("postgresql://yogaflow:password@localhost:5432/yogaflow")
cur = conn.cursor()

# Example: Update single pose
cur.execute(
    "UPDATE poses SET image_urls = %s WHERE name = %s",
    (json.dumps(["https://storage.com/pose-1.jpg", "https://storage.com/pose-2.jpg"]),
     "Downward Dog")
)

conn.commit()
```

## Customization

### Character Consistency

Edit the character description in prompts for consistent appearance:

```python
CHARACTER = "professional yoga instructor, athletic build, long dark hair in ponytail, wearing purple yoga outfit, serene expression"
```

### Environments

Change environment in prompt templates (prompts.json):

- "modern yoga studio, wooden floor, large windows"
- "beach setting, ocean background, golden hour"
- "outdoor deck, trees in background, morning light"
- "minimalist studio, white walls, soft lighting"

### Lighting Styles

- "natural window lighting, soft shadows"
- "golden hour lighting, warm tones"
- "studio lighting, professional, even"
- "soft diffused lighting, gentle"

## Cost Comparison

| Method | Setup Time | Cost (100 images) | Speed | Quality |
|--------|------------|-------------------|-------|---------|
| Replicate API | 5 min | $0.50 | Fast (5-10s/img) | High |
| Midjourney | 10 min | $10/mo | Medium (30s/img) | Highest |
| Local SD | 30-60 min | Free* | Slow (CPU: 3min, GPU: 10s) | High |
| RunPod | 15 min | $0.34 | Fast (GPU: 10s) | High |

*After initial setup ($0 if you have GPU, otherwise electricity costs)

## Tips

1. **Start small**: Test with 5-10 poses before full batch
2. **Use consistent character**: Same description across all prompts
3. **Generate variations**: 4+ per pose, pick the best
4. **Save good seeds**: Note seeds of best results for similar output
5. **Batch processing**: Generate overnight for large collections

## Troubleshooting

### Replicate API Errors

```bash
# Check API token
echo $REPLICATE_API_TOKEN

# Test connection
python -c "import replicate; print(replicate.models.list())"
```

### Local Generation OOM

```bash
# Reduce image size
python generate_local.py --width 512 --height 512

# Or use CPU only (slower but works with less RAM)
python generate_local.py  # Automatically detects and uses CPU if no GPU
```

### Database Connection

```bash
# Start database
cd ../../backend
docker-compose up -d db

# Test connection
psql postgresql://yogaflow:password@localhost:5432/yogaflow -c "SELECT COUNT(*) FROM poses;"
```

## Next Steps

1. Review generated images
2. Select best variations for each pose
3. Upload to cloud storage
4. Update database with URLs
5. Test in app
6. Iterate on prompts/style as needed

## Resources

- [Replicate API Docs](https://replicate.com/docs)
- [Stable Diffusion Guide](https://stable-diffusion-art.com/)
- [ControlNet Paper](https://arxiv.org/abs/2302.05543)
- [Prompt Engineering Guide](https://prompthero.com/)
