# YogaFlow CDN Configuration Guide

## Overview

This guide covers CDN setup for YogaFlow image delivery with two approaches:
1. **Local Development**: Nginx with caching (included)
2. **Production**: CloudFlare CDN (recommended) or AWS CloudFront

## Local Development Setup (Nginx)

### Quick Start

The nginx configuration is already set up in `/infrastructure/nginx/nginx.conf` and integrated with Docker Compose.

**Start the nginx cache server:**

```bash
cd /Users/justinavery/claude/yoga-app
docker-compose up -d nginx
```

**Image URLs:**
- Local: `http://localhost/images/poses/warrior-pose.jpg`
- The nginx server will serve images from `/content/images/` with aggressive caching

### Configuration Details

**Cache Settings:**
- Cache duration: 1 year (images are immutable)
- Cache size: 1GB max
- Inactive eviction: 7 days
- Cache zone: 10MB in-memory index

**Performance Features:**
- Gzip compression for all text/json responses
- Sendfile for efficient static file serving
- TCP optimization (tcp_nopush, tcp_nodelay)
- Rate limiting: 30 requests/second for images

**Cache Headers:**
```
Cache-Control: public, max-age=31536000, immutable
Access-Control-Allow-Origin: *
X-Cache-Status: HIT|MISS|BYPASS
```

### Testing Local CDN

```bash
# Test image serving
curl -I http://localhost/images/poses/warrior-pose.jpg

# Expected headers:
# Cache-Control: public, max-age=31536000, immutable
# X-Cache-Status: MISS (first request) or HIT (subsequent)

# Test cache performance
ab -n 1000 -c 10 http://localhost/images/poses/warrior-pose.jpg
```

## CloudFlare CDN Setup (Production)

### Why CloudFlare?

- **Free Tier**: Unlimited bandwidth, global CDN
- **DDoS Protection**: Built-in security
- **SSL/TLS**: Free certificates
- **Image Optimization**: Automatic WebP conversion, resizing
- **Analytics**: Real-time traffic insights

### Setup Steps

#### 1. Sign Up for CloudFlare

1. Go to [cloudflare.com](https://www.cloudflare.com)
2. Sign up for a free account
3. Add your domain (e.g., yogaflow.app)

#### 2. Update DNS Records

Add a CNAME record for your CDN subdomain:

```
Type: CNAME
Name: cdn
Target: yourdomain.com
Proxy status: Proxied (orange cloud)
TTL: Auto
```

Your images will be served from: `https://cdn.yogaflow.app/images/`

#### 3. Configure Caching Rules

In CloudFlare dashboard:

**Page Rules** (free tier: 3 rules):

1. **Image Caching Rule**
   ```
   URL: cdn.yogaflow.app/images/*
   Settings:
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 month
   - Browser Cache TTL: 1 year
   ```

2. **API Bypass Rule**
   ```
   URL: cdn.yogaflow.app/api/*
   Settings:
   - Cache Level: Bypass
   ```

**Cache Rules** (if available):

```yaml
Rule 1: Image Caching
  If: Hostname equals cdn.yogaflow.app AND URI Path starts with /images/
  Then:
    - Cache eligibility: Eligible for cache
    - Cache TTL: 1 month
    - Browser TTL: 1 year
    - Respect origin cache control: No
```

#### 4. Enable Image Optimization

In CloudFlare dashboard → Speed → Optimization:

- ✅ **Auto Minify**: JavaScript, CSS, HTML
- ✅ **Brotli**: Enable
- ✅ **Rocket Loader**: Enable
- ✅ **Mirage**: Enable (lossy image optimization)
- ✅ **Polish**: Lossless or Lossy (choose based on quality needs)
- ✅ **WebP**: Enable (automatic format conversion)

#### 5. Configure Security

**SSL/TLS**:
- Mode: Full (strict) or Flexible
- Always Use HTTPS: On
- Minimum TLS Version: 1.2

**Firewall Rules** (optional):
```
Rule: Rate Limit Images
  If: Hostname equals cdn.yogaflow.app AND URI Path starts with /images/
  Then: Rate limit > 100 requests per minute
```

#### 6. Update Backend Configuration

Update your backend to use CloudFlare CDN URLs:

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # ...
    cdn_base_url: str = "https://cdn.yogaflow.app"
    cdn_enabled: bool = True
```

Add to `.env`:
```env
CDN_BASE_URL=https://cdn.yogaflow.app
CDN_ENABLED=true
```

#### 7. Update Frontend

Update image URLs in frontend to use CDN:

```typescript
// frontend/src/config/cdn.ts
export const CDN_CONFIG = {
  enabled: import.meta.env.VITE_CDN_ENABLED === 'true',
  baseUrl: import.meta.env.VITE_CDN_BASE_URL || 'https://cdn.yogaflow.app',
};

export function getCdnUrl(path: string): string {
  if (!CDN_CONFIG.enabled) {
    return path;
  }
  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${CDN_CONFIG.baseUrl}/${cleanPath}`;
}

// Usage:
// <img src={getCdnUrl('images/poses/warrior-pose.jpg')} />
```

Add to `.env`:
```env
VITE_CDN_ENABLED=true
VITE_CDN_BASE_URL=https://cdn.yogaflow.app
```

### Testing CloudFlare CDN

```bash
# Test image delivery
curl -I https://cdn.yogaflow.app/images/poses/warrior-pose.jpg

# Check for CloudFlare headers:
# cf-cache-status: HIT|MISS|EXPIRED
# cf-ray: [ray-id]
# server: cloudflare

# Test from multiple locations
curl -H "CF-IPCountry: US" https://cdn.yogaflow.app/images/poses/warrior-pose.jpg
curl -H "CF-IPCountry: EU" https://cdn.yogaflow.app/images/poses/warrior-pose.jpg
```

## AWS CloudFront (Alternative)

If you prefer AWS:

### Setup Steps

1. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://yogaflow-images
   aws s3 sync ./content/images/ s3://yogaflow-images/images/
   ```

2. **Create CloudFront Distribution**
   - Origin: S3 bucket
   - Cache behavior: Cache everything
   - TTL: 31536000 (1 year)
   - Compress objects: Yes

3. **Update Configuration**
   ```env
   CDN_BASE_URL=https://d1234567890.cloudfront.net
   CDN_ENABLED=true
   ```

### Cost Comparison

**CloudFlare Free Tier:**
- ✅ Unlimited bandwidth
- ✅ Global CDN (200+ cities)
- ✅ DDoS protection
- ✅ Free SSL
- ❌ Limited page rules (3)

**AWS CloudFront:**
- ❌ $0.085/GB (first 10TB)
- ✅ Pay-as-you-go
- ✅ Advanced features
- ❌ Requires S3 storage

## Image Optimization Best Practices

### 1. Image Format Strategy

```
Original → Serve
.jpg     → .webp (with .jpg fallback)
.png     → .webp (with .png fallback)
.svg     → .svg (no optimization needed)
```

### 2. Responsive Images

Use `srcset` for different screen sizes:

```html
<img
  src="https://cdn.yogaflow.app/images/poses/warrior-pose.jpg"
  srcset="
    https://cdn.yogaflow.app/images/poses/warrior-pose-400w.jpg 400w,
    https://cdn.yogaflow.app/images/poses/warrior-pose-800w.jpg 800w,
    https://cdn.yogaflow.app/images/poses/warrior-pose-1200w.jpg 1200w
  "
  sizes="(max-width: 768px) 100vw, 50vw"
  alt="Warrior Pose"
  loading="lazy"
/>
```

### 3. Image Compression

Pre-compress images before uploading:

```bash
# Install tools
brew install jpegoptim optipng

# Optimize JPEG (85% quality)
jpegoptim --max=85 --strip-all image.jpg

# Optimize PNG
optipng -o7 image.png
```

### 4. Lazy Loading

Always use `loading="lazy"` for images below the fold:

```html
<img src="..." loading="lazy" alt="..." />
```

## Performance Targets

### Goals
- **First Load**: < 1 second
- **Cached Load**: < 100ms
- **Cache Hit Rate**: > 95%
- **Bandwidth Savings**: > 50% (with compression)

### Monitoring

**CloudFlare Analytics:**
- Dashboard → Analytics → Performance
- Check cache hit rate, bandwidth saved, response time

**Chrome DevTools:**
```javascript
// Check image load times
performance.getEntriesByType('resource')
  .filter(r => r.initiatorType === 'img')
  .map(r => ({ name: r.name, duration: r.duration }))
  .sort((a, b) => b.duration - a.duration)
```

## Backend Integration

### CDN Helper Service

Create `/backend/app/services/cdn_service.py`:

```python
"""CDN service for image URL generation."""
from app.core.config import settings

class CDNService:
    """Generate CDN URLs for static assets."""

    def get_image_url(self, path: str) -> str:
        """
        Get CDN URL for an image.

        Args:
            path: Relative image path (e.g., 'poses/warrior-pose.jpg')

        Returns:
            str: Full CDN URL or local URL if CDN disabled
        """
        if not settings.cdn_enabled:
            return f"/images/{path}"

        # Remove leading slash if present
        clean_path = path.lstrip('/')
        return f"{settings.cdn_base_url}/images/{clean_path}"

    def get_thumbnail_url(self, path: str, width: int = 400) -> str:
        """
        Get CDN URL for image thumbnail.

        Args:
            path: Relative image path
            width: Thumbnail width in pixels

        Returns:
            str: Full CDN URL for thumbnail
        """
        base_url = self.get_image_url(path)

        # CloudFlare image resizing (requires paid plan)
        # return f"{base_url}/cdn-cgi/image/width={width},format=auto/{path}"

        # For now, return standard URL
        return base_url

cdn_service = CDNService()
```

### Use in API Responses

```python
from app.services.cdn_service import cdn_service

@router.get("/poses/{pose_id}")
async def get_pose(pose_id: int, db_session: DatabaseSession):
    pose = await get_pose_by_id(pose_id, db_session)

    # Convert image paths to CDN URLs
    return {
        "pose_id": pose.pose_id,
        "name": pose.name,
        "image_url": cdn_service.get_image_url(pose.image_path),
        "thumbnail_url": cdn_service.get_thumbnail_url(pose.image_path, width=400),
    }
```

## Troubleshooting

### Images not loading from CDN

1. Check DNS propagation: `dig cdn.yogaflow.app`
2. Verify CloudFlare proxy is enabled (orange cloud)
3. Check cache rules are active
4. Test origin server directly

### Slow image loading

1. Check cache hit rate in CloudFlare analytics
2. Verify images are compressed
3. Enable WebP conversion
4. Check origin server response time

### CORS errors

Add CORS headers in nginx config:
```nginx
add_header Access-Control-Allow-Origin "*" always;
add_header Access-Control-Allow-Methods "GET, HEAD, OPTIONS" always;
```

Or in CloudFlare:
- Workers → Create Worker → Add CORS headers

## Next Steps

1. ✅ Set up local nginx CDN for development
2. ⬜ Upload images to `/content/images/`
3. ⬜ Test local CDN performance
4. ⬜ Sign up for CloudFlare (when ready for staging)
5. ⬜ Configure CloudFlare caching rules
6. ⬜ Update backend CDN service
7. ⬜ Update frontend to use CDN URLs
8. ⬜ Monitor performance and cache hit rates
