"""
Email service for YogaFlow.
Handles transactional email sending with templates.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from app.core.config import settings
from app.core.logging_config import logger


class EmailService:
    """
    Service for sending transactional emails.
    Supports templated emails with HTML and plain text fallback.
    """

    def __init__(self):
        """Initialize email service with template engine."""
        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email using configured SMTP settings.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not settings.email_enabled:
            logger.warning(
                "Email service disabled - skipping email",
                to_email=to_email,
                subject=subject
            )
            return False

        if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
            logger.error(
                "Email configuration incomplete",
                smtp_host=settings.smtp_host,
                smtp_user=settings.smtp_user
            )
            return False

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{settings.email_from_name} <{settings.email_from}>"
            message["To"] = to_email
            message["Subject"] = subject

            # Add plain text version if provided
            if text_body:
                part1 = MIMEText(text_body, "plain")
                message.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_body, "html")
            message.attach(part2)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user,
                password=settings.smtp_password,
                use_tls=settings.smtp_tls,
                start_tls=settings.smtp_tls and not settings.smtp_ssl,
            )

            logger.info(
                "Email sent successfully",
                to_email=to_email,
                subject=subject
            )
            return True

        except Exception as error:
            logger.error(
                "Failed to send email",
                error=str(error),
                to_email=to_email,
                subject=subject
            )
            return False

    async def send_welcome_email(self, to_email: str, name: str) -> bool:
        """
        Send welcome email to new user.

        Args:
            to_email: User's email address
            name: User's name

        Returns:
            bool: True if email sent successfully
        """
        try:
            template = self.template_env.get_template("welcome.html")
            html_body = template.render(
                name=name,
                app_name=settings.app_name,
                frontend_url=settings.frontend_url
            )

            subject = f"Welcome to {settings.app_name}!"

            return await self.send_email(
                to_email=to_email,
                subject=subject,
                html_body=html_body
            )
        except Exception as error:
            logger.error(
                "Failed to send welcome email",
                error=str(error),
                to_email=to_email
            )
            return False

    async def send_verification_email(
        self,
        to_email: str,
        name: str,
        verification_token: str
    ) -> bool:
        """
        Send email verification email with token link.

        Args:
            to_email: User's email address
            name: User's name
            verification_token: Verification token for URL

        Returns:
            bool: True if email sent successfully
        """
        try:
            verification_url = f"{settings.frontend_url}/verify-email?token={verification_token}"

            template = self.template_env.get_template("verification.html")
            html_body = template.render(
                name=name,
                verification_url=verification_url,
                app_name=settings.app_name
            )

            subject = f"Verify your {settings.app_name} email"

            return await self.send_email(
                to_email=to_email,
                subject=subject,
                html_body=html_body
            )
        except Exception as error:
            logger.error(
                "Failed to send verification email",
                error=str(error),
                to_email=to_email
            )
            return False

    async def send_password_reset_email(
        self,
        to_email: str,
        name: str,
        reset_token: str
    ) -> bool:
        """
        Send password reset email with token link.

        Args:
            to_email: User's email address
            name: User's name
            reset_token: Password reset token for URL

        Returns:
            bool: True if email sent successfully
        """
        try:
            reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"

            template = self.template_env.get_template("password_reset.html")
            html_body = template.render(
                name=name,
                reset_url=reset_url,
                app_name=settings.app_name
            )

            subject = f"Reset your {settings.app_name} password"

            return await self.send_email(
                to_email=to_email,
                subject=subject,
                html_body=html_body
            )
        except Exception as error:
            logger.error(
                "Failed to send password reset email",
                error=str(error),
                to_email=to_email
            )
            return False


def generate_verification_token() -> str:
    """
    Generate a secure random token for email verification.

    Returns:
        str: URL-safe random token
    """
    return secrets.token_urlsafe(32)


# Global email service instance
email_service = EmailService()
