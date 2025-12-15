# ControlNet Quick Start

The issue: Text-to-image models can't reliably generate accurate yoga poses without pose guidance.

The solution: **ControlNet** uses a skeleton/reference image to guide generation.

## Option 1: Quick Test with Public Pose References (5 minutes)

Use existing pose images from the web:

```bash
# Test with a public yoga pose reference
python generate_replicate.py \
  --poses "Warrior 2" \
  --variations 2 \
  --pose-reference "https://i.imgur.com/example-warrior2-skeleton.png"
```

**The problem**: You need skeleton images for each pose.

## Option 2: Create Pose Skeletons (30 minutes)

### Setup
```bash
# Install additional dependencies
pip install mediapipe opencv-python

# Run setup script
python setup_controlnet.py
```

This will:
1. Download sample yoga photos
2. Extract pose skeletons using AI
3. Save skeletons in `pose_skeletons/` directory

### Upload Skeletons
Upload the skeletons to a public URL:
- **Imgur**: https://imgur.com/upload (free, easy)
- **Cloudflare R2**: More professional
- **GitHub**: Commit to your repo

### Generate with ControlNet
```bash
python generate_with_controlnet.py
```

## Option 3: Fastest Alternative - Use Midjourney ($10/mo)

Honestly, for your use case, **Midjourney might be faster**:

**Pros:**
- Better pose accuracy without ControlNet
- Character consistency features
- $10/month, unlimited generations in relaxed mode
- Manual but reliable

**Example workflow:**
```
1. Create character: /imagine fit brunette yoga instructor, gray outfit, standing neutral pose --ar 2:3 --cref
2. Generate poses: /imagine [character ref] performing warrior 2 pose --ar 2:3 --cref [character URL] --v 6
3. Repeat for each pose (30-60 min for 50 poses)
4. Download and use
```

## Recommendation

**Given your situation:**

1. **Right now**: Try Midjourney for 10-20 hero poses (2 hours, $10)
   - Better results, less setup
   - Manual but reliable

2. **This weekend**: Set up ControlNet properly (once)
   - Use for remaining poses
   - Automated, perfect accuracy
   - Uses your $50 Replicate credit

3. **Long term**: Automated ControlNet pipeline
   - Generate any new poses instantly
   - No manual work

**Want me to:**
- A) Help set up ControlNet (30-60 min investment)
- B) Write Midjourney prompts for your top poses (5 min)
- C) Try a different Replicate model first
