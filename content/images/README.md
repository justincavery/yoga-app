# YogaFlow Image Assets

This directory contains all image assets for the YogaFlow application.

## Directory Structure

```
images/
├── poses/          # Pose images (full size)
├── thumbnails/     # Pose thumbnails (400x400)
└── README.md       # This file
```

## Image Guidelines

### Pose Images
- **Dimensions**: 800x600 or 1200x900 (landscape)
- **Format**: JPEG for photos, PNG for graphics with transparency
- **Quality**: 85% JPEG quality
- **Size**: < 200KB per image
- **Naming**: kebab-case (e.g., `warrior-pose.jpg`, `downward-dog.jpg`)

### Thumbnails
- **Dimensions**: 400x400 (square)
- **Format**: JPEG
- **Quality**: 80% JPEG quality
- **Size**: < 50KB per image
- **Naming**: Same as pose images (e.g., `warrior-pose.jpg`)

## Image Optimization

Before adding images to this directory, optimize them:

```bash
# Install optimization tools
brew install jpegoptim optipng

# Optimize JPEG (85% quality)
jpegoptim --max=85 --strip-all image.jpg

# Optimize PNG
optipng -o7 image.png

# Batch optimize all JPEGs
find . -name "*.jpg" -exec jpegoptim --max=85 --strip-all {} \;
```

## Adding New Images

1. **Prepare Image**
   - Crop to correct dimensions
   - Optimize file size
   - Use descriptive filename

2. **Add to Repository**
   ```bash
   # Add pose image
   cp optimized-pose.jpg content/images/poses/warrior-pose.jpg

   # Add thumbnail
   cp optimized-thumbnail.jpg content/images/thumbnails/warrior-pose.jpg
   ```

3. **Update Database**
   ```sql
   INSERT INTO poses (name, image_path, thumbnail_path, ...)
   VALUES ('Warrior Pose', 'poses/warrior-pose.jpg', 'thumbnails/warrior-pose.jpg', ...);
   ```

4. **Test CDN Serving**
   ```bash
   # Local CDN
   curl -I http://localhost/images/poses/warrior-pose.jpg

   # Production CDN
   curl -I https://cdn.yogaflow.app/images/poses/warrior-pose.jpg
   ```

## CDN Integration

Images in this directory are automatically served via:

- **Local Development**: Nginx CDN (`http://localhost/images/`)
- **Production**: CloudFlare CDN (`https://cdn.yogaflow.app/images/`)

The backend CDN service automatically generates correct URLs based on environment.

## Copyright & Licensing

All images must have proper licensing:

- **Stock Photos**: Pexels, Unsplash (free commercial use)
- **Custom Photography**: Ensure model releases
- **Graphics**: Ensure proper attribution

Add attribution in `/content/ATTRIBUTION.md` if required by license.

## Sample Images

For development, you can use free stock photos from:

- [Pexels Yoga Collection](https://www.pexels.com/search/yoga/)
- [Unsplash Yoga Photos](https://unsplash.com/s/photos/yoga)
- [Pixabay Yoga Images](https://pixabay.com/images/search/yoga/)

Example download:
```bash
# Download sample yoga image from Pexels
wget -O content/images/poses/meditation-pose.jpg \
  "https://images.pexels.com/photos/3822906/pexels-photo-3822906.jpeg?w=800"

# Optimize it
jpegoptim --max=85 --strip-all content/images/poses/meditation-pose.jpg
```

## Git LFS (Optional)

For larger image repositories, consider using Git LFS:

```bash
# Install Git LFS
brew install git-lfs
git lfs install

# Track image files
git lfs track "*.jpg"
git lfs track "*.png"
git add .gitattributes

# Add and commit
git add content/images/
git commit -m "Add pose images"
```

## Performance Monitoring

Monitor image loading performance:

```javascript
// Check image load times in browser console
performance.getEntriesByType('resource')
  .filter(r => r.initiatorType === 'img')
  .map(r => ({
    name: r.name.split('/').pop(),
    duration: Math.round(r.duration) + 'ms',
    size: r.transferSize ? (r.transferSize / 1024).toFixed(2) + 'KB' : 'cached'
  }))
  .sort((a, b) => parseFloat(b.duration) - parseFloat(a.duration))
```

Target: All images load in < 1 second on 3G connection.
