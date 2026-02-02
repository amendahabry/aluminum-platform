from pydantic import BaseModel, EmailStr


class RegisterTenantRequest(BaseModel):
    name: str
    slug: str
    admin_email: EmailStr
    admin_password: str
    admin_full_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_slug: str | None = None  # optional if tenant in subdomain/header


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    tenant_id: str
    tenant_name: str | None
    roles: list[str]
    permissions: list[str]
    is_active: bool
