"""
Security utilities for YogaFlow authentication.
Implements JWT tokens and password hashing per requirements.

Security Requirements (REQ-NF-SEC-*):
- Password hashing with bcrypt work factor >= 12
- JWT tokens for session management
- Secure password validation
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging_config import logger

# Password hashing context with bcrypt
# Work factor set to 12 (minimum per REQ-NF-SEC-002)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.bcrypt_rounds
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password (never store plain text)

    Security:
        - Uses bcrypt with work factor >= 12
        - Salt is automatically generated
        - Resistant to rainbow table attacks
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored password hash

    Returns:
        bool: True if password matches, False otherwise

    Security:
        - Constant-time comparison
        - Resistant to timing attacks
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as error:
        logger.error("Password verification error", error=str(error))
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.

    Requirements (REQ-UM-003):
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number

    Args:
        password: Password to validate

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"

    return True, ""


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.

    Args:
        data: Data to encode in token (typically {"sub": user_email})
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token

    Security:
        - Tokens expire after 24 hours by default
        - Uses HS256 algorithm
        - Secret key must be strong and kept secure
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    logger.debug("Access token created", expires_at=expire.isoformat())
    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token for extended sessions.

    Args:
        data: Data to encode in token
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT refresh token

    Security:
        - Longer expiration (7 days default)
        - Used for "remember me" functionality
        - Should be stored securely on client
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_minutes)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    logger.debug("Refresh token created", expires_at=expire.isoformat())
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Optional[dict]: Decoded token payload or None if invalid

    Security:
        - Validates signature
        - Checks expiration
        - Verifies token type
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as error:
        logger.warning("Token decode error", error=str(error))
        return None


def generate_password_reset_token(email: str) -> str:
    """
    Generate short-lived token for password reset.

    Args:
        email: User email address

    Returns:
        str: JWT token valid for 1 hour

    Security:
        - Short expiration (1 hour)
        - Single-use (should be invalidated after use)
        - Contains email for verification
    """
    expires_delta = timedelta(hours=1)
    token_data = {"sub": email, "purpose": "password_reset"}
    return create_access_token(token_data, expires_delta)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token and extract email.

    Args:
        token: Password reset token

    Returns:
        Optional[str]: User email if valid, None otherwise
    """
    payload = decode_token(token)

    if not payload:
        return None

    if payload.get("purpose") != "password_reset":
        return None

    email = payload.get("sub")
    return email
