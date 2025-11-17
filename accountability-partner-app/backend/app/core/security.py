"""Security utilities for password hashing and verification."""
from passlib.context import CryptContext

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password to hash

    Returns:
        Hashed password string

    Note:
        Bcrypt has a 72-byte limit, so we manually truncate before hashing.
    """
    # Manually truncate to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        plain_password: Plaintext password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise

    Note:
        Truncates password to 72 bytes to match hashing behavior.
    """
    # Manually truncate to 72 bytes to match hashing behavior
    password_bytes = plain_password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)
