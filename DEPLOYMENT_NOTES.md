# Deployment Notes - Pose Images Update

## Date: 2025-12-15

### Changes Deployed
- ✅ 15 optimized pose images (JPEG, <200KB each)
- ✅ 15 thumbnails (400x400, <25KB each)
- ✅ Backend static file serving configured
- ✅ Frontend proxy configuration
- ✅ Image optimization and thumbnail generation scripts

### Post-Deployment Required

#### 1. Update Database with Image URLs

SSH into the production server and run:

```bash
# SSH into server
ssh root@your-hetzner-server

# Navigate to backend directory
cd /path/to/yoga-app/backend

# Activate virtual environment
source venv/bin/activate

# Run database update script
python scripts/update_pose_images.py
```

This will update 12 poses with their image URLs:
- Mountain Pose (ID 1)
- Child's Pose (ID 2)
- Downward Facing Dog (ID 3)
- Cat-Cow Pose (ID 4)
- Standing Forward Bend (ID 7)
- Warrior I (ID 8)
- Tree Pose (ID 10)
- Warrior II (ID 11)
- Triangle Pose (ID 12)
- Extended Side Angle Pose (ID 13)
- Half Moon Pose (ID 47)
- Warrior III (ID 48)

#### 2. Verify Static Files are Accessible

Check that images are being served:
```bash
curl -I https://your-domain.com/images/poses/mountain-pose.jpg
```

Should return HTTP 200 with Content-Type: image/jpeg

#### 3. Clear Frontend Cache (if needed)

If users don't see images immediately:
```bash
# Force browser cache refresh
# Users: Press Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

### Testing Checklist

- [ ] Images load on pose list page
- [ ] Thumbnails display correctly
- [ ] Image URLs in API responses are correct
- [ ] No 404 errors in browser console
- [ ] Images are optimized (check file sizes)

### Remaining Work

3 images don't have matching poses in database:
- chair-pose.jpg
- plank-pose.jpg
- upward-facing-dog.jpg

These can be matched later or removed if not needed.

### Notes

- Images are stored in `content/images/poses/`
- Thumbnails in `content/images/thumbnails/`
- Backend serves them via StaticFiles mount
- Frontend proxies `/images` to backend in development
- Production should serve via CDN or nginx
