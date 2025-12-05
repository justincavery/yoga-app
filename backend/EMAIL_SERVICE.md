# YogaFlow Email Service Documentation

## Overview

The email service provides transactional email functionality for user authentication and notifications. It uses SMTP for email delivery with support for HTML templates.

## Features

- **Email Verification**: Sends verification emails with secure tokens after user registration
- **Password Reset**: Sends password reset emails with secure tokens (ready for future implementation)
- **Welcome Emails**: Sends welcome emails to new users
- **Template Engine**: Uses Jinja2 for HTML email templates
- **Async Support**: Fully async email sending with aiosmtplib

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Email Configuration
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

### Development Setup (Mailtrap)

1. Sign up for a free account at [Mailtrap.io](https://mailtrap.io/)
2. Create a new inbox
3. Copy the SMTP credentials (host, port, username, password)
4. Update your `.env` file with the credentials
5. Set `EMAIL_ENABLED=true`

### Production Setup

For production, use a professional email service:

#### SendGrid
```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
SMTP_TLS=true
SMTP_SSL=false
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=YogaFlow
FRONTEND_URL=https://yourdomain.com
```

#### Mailgun
```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-mailgun-domain.com
SMTP_PASSWORD=your_mailgun_password
SMTP_TLS=true
SMTP_SSL=false
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=YogaFlow
FRONTEND_URL=https://yourdomain.com
```

#### AWS SES
```env
EMAIL_ENABLED=true
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your_aws_access_key_id
SMTP_PASSWORD=your_aws_secret_access_key
SMTP_TLS=true
SMTP_SSL=false
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=YogaFlow
FRONTEND_URL=https://yourdomain.com
```

## Email Templates

Templates are located in `/backend/app/templates/email/`:

- **welcome.html**: Welcome email sent after registration
- **verification.html**: Email verification with token link
- **password_reset.html**: Password reset with token link

### Customizing Templates

Templates use Jinja2 syntax. Available variables:

#### Welcome Email
- `name`: User's name
- `app_name`: Application name
- `frontend_url`: Frontend URL

#### Verification Email
- `name`: User's name
- `app_name`: Application name
- `verification_url`: Complete verification URL with token

#### Password Reset Email
- `name`: User's name
- `app_name`: Application name
- `reset_url`: Complete password reset URL with token

## API Endpoints

### Registration Flow
1. `POST /api/v1/auth/register` - Creates user and sends verification email
2. User clicks link in email
3. `POST /api/v1/auth/verify-email?token=...` - Verifies email

### Resend Verification
`POST /api/v1/auth/resend-verification` - Resends verification email

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

## Usage Examples

### Testing Email Service

```python
from app.services.email_service import email_service

# Send verification email
await email_service.send_verification_email(
    to_email="user@example.com",
    name="John Doe",
    verification_token="abc123..."
)

# Send welcome email
await email_service.send_welcome_email(
    to_email="user@example.com",
    name="John Doe"
)
```

### Testing Verification Flow

```bash
# 1. Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "name": "Test User",
    "experience_level": "beginner"
  }'

# 2. Check Mailtrap inbox for verification email
# 3. Copy the token from the verification URL

# 4. Verify email
curl -X POST "http://localhost:8000/api/v1/auth/verify-email?token=YOUR_TOKEN_HERE"

# 5. Resend verification if needed
curl -X POST http://localhost:8000/api/v1/auth/resend-verification \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Security Considerations

1. **Token Generation**: Uses `secrets.token_urlsafe(32)` for secure random tokens
2. **Token Expiration**: Verification tokens expire after 24 hours
3. **HTTPS**: Always use HTTPS in production for `FRONTEND_URL`
4. **Environment Variables**: Never commit `.env` files with real credentials
5. **Email Validation**: Uses `email-validator` library for email format validation

## Troubleshooting

### Email not sending

1. Check `EMAIL_ENABLED=true` in `.env`
2. Verify SMTP credentials are correct
3. Check logs for error messages
4. Test SMTP connection manually

### Email sending but not received

1. Check spam folder
2. Verify `EMAIL_FROM` is allowed by SMTP provider
3. Check SMTP provider dashboard for delivery status
4. Verify recipient email is valid

### Template rendering errors

1. Check template file exists in `/backend/app/templates/email/`
2. Verify all required template variables are provided
3. Check logs for Jinja2 rendering errors

## Monitoring

Email service logs all operations with structured logging:

```python
# Success
logger.info("Email sent successfully", to_email=..., subject=...)

# Failure
logger.error("Failed to send email", error=..., to_email=..., subject=...)
```

Monitor these logs in production to track email delivery success rates.

## Future Enhancements

- [ ] Email queue with retry mechanism (Celery/Redis)
- [ ] Email analytics and tracking
- [ ] Multi-language email templates
- [ ] HTML/Text dual content for all emails
- [ ] Email preferences management
- [ ] Unsubscribe functionality
- [ ] Email bounce handling
- [ ] Rate limiting per user
