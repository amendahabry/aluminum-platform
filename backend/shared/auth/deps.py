"""FastAPI dependencies for JWT auth and RBAC."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from .jwt import verify_token

# Optional: support both Bearer and X-Tenant for gateway
security = HTTPBearer(auto_error=False)
optional_bearer = HTTPBearer(auto_error=False)


def _get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_bearer)],
) -> dict | None:
    if not credentials or credentials.credentials is None:
        return None
    return verify_token(credentials.credentials)


def get_optional_user(
    payload: Annotated[dict | None, Depends(_get_token_payload)],
):
    """Return current user payload from JWT or None if unauthenticated."""
    return payload


def get_current_user(
    payload: Annotated[dict | None, Depends(_get_token_payload)],
):
    """Require valid JWT; raise 401 if missing or invalid."""
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    return payload


def require_permission(permission: str):
    """Dependency factory: require the given permission in JWT."""

    def _check(
        user: Annotated[dict, Depends(get_current_user)],
    ):
        perms = user.get("permissions") or []
        if permission not in perms and "admin:*" not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}",
            )
        return user

    return _check


def require_tenant(user: Annotated[dict, Depends(get_current_user)]):
    """Ensure user has tenant_id (used to set context)."""
    tid = user.get("tenant_id")
    if not tid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenant")
    return user
