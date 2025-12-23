# Service-Based Yoga Pose Image Generation

## Overview
Fast, high-quality yoga pose generation using cloud AI services. Best for one-off batch generation or ongoing needs without local setup.

## Recommended Services

### 1. Replicate (API-Based) - RECOMMENDED for Batch

**Pros:**
- Pay-per-use ($0.0023-0.015 per image)
- Programmatic access
- ControlNet support
- Fast generation (5-10 seconds)

**Setup:**

```bash
pip install replicate
```

**Usage:**

```python
import replicate

# Get API key from https://replicate.com/account/api-tokens
output = replicate.run(
    "jagilley/controlnet-pose:0a69b7f85f0b7d6c54c9aeb3f9d1b8e1a6d42e8a9f5e3d1c7b2a8e5f3d1a9c6e",
    input={
        "image": "https://example.com/pose_reference.jpg",
        "prompt": "professional yoga instructor doing downward dog pose, yoga studio, natural lighting, high quality photo",
        "negative_prompt": "blurry, low quality, deformed, disfigured, extra limbs",
        "num_samples": "4",
        "image_resolution": "512",
        "ddim_steps": "20"
    }
)
print(output)
```

**Cost Estimate:**
- 50 poses × 4 variations each = 200 images
- 200 × $0.005 = **~$1.00**

### 2. Midjourney (Best Quality) - RECOMMENDED for Final Assets

**Pros:**
- Highest quality results
- Artistic control
- Consistent character generation
- Great for marketing materials

**Cons:**
- No API (Discord-based)
- $10/month minimum
- Manual workflow

**Setup:**
1. Subscribe at https://midjourney.com ($10/month Basic)
2. Join Discord server
3. Use `/imagine` command

**Character Consistency Workflow:**

```
Step 1: Generate base character
/imagine professional yoga instructor, athletic build, ponytail,
wearing purple yoga outfit, neutral pose, studio lighting,
professional photo --ar 2:3 --style raw --v 6

Step 2: Save reference image (right-click → Copy Image URL)

Step 3: Generate poses with character reference
/imagine [paste image URL] professional yoga instructor doing
warrior 2 pose, yoga studio, natural lighting --ar 2:3 --style raw
--cref [paste image URL again] --cw 100 --v 6
```

**Batch Generation Strategy:**
1. Create character reference
2. Generate 4-8 variations per pose
3. Upscale best results with `U1`, `U2`, etc.
4. Use `Vary (Subtle)` for minor adjustments

**Example Prompts:**

```
Warrior 2:
professional yoga instructor doing warrior 2 pose, arms extended,
modern yoga studio, side view, natural lighting, professional photo --ar 2:3

Downward Dog:
yoga instructor in downward dog pose, hands and feet on yoga mat,
side profile, yoga studio, soft lighting, high quality --ar 3:2

Tree Pose:
athletic woman in tree pose, standing on one leg, hands in prayer,
peaceful expression, outdoor deck, sunrise lighting --ar 2:3
```

### 3. Leonardo.ai (Good Balance)

**Pros:**
- Free tier (150 tokens/day = ~25 images)
- Web interface + API
- Real-time generation
- ControlNet support

**Pricing:**
- Free: 150 tokens/day
- Apprentice: $12/month (8,500 tokens)
- Artisan: $30/month (25,000 tokens)

**Setup:**
1. Sign up at https://leonardo.ai
2. Go to AI Image Generation
3. Select "Leonardo Diffusion XL" model
4. Enable ControlNet with pose input

### 4. Stable Diffusion XL on RunPod (Cloud GPU)

**Best for:** Large batches, need full control, want local-like experience

**Pros:**
- Pay only for GPU time ($0.34/hour for RTX 3090)
- Full ComfyUI/A1111 access
- Can run overnight batches

**Setup:**
1. Sign up at https://runpod.io
2. Deploy ComfyUI template
3. Upload pose references
4. Run batch generation
5. Download results

**Cost Estimate:**
- 1 hour of generation = ~500 images
- 500 images @ $0.34/hour = **$0.00068 per image**

## Recommended Workflow

### For Quick Start (This Weekend):

1. **Midjourney** for 10-20 hero poses
   - High quality, use for featured content
   - Time: 2-3 hours
   - Cost: $10 (subscription)

2. **Replicate API** for remaining poses
   - Automate with Python script
   - Time: 1 hour setup + 30 minutes generation
   - Cost: $1-5

### For Production Scale:

1. **RunPod** with ComfyUI
   - Rent GPU for 2-4 hours
   - Generate all poses in batch
   - Cost: $1-2
   - Time: 1 hour setup + 2-3 hours generation

## Batch Generation Script (Replicate)

```python
import replicate
import json
import os

# Load your poses from database
poses = [
    {"id": 1, "name": "Downward Dog", "sanskrit": "Adho Mukha Svanasana"},
    {"id": 2, "name": "Warrior 2", "sanskrit": "Virabhadrasana II"},
    # ... more poses
]

# Character description for consistency
CHARACTER = "professional yoga instructor, athletic build, wearing navy blue yoga outfit"

for pose in poses:
    prompt = f"{CHARACTER}, performing {pose['name']}, yoga studio, natural lighting, professional photo, high quality"

    print(f"Generating: {pose['name']}")

    output = replicate.run(
        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        input={
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, deformed, extra limbs, bad anatomy",
            "num_outputs": 4,
            "width": 768,
            "height": 1024
        }
    )

    # Save image URLs
    pose['generated_images'] = output

    # Save to file
    with open(f"generated_poses/{pose['id']}_{pose['name'].replace(' ', '_')}.json", 'w') as f:
        json.dump(pose, f, indent=2)

    print(f"  Generated {len(output)} variations")

print("Done! Check generated_poses/ directory")
```

## Quality Guidelines

### Image Specifications
- **Resolution**: Minimum 1024x1024 (square) or 768x1024 (portrait)
- **Format**: JPEG (web) or PNG (if transparency needed)
- **File size**: Under 500KB per image (optimize with TinyPNG)

### Prompt Best Practices

**Structure:**
```
[character description], [action/pose], [environment],
[lighting], [quality modifiers] --ar [aspect ratio]
```

**Character Consistency:**
- Use same character description across all prompts
- Use `--cref` (Midjourney) or embeddings (SD) for consistency
- Keep outfit/style consistent

**Lighting:**
- "natural window lighting" - soft, flattering
- "studio lighting" - professional, even
- "golden hour" - warm, outdoor feeling
- "soft diffused light" - gentle, not harsh

**Quality Modifiers:**
- professional photography
- high quality
- detailed
- sharp focus
- 8k resolution

### Negative Prompts
Always include:
```
blurry, low quality, deformed, disfigured, extra limbs,
bad anatomy, poorly drawn hands, mutation, watermark,
signature, text, error, cropped
```

## Cost Comparison

| Service | Setup | 100 Images | 500 Images | Best For |
|---------|-------|------------|------------|----------|
| Replicate | 5 min | $0.50 | $2.50 | Automation |
| Midjourney | 10 min | $10/mo | $10/mo | Quality |
| Leonardo.ai | 5 min | Free-$12 | $30 | Balance |
| RunPod | 30 min | $0.34 | $1.70 | Batch |

## Next Steps

1. Choose your service based on needs
2. Generate 2-3 test poses to verify quality
3. Refine prompts and settings
4. Run batch generation
5. Review and select best variations
6. Upload to storage and update database

## Example Database Update

```python
# After generating images
import psycopg2

conn = psycopg2.connect("postgresql://yogaflow:password@localhost:5432/yogaflow")
cur = conn.cursor()

pose_images = {
    1: ["https://storage.example.com/poses/downward-dog-1.jpg",
        "https://storage.example.com/poses/downward-dog-2.jpg"],
    2: ["https://storage.example.com/poses/warrior-2-1.jpg"],
    # ...
}

for pose_id, image_urls in pose_images.items():
    cur.execute(
        "UPDATE poses SET image_urls = %s WHERE id = %s",
        (json.dumps(image_urls), pose_id)
    )

conn.commit()
```
