"""
JWT Token Blacklist Service using Redis

Implements token revocation for logout functionality.
When a user logs out, their JWT token is added to a blacklist
to prevent reuse until natural expiration.
"""
from typing import Optional
from datetime import datetime, timedelta
import redis.asyncio as redis

from app.core.config import settings
from app.core.logging_config import logger


class TokenBlacklist:
    """
    Redis-based token blacklist for JWT revocation.

    Tokens are stored with TTL matching their expiration time,
    so they're automatically removed when they would naturally expire.
    """

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379')

    async def connect(self):
        """Connect to Redis"""
        if self._redis is None:
            try:
                self._redis = await redis.from_url(
                    self._redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self._redis.ping()
                logger.info("Connected to Redis for token blacklist")
            except Exception as error:
                logger.warning(
                    "Failed to connect to Redis - token revocation disabled",
                    error=str(error)
                )
                self._redis = None

    async def disconnect(self):
        """Disconnect from Redis"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def is_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token: JWT access token

        Returns:
            bool: True if token is blacklisted, False otherwise
        """
        if self._redis is None:
            # Redis not available - can't check blacklist
            # For security, we could fail closed, but that would break
            # authentication entirely. In production, ensure Redis is available.
            return False

        try:
            key = f"blacklist:{token}"
            exists = await self._redis.exists(key)
            return exists > 0
        except Exception as error:
            logger.error("Error checking token blacklist", error=str(error))
            # Fail open - if Redis errors, allow the token
            # The token will still expire naturally via JWT expiration
            return False

    async def blacklist_token(self, token: str, expires_in_seconds: int):
        """
        Add a token to the blacklist.

        Args:
            token: JWT access token to blacklist
            expires_in_seconds: TTL for the blacklist entry (token's remaining lifetime)
        """
        if self._redis is None:
            logger.warning("Cannot blacklist token - Redis not available")
            return

        try:
            key = f"blacklist:{token}"
            # Store with TTL matching token expiration
            # Value doesn't matter, just the key existence
            await self._redis.setex(
                key,
                expires_in_seconds,
                "blacklisted"
            )
            logger.info(
                "Token blacklisted",
                ttl_seconds=expires_in_seconds
            )
        except Exception as error:
            logger.error("Error blacklisting token", error=str(error))

    async def blacklist_user_tokens(self, user_id: int, expires_in_seconds: int = 86400):
        """
        Blacklist all tokens for a user (e.g., on password change).

        Args:
            user_id: User ID whose tokens should be revoked
            expires_in_seconds: TTL for the blacklist (default 24 hours)
        """
        if self._redis is None:
            logger.warning("Cannot blacklist user tokens - Redis not available")
            return

        try:
            key = f"blacklist:user:{user_id}"
            await self._redis.setex(
                key,
                expires_in_seconds,
                "all_tokens_revoked"
            )
            logger.info(
                "All tokens blacklisted for user",
                user_id=user_id,
                ttl_seconds=expires_in_seconds
            )
        except Exception as error:
            logger.error("Error blacklisting user tokens", error=str(error))

    async def is_user_blacklisted(self, user_id: int) -> bool:
        """
        Check if all tokens for a user are blacklisted.

        Args:
            user_id: User ID to check

        Returns:
            bool: True if user's tokens are blacklisted, False otherwise
        """
        if self._redis is None:
            return False

        try:
            key = f"blacklist:user:{user_id}"
            exists = await self._redis.exists(key)
            return exists > 0
        except Exception as error:
            logger.error("Error checking user blacklist", error=str(error))
            return False


# Global token blacklist instance
token_blacklist = TokenBlacklist()


async def init_token_blacklist():
    """Initialize token blacklist on app startup"""
    await token_blacklist.connect()


async def close_token_blacklist():
    """Close token blacklist on app shutdown"""
    await token_blacklist.disconnect()
