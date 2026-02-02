"""Tenant context middleware: set tenant_id from JWT for DB isolation."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from shared.db.session import current_tenant_id


def set_tenant_context(tenant_id: str | None):
    """Set tenant_id in context (e.g. after JWT validation)."""
    token = current_tenant_id.set(tenant_id)
    return token


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware that sets tenant_id from JWT. Run after auth middleware."""

    async def dispatch(self, request: Request, call_next):
        # If state has user (set by auth), use tenant_id from there
        user = getattr(request.state, "user", None)
        if user and isinstance(user, dict):
            set_tenant_context(user.get("tenant_id"))
        else:
            set_tenant_context(None)
        try:
            response = await call_next(request)
            return response
        finally:
            current_tenant_id.set(None)
