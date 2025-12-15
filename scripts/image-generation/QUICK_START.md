# Quick Start - Generate Yoga Pose Images

## 🚀 Fastest Path (Replicate API - 15 minutes)

### 1. Setup

```bash
cd scripts/image-generation

# Install dependencies
pip install replicate pillow requests psycopg2-binary

# Get API token from https://replicate.com/account/api-tokens
export REPLICATE_API_TOKEN=r8_your_token_here
```

### 2. Test Generation (5 poses)

```bash
python generate_replicate.py \
  --limit 5 \
  --variations 2 \
  --output ./test_poses
```

Cost: ~$0.05 | Time: ~2 minutes

### 3. Review Results

```bash
open test_poses/
```

### 4. Full Batch Generation

```bash
python generate_replicate.py \
  --variations 4 \
  --output ./final_poses
```

For 50 poses × 4 variations = 200 images
Cost: ~$1.00 | Time: ~5-10 minutes

### 5. Upload & Update Database

```bash
# Upload to storage
python upload_to_storage.py \
  --input ./final_poses \
  --provider local \
  --update-db

# Or upload to S3
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
python upload_to_storage.py \
  --input ./final_poses \
  --provider s3 \
  --bucket your-bucket \
  --base-url https://your-cdn.com \
  --update-db
```

Done! Your app now has pose images.

---

## 🏠 Local Generation Path (Stable Diffusion)

### 1. Install ComfyUI (One-time setup - 30 minutes)

```bash
cd ~/
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install torch torchvision torchaudio
pip install -r requirements.txt

# Download models
mkdir -p models/checkpoints models/controlnet
cd models/checkpoints
curl -L -o dreamshaper_8.safetensors \
  "https://civitai.com/api/download/models/128713"

cd ../controlnet
curl -L -o control_v11p_sd15_openpose.pth \
  "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth"
```

### 2. Start ComfyUI

```bash
cd ~/ComfyUI
source venv/bin/activate
python main.py

# Open browser: http://127.0.0.1:8188
```

### 3. Generate Images (Manual)

1. Load ControlNet workflow
2. Upload pose reference image
3. Set prompt: "professional yoga instructor doing [pose], yoga studio, natural lighting"
4. Generate!

### 4. Or Use Python Script

```bash
cd ~/yoga-app/scripts/image-generation

# Install dependencies
pip install torch diffusers transformers accelerate controlnet-aux

# Generate
python generate_local.py \
  --variations 4 \
  --output ./local_poses
```

**Performance:**
- CPU: ~2-5 min per image
- GPU (8GB VRAM): ~10 sec per image

---

## 🎨 Midjourney Path (Highest Quality)

### 1. Setup ($10/month)

1. Subscribe: https://midjourney.com
2. Join Discord server
3. Go to any bot channel

### 2. Create Character Reference

```
/imagine professional yoga instructor, athletic build,
wearing purple yoga outfit, neutral standing pose,
yoga studio, natural lighting, professional photo
--ar 2:3 --style raw --v 6
```

Save the best result's URL (right-click → Copy Image Link)

### 3. Generate Poses with Character

```
/imagine [paste reference URL] professional yoga instructor
performing downward dog pose, side view, yoga studio,
natural lighting, professional photo --ar 2:3
--cref [paste reference URL again] --cw 100 --v 6
```

### 4. Batch Generate

Repeat for each pose:
- Warrior 2
- Tree Pose
- Child's Pose
- etc.

Use `/describe` on existing yoga photos to get better prompts!

### 5. Download & Upload

1. Download images from Discord (click → Open in Browser → Save)
2. Organize by pose name
3. Upload to storage
4. Update database

---

## 📋 Common Commands Cheat Sheet

### Generate Test Batch (Replicate)
```bash
python generate_replicate.py --limit 5 --variations 2
```

### Generate Specific Poses
```bash
python generate_replicate.py \
  --poses "Downward Dog" "Warrior 2" "Tree Pose" \
  --variations 4
```

### Custom Character
```bash
python generate_replicate.py \
  --character "male yoga instructor wearing gray outfit" \
  --variations 4
```

### Local Generation
```bash
python generate_local.py --variations 4 --seed 42
```

### Upload to Local Storage
```bash
python upload_to_storage.py \
  --input generated_poses \
  --provider local \
  --update-db
```

### Upload to S3
```bash
python upload_to_storage.py \
  --input generated_poses \
  --provider s3 \
  --bucket my-yoga-assets \
  --base-url https://cdn.example.com \
  --update-db
```

### Dry Run (Preview)
```bash
python upload_to_storage.py \
  --input generated_poses \
  --dry-run
```

---

## 💰 Cost Comparison

| Method | Time | Cost (50 poses) | Quality |
|--------|------|-----------------|---------|
| **Replicate** | 10 min | $1.00 | ⭐⭐⭐⭐ |
| **Midjourney** | 2-3 hrs | $10/mo | ⭐⭐⭐⭐⭐ |
| **Local (GPU)** | 1 hr | Free* | ⭐⭐⭐⭐ |
| **Local (CPU)** | 4-6 hrs | Free* | ⭐⭐⭐⭐ |

*After setup costs

---

## 🎯 Recommended Workflow

### For Quick MVP:
1. **Replicate** for all poses (15 min, $1-2)
2. Select best variations
3. Upload to local storage
4. Done!

### For Production:
1. **Midjourney** for 10-20 hero poses (best quality)
2. **Replicate** for remaining poses (speed + cost)
3. Upload to CDN (Cloudflare R2, AWS S3)
4. Update database
5. Ship!

### For Learning/Customization:
1. **Local Stable Diffusion** setup
2. Experiment with models and prompts
3. Fine-tune for your specific style
4. Generate on your schedule

---

## 🔧 Troubleshooting

### "No module named 'replicate'"
```bash
pip install replicate
```

### "REPLICATE_API_TOKEN not found"
```bash
export REPLICATE_API_TOKEN=your_token_here
# Or add to ~/.bashrc or ~/.zshrc
```

### "Error: manifest.json not found"
```bash
# Run generation script first
python generate_replicate.py --limit 5
```

### Database connection error
```bash
# Start backend database
cd ../../backend
docker-compose up -d db

# Test connection
psql postgresql://yogaflow:password@localhost:5432/yogaflow -c "SELECT COUNT(*) FROM poses;"
```

### Out of memory (local generation)
```bash
# Use smaller images
python generate_local.py --width 512 --height 512

# Or generate fewer at once
python generate_local.py --limit 10
```

---

## 📚 More Resources

- [Full Local Guide](../../docs/IMAGE_GENERATION_LOCAL.md)
- [Service Guide](../../docs/IMAGE_GENERATION_SERVICES.md)
- [Prompt Templates](./prompts.json)
- [Detailed README](./README.md)

---

## ❓ Need Help?

Common questions:

**Q: Which method should I use?**
A: Replicate API for fastest results. Local for learning/customization.

**Q: How do I get consistent character across poses?**
A: Use the same `--character` description in all prompts.

**Q: Can I use my own photos as reference?**
A: Yes! See docs for using ControlNet with custom pose references.

**Q: Images look weird/distorted?**
A: Try different prompts, increase quality modifiers, or generate more variations.

**Q: How do I update just one pose?**
A: `python generate_replicate.py --poses "Downward Dog" --variations 4`
