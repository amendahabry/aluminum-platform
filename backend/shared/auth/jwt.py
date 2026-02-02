"""JWT creation and verification."""
import os
from datetime import datetime, timedelta
from typing import Any

import jwt
from jwt import PyJWTError

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production-use-long-secret")


def create_access_token(
    subject: str,
    tenant_id: str,
    roles: list[str],
    permissions: list[str],
    extra: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "roles": roles,
        "permissions": permissions,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str, tenant_id: str, jti: str) -> str:
    """Create a long-lived refresh token."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "jti": jti,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and return payload; raises PyJWTError on invalid token."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def verify_token(token: str) -> dict[str, Any] | None:
    """Verify token and return payload or None."""
    try:
        return decode_token(token)
    except PyJWTError:
        return None
