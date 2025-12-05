# YogaFlow DevOps Testing Guide

This guide covers testing procedures for the email service and CDN infrastructure.

## Prerequisites

```bash
cd /Users/justinavery/claude/yoga-app

# Ensure virtual environment is activated
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

## Email Service Testing

### 1. Setup Mailtrap for Testing

1. **Sign up for Mailtrap**
   - Go to [mailtrap.io](https://mailtrap.io/)
   - Create a free account
   - Create a new inbox

2. **Get SMTP Credentials**
   - Click on your inbox
   - Go to "SMTP Settings"
   - Copy credentials

3. **Update .env File**
   ```bash
   cd /Users/justinavery/claude/yoga-app/backend
   cp .env.example .env  # if not already done
   ```

   Edit `.env` and add your Mailtrap credentials:
   ```env
   EMAIL_ENABLED=true
   SMTP_HOST=sandbox.smtp.mailtrap.io
   SMTP_PORT=2525
   SMTP_USER=your_mailtrap_username
   SMTP_PASSWORD=your_mailtrap_password
   SMTP_TLS=true
   SMTP_SSL=false
   EMAIL_FROM=noreply@yogaflow.app
   EMAIL_FROM_NAME=YogaFlow
   FRONTEND_URL=http://localhost:3000
   ```

### 2. Start Backend Server

```bash
cd /Users/justinavery/claude/yoga-app/backend

# Activate virtual environment
source ../venv/bin/activate

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Test Registration Flow with Email

```bash
# Register a new user (email will be sent automatically)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "name": "Test User",
    "experience_level": "beginner"
  }'
```

**Expected Result:**
- HTTP 201 Created
- User created in database
- Verification email sent to Mailtrap inbox
- Response includes user data and auth tokens

**Verify in Mailtrap:**
1. Go to your Mailtrap inbox
2. Find the verification email
3. Check email content and HTML rendering
4. Copy the verification token from the URL

### 4. Test Email Verification

```bash
# Verify email with token from email
curl -X POST "http://localhost:8000/api/v1/auth/verify-email?token=YOUR_TOKEN_HERE"
```

**Expected Result:**
- HTTP 200 OK
- Email marked as verified in database
- Response: `{"message": "Email verified successfully", "email": "test@example.com"}`

### 5. Test Resend Verification Email

```bash
# Resend verification email
curl -X POST http://localhost:8000/api/v1/auth/resend-verification \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

**Expected Result:**
- HTTP 200 OK
- New verification email sent to Mailtrap
- New token generated
- Response: `{"message": "Verification email sent", "email": "test@example.com"}`

### 6. Test Error Cases

#### Already Verified Email
```bash
# Try to resend verification for already verified email
curl -X POST http://localhost:8000/api/v1/auth/resend-verification \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```
**Expected:** HTTP 400 - "Email already verified"

#### Invalid Token
```bash
# Try to verify with invalid token
curl -X POST "http://localhost:8000/api/v1/auth/verify-email?token=invalid_token_123"
```
**Expected:** HTTP 400 - "Invalid verification token"

#### Non-existent User
```bash
# Try to resend for non-existent user
curl -X POST http://localhost:8000/api/v1/auth/resend-verification \
  -H "Content-Type: application/json" \
  -d '{"email": "nonexistent@example.com"}'
```
**Expected:** HTTP 404 - "User not found"

## CDN Testing

### 1. Start Nginx CDN Server

```bash
cd /Users/justinavery/claude/yoga-app

# Ensure content/images directory exists
mkdir -p content/images/poses

# Add a test image (or download one)
# Example: wget -O content/images/poses/test-pose.jpg https://picsum.photos/800/600

# Start nginx container
docker-compose up -d nginx

# Check container status
docker-compose ps
```

### 2. Test Health Check

```bash
curl http://localhost/health
```

**Expected Result:**
```
healthy
```

### 3. Test Image Serving

```bash
# Test image serving (if you have a test image)
curl -I http://localhost/images/poses/test-pose.jpg
```

**Expected Headers:**
```
HTTP/1.1 200 OK
Cache-Control: public, max-age=31536000, immutable
X-Cache-Status: MISS (first request) or HIT (subsequent)
Access-Control-Allow-Origin: *
Content-Type: image/jpeg
```

### 4. Test Cache Performance

```bash
# First request (cache MISS)
time curl -o /dev/null -s http://localhost/images/poses/test-pose.jpg

# Second request (cache HIT - should be much faster)
time curl -o /dev/null -s http://localhost/images/poses/test-pose.jpg

# Check cache status
curl -I http://localhost/images/poses/test-pose.jpg | grep X-Cache-Status
```

### 5. Load Test CDN

```bash
# Install Apache Bench if not available
# brew install httpd (macOS)

# Run load test
ab -n 1000 -c 10 http://localhost/images/poses/test-pose.jpg
```

**Expected Results:**
- Requests per second: > 1000
- Time per request: < 10ms (after cache warming)
- Failed requests: 0

### 6. Test CDN Service in Backend

Create a test script:

```bash
cd /Users/justinavery/claude/yoga-app/backend
cat > test_cdn.py << 'EOF'
from app.services.cdn_service import cdn_service
from app.core.config import settings

# Test with CDN disabled
print(f"CDN Enabled: {cdn_service.is_cdn_enabled()}")
print(f"Image URL: {cdn_service.get_image_url('poses/warrior-pose.jpg')}")
print(f"Video URL: {cdn_service.get_video_url('tutorials/sun-salutation.mp4')}")
print(f"Cache Control: {cdn_service.get_cache_control_header('image')}")

# Test with CDN enabled
settings.cdn_enabled = True
settings.cdn_base_url = "https://cdn.yogaflow.app"
print(f"\nWith CDN enabled:")
print(f"Image URL: {cdn_service.get_image_url('poses/warrior-pose.jpg')}")
EOF

python test_cdn.py
```

**Expected Output:**
```
CDN Enabled: False
Image URL: /images/poses/warrior-pose.jpg
Video URL: /videos/tutorials/sun-salutation.mp4
Cache Control: public, max-age=31536000, immutable

With CDN enabled:
Image URL: https://cdn.yogaflow.app/images/poses/warrior-pose.jpg
```

## Integration Testing

### Full Email + Registration Flow

```bash
#!/bin/bash
# Full integration test

echo "1. Register user..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "integration-test@example.com",
    "password": "SecurePass123",
    "name": "Integration Test",
    "experience_level": "beginner"
  }')

echo "Response: $RESPONSE"
echo "2. Check Mailtrap for verification email"
echo "3. Copy token from email"
read -p "Enter verification token: " TOKEN

echo "4. Verify email..."
curl -X POST "http://localhost:8000/api/v1/auth/verify-email?token=$TOKEN"

echo -e "\n5. Test login..."
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "integration-test@example.com",
    "password": "SecurePass123",
    "remember_me": false
  }'
```

## Troubleshooting

### Email Service Issues

**Problem:** Emails not sending

**Solutions:**
1. Check `EMAIL_ENABLED=true` in `.env`
2. Verify SMTP credentials are correct
3. Check backend logs:
   ```bash
   # Look for email-related errors
   tail -f backend.log | grep -i email
   ```
4. Test SMTP connection manually:
   ```python
   import aiosmtplib
   import asyncio

   async def test_smtp():
       try:
           await aiosmtplib.send(
               MIMEText("Test"),
               hostname="sandbox.smtp.mailtrap.io",
               port=2525,
               username="your_username",
               password="your_password",
               use_tls=True
           )
           print("SMTP connection successful!")
       except Exception as e:
           print(f"SMTP error: {e}")

   asyncio.run(test_smtp())
   ```

**Problem:** Template rendering errors

**Solutions:**
1. Check template exists: `ls backend/app/templates/email/`
2. Verify Jinja2 is installed: `pip show jinja2`
3. Check template syntax

### CDN Issues

**Problem:** Nginx container not starting

**Solutions:**
1. Check nginx config syntax:
   ```bash
   docker run --rm -v $(pwd)/infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -t
   ```
2. Check logs:
   ```bash
   docker-compose logs nginx
   ```
3. Ensure port 80 is available:
   ```bash
   lsof -i :80
   ```

**Problem:** Images not loading

**Solutions:**
1. Check image directory exists and has files:
   ```bash
   ls -la content/images/
   ```
2. Check nginx logs:
   ```bash
   docker-compose logs nginx
   ```
3. Test directly:
   ```bash
   docker exec yogaflow-cdn ls -la /app/content/images/
   ```

**Problem:** Cache not working

**Solutions:**
1. Check cache directory permissions:
   ```bash
   docker exec yogaflow-cdn ls -la /var/cache/nginx/
   ```
2. Clear cache:
   ```bash
   docker exec yogaflow-cdn rm -rf /var/cache/nginx/images/*
   ```
3. Restart nginx:
   ```bash
   docker-compose restart nginx
   ```

## Performance Benchmarks

### Email Service
- Email sending time: < 2 seconds
- Template rendering: < 100ms
- Token generation: < 10ms

### CDN
- First request (cache MISS): < 100ms
- Cached request (cache HIT): < 10ms
- Cache hit rate target: > 95%
- Throughput: > 1000 requests/second

## Production Checklist

Before deploying to production:

### Email Service
- [ ] Use production SMTP service (SendGrid/Mailgun/AWS SES)
- [ ] Update `EMAIL_FROM` to real domain
- [ ] Configure SPF, DKIM, DMARC records
- [ ] Test email delivery to various providers (Gmail, Outlook, etc.)
- [ ] Set up email monitoring and alerts
- [ ] Implement email queue with retry mechanism

### CDN
- [ ] Sign up for CloudFlare or AWS CloudFront
- [ ] Configure custom domain (cdn.yogaflow.app)
- [ ] Set up SSL/TLS certificates
- [ ] Configure caching rules
- [ ] Enable image optimization
- [ ] Set up monitoring and alerts
- [ ] Test from multiple geographic locations
- [ ] Configure DDoS protection

## Monitoring

### Email Service Logs
```bash
# Watch email-related logs
docker-compose logs -f backend | grep -i email
```

### CDN Logs
```bash
# Watch nginx access logs
docker-compose logs -f nginx

# Check cache statistics
docker exec yogaflow-cdn cat /var/log/nginx/access.log | grep "cache:HIT" | wc -l
```

### Database Verification
```bash
# Check email verification status
docker exec -it yogaflow-postgres psql -U yogaflow -d yogaflow_dev -c "SELECT email, email_verified, created_at FROM users;"
```
