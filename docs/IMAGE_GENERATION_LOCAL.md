# Local Yoga Pose Image Generation Guide

## Overview
This guide covers generating yoga pose images locally using Stable Diffusion with ControlNet for pose control.

## Prerequisites
- Python 3.10+
- 16GB+ RAM recommended (8GB minimum)
- GPU with 6GB+ VRAM (optional but 10-100x faster)
- ~20GB disk space for models

## Option 1: ComfyUI (Recommended - Most Flexible)

### Installation

```bash
cd ~/
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python -m venv venv
source venv/bin/activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### Download Models

```bash
# Create model directories
mkdir -p models/checkpoints models/controlnet

# Download Stable Diffusion model (choose one)
# Option A: Realistic Vision (photorealistic)
cd models/checkpoints
curl -L -o realisticVision_v60B1.safetensors \
  "https://civitai.com/api/download/models/245598"

# Option B: DreamShaper (versatile, good for yoga)
curl -L -o dreamshaper_8.safetensors \
  "https://civitai.com/api/download/models/128713"

# Download ControlNet OpenPose model
cd ../controlnet
curl -L -o control_v11p_sd15_openpose.pth \
  "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth"
```

### Start ComfyUI

```bash
cd ~/ComfyUI
source venv/bin/activate
python main.py

# Access at http://127.0.0.1:8188
```

### Workflow Setup

1. Load the ControlNet OpenPose workflow (examples included in ComfyUI)
2. Upload a reference pose image (stick figure or photo)
3. Set prompt: "professional yoga instructor doing downward dog pose, yoga studio, natural lighting, high quality photo"
4. Generate images

## Option 2: Automatic1111 WebUI (User-Friendly)

### Installation

```bash
cd ~/
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui
./webui.sh --skip-torch-cuda-test  # First run downloads everything
```

### Install ControlNet Extension

1. Start WebUI: `./webui.sh`
2. Go to Extensions → Install from URL
3. Paste: `https://github.com/Mikubill/sd-webui-controlnet`
4. Click Install, then restart

### Download Models (same as ComfyUI)
Place in `stable-diffusion-webui/models/Stable-diffusion/` and `stable-diffusion-webui/models/ControlNet/`

### Usage
1. Navigate to txt2img tab
2. Enable ControlNet section
3. Upload pose reference image
4. Set control type to "OpenPose"
5. Write prompt and generate

## Option 3: Python Script (Programmatic)

See `scripts/generate_poses_local.py` for automated batch generation.

## Pose Reference Sources

### Create Pose Skeletons
1. **From existing photos**: Use MediaPipe or OpenPose to extract skeleton
2. **Manual creation**: Use Photoshop/GIMP with stick figures
3. **Yoga pose databases**: Download CC-licensed yoga photos and extract poses

### Example: Extract Pose from Photo

```python
import mediapipe as mp
import cv2

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

image = cv2.imread('yoga_reference.jpg')
results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

# Draw skeleton
mp.solutions.drawing_utils.draw_landmarks(
    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
cv2.imwrite('pose_skeleton.jpg', image)
```

## Recommended Prompts

### Base Prompt Template
```
[subject], doing [yoga pose name], [environment], [lighting], [quality tags]
```

### Examples
- "Professional yoga instructor, doing warrior 2 pose, modern yoga studio, natural window lighting, high quality photography, 8k"
- "Athletic woman, performing tree pose, outdoor beach setting, golden hour, professional photo"
- "Yoga teacher, demonstrating downward dog, minimalist studio, soft studio lighting, detailed, sharp focus"

### Negative Prompts
```
blurry, low quality, deformed, disfigured, extra limbs, bad anatomy,
poorly drawn hands, mutation, watermark, signature
```

## Tips for Best Results

1. **Consistency**: Use the same checkpoint model and settings for all poses
2. **Batch processing**: Generate 4-8 variations per pose, pick the best
3. **Seed control**: Save seeds of good generations for similar results
4. **Resolution**: Generate at 512x768 (portrait) or 768x512 (landscape)
5. **Upscaling**: Use RealESRGAN or similar to upscale to 1024x1536 after

## Performance Notes

- **CPU only**: 2-5 minutes per image
- **GPU (6GB VRAM)**: 5-15 seconds per image
- **GPU (12GB+ VRAM)**: 3-8 seconds per image

## Troubleshooting

### Out of Memory
- Reduce image resolution to 512x512
- Use `--lowvram` or `--medvram` flags
- Close other applications

### Poor Quality
- Try different checkpoint models
- Increase sampling steps (20-30)
- Adjust CFG scale (7-9 works well)
- Use better pose reference images

## Next Steps

1. Generate test images with your preferred method
2. Organize output by pose name
3. Upload to cloud storage or local asset directory
4. Update database with image URLs
