"""
Security headers middleware for YogaFlow API.
Adds security headers to all responses.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Headers added:
    - X-Content-Type-Options: Prevent MIME sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filter
    - Strict-Transport-Security: Force HTTPS (production only)
    - Content-Security-Policy: Restrict resource loading
    - Referrer-Policy: Control referrer information
    """

    def __init__(self, app, environment: str = "development"):
        super().__init__(app)
        self.environment = environment

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response: Response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS (HTTP Strict Transport Security) - Production only
        if self.environment == "production":
            # Force HTTPS for 1 year, include subdomains
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        # Adjust CSP based on your needs
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Adjust for production
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Permissions Policy (formerly Feature-Policy)
        permissions_directives = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()"
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_directives)

        return response
