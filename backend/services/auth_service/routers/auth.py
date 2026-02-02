"""Auth routes: register-tenant, login, refresh, me."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from shared.auth.jwt import create_access_token
from shared.rbac.constants import DEFAULT_ROLE_PERMISSIONS
from ..deps import DbSession, TenantUser, get_db_session
from ..schemas.auth import (
    RegisterTenantRequest,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    TokenResponse,
    MeResponse,
)
from ..services.auth_service import register_tenant, login, refresh_tokens, get_me

router = APIRouter()


@router.post("/register-tenant", response_model=dict)
def register_tenant_endpoint(db: DbSession, body: RegisterTenantRequest):
    """Create a new tenant and first admin user."""
    tenant, user = register_tenant(db, body)
    return {"tenant_id": tenant.id, "user_id": user.id, "message": "Tenant registered. Use /auth/login to sign in."}


@router.post("/login", response_model=LoginResponse)
def login_endpoint(db: DbSession, body: LoginRequest):
    """Login with email/password; optionally pass tenant_slug."""
    user, access_token, refresh_token = login(db, body)
    from shared.auth.jwt import ACCESS_TOKEN_EXPIRE_MINUTES
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=LoginResponse)
def refresh_endpoint(db: DbSession, body: RefreshRequest):
    """Exchange refresh token for new access + refresh tokens."""
    from shared.auth.jwt import ACCESS_TOKEN_EXPIRE_MINUTES
    access_token, refresh_token = refresh_tokens(db, body.refresh_token)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=MeResponse)
def me_endpoint(db: DbSession, user: TenantUser):
    """Return current user info (requires auth)."""
    data = get_me(db, user["sub"], user["tenant_id"])
    return MeResponse(**data)
