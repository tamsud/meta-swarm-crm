"""JWT token creation and validation utilities."""

from datetime import datetime, timedelta, timezone

from jose import ExpiredSignatureError, JWTError, jwt

from app.config import get_settings
from app.exceptions import InvalidTokenError, TokenExpiredError


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with the given payload.

    Args:
        data: Dictionary of claims to include in the token payload.
        expires_delta: Optional custom expiration time. If not provided,
            uses ACCESS_TOKEN_EXPIRE_MINUTES from settings.

    Returns:
        Encoded JWT token string.
    """
    settings = get_settings()

    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode["exp"] = expire

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token.

    Args:
        token: The JWT token string to decode.

    Returns:
        Decoded token payload as a dictionary.

    Raises:
        TokenExpiredError: If the token has expired.
        InvalidTokenError: If the token is malformed or signature is invalid.
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except JWTError as exc:
        raise InvalidTokenError() from exc
