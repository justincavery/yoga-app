# Overnight Image Generation Status

## Summary

✅ **Batch generation is running!**

Started: December 15, 2025 at 11:47 PM
Process ID: 58460
Status: Running in background with `nohup`

## Configuration

- **Total poses**: 50
- **First 10 poses**: Using `gemini-3-pro-image-preview` (PRO model)
- **Remaining 40 poses**: Using `gemini-2.5-flash-image` (FLASH model)
- **Rate limiting**: 1 image per 60 seconds
- **Max retries per pose**: 10 (with automatic prompt modifications for safety)
- **Output directory**: `/Users/justinavery/claude/yoga-app/content/images/poses/`

## Estimated Completion

- **Time per image**: ~60 seconds (plus 10-15 seconds generation time)
- **Total estimated time**: ~60-70 minutes for all 50 images
- **Expected completion**: Around 1:00 AM

## Monitoring Progress

### Check if process is still running:
```bash
ps -p 58460
```

### View detailed live log:
```bash
tail -f /Users/justinavery/claude/yoga-app/scripts/image-generation/gemini_generation_detailed.log
```

### View summary log (JSON):
```bash
cat /Users/justinavery/claude/yoga-app/scripts/image-generation/gemini_generation_log.json
```

### Count generated images:
```bash
ls -1 /Users/justinavery/claude/yoga-app/content/images/poses/ | wc -l
```

### View all generated images:
```bash
ls -lh /Users/justinavery/claude/yoga-app/content/images/poses/
```

## Current Progress (as of start)

✅ **Successfully generated**:
1. Mountain Pose (PRO model) - 1408x768 JPEG
2. Downward Facing Dog (PRO model) - 1408x768 JPEG

🔄 **In progress**:
- Pose 3 of 50...

## Features

### Automatic Retry with Prompt Modifications
If a prompt is rejected due to content guidelines, the script automatically:
1. Adds professional/fitness context
2. Emphasizes educational purpose
3. Adds more specific clothing details
4. Emphasizes studio/professional setting
5. Up to 10 different variations

### Comprehensive Logging
- **Detailed log**: `gemini_generation_detailed.log` - Full output with timestamps
- **JSON log**: `gemini_generation_log.json` - Structured data with:
  - Configuration
  - Summary stats
  - Per-pose attempts and results
  - Prompts used for each attempt

### Output Format
- **File naming**: `pose-name.png` (e.g., `mountain-pose.png`, `downward-facing-dog.png`)
- **Image format**: PNG or JPEG (as provided by Gemini)
- **Image size**: Typically 1408x768 or 1024x1024 pixels

## After Completion

When you wake up, check:

1. **Final status**:
   ```bash
   cat gemini_generation_log.json | grep -A 5 '"summary"'
   ```

2. **View all images**:
   ```bash
   open /Users/justinavery/claude/yoga-app/content/images/poses/
   ```

3. **Compare PRO vs FLASH models**:
   - First 10 images (PRO): Mountain Pose through Chair Pose
   - Remaining 40 images (FLASH): Standing Forward Fold through Easy Pose

## Troubleshooting

### If process stopped early:
```bash
# Check if still running
ps -p 58460

# If not running, check the log for errors
tail -100 gemini_generation_detailed.log

# Restart from where it left off (manually edit script to start from last successful pose)
```

### If some poses failed:
- Check `gemini_generation_log.json` for failed poses
- Review the prompts that were tried
- Can manually re-run specific poses if needed

## API Information

- **API Key**: Configured (ending in ...ojck)
- **Models**:
  - `gemini-3-pro-image-preview` (for comparison)
  - `gemini-2.5-flash-image` (main model)
- **Rate limits**: 20 requests per minute (we're doing 1 per minute to be safe)
- **Cost**: ~$0.039 per image

## Files Created

- `/content/images/poses/*.png` - Generated pose images
- `gemini_generation_detailed.log` - Detailed execution log
- `gemini_generation_log.json` - Structured results log
- `generation_output.log` - Background process output (nohup)

---

**Enjoy your sleep! The images will be ready when you wake up. 🧘‍♀️✨**
