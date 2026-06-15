"""Password hashing and JWT utilities."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the *hashed* password."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(
    user_id: int,
    username: str,
    secret: str,
    expire_hours: int = 24,
) -> str:
    """Create a signed HS256 JWT with sub, username, and exp claims."""
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=expire_hours),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(token: str, secret: str) -> dict:
    """Decode and verify a JWT, returning the payload dict.

    Raises:
        jwt.InvalidTokenError: if the token is invalid or expired.
    """
    return jwt.decode(token, secret, algorithms=["HS256"])
