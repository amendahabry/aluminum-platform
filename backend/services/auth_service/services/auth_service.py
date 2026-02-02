"""Auth business logic: register tenant, login, refresh, me."""
import os
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from shared.db.session import current_tenant_id
from shared.auth.jwt import create_access_token, create_refresh_token, decode_token
from shared.rbac.constants import DEFAULT_ROLE_PERMISSIONS, PERMISSIONS
from ..models import Tenant, User, Role, Permission, UserRole, RefreshToken
from ..services.password import hash_password, verify_password
from ..schemas.auth import RegisterTenantRequest, LoginRequest


def register_tenant(db: Session, body: RegisterTenantRequest) -> tuple[Tenant, User]:
    """Create tenant + first admin user and admin role."""
    # Check slug unique
    if db.query(Tenant).filter(Tenant.slug == body.slug).first():
        raise HTTPException(status_code=400, detail="Tenant slug already exists")

    tenant_id = str(uuid.uuid4())
    tenant = Tenant(
        id=tenant_id,
        name=body.name,
        slug=body.slug,
        is_active=True,
    )
    db.add(tenant)

    # Create admin role for this tenant
    admin_role_id = str(uuid.uuid4())
    admin_role = Role(
        id=admin_role_id,
        tenant_id=tenant_id,
        name="admin",
        description="Tenant administrator",
    )
    db.add(admin_role)

    # Seed all permissions for tenant from shared.rbac
    from sqlalchemy import insert
    from ..models.role import role_permissions
    perm_by_code = {}
    for code in PERMISSIONS:
        perm_id = str(uuid.uuid4())
        db.add(Permission(id=perm_id, tenant_id=tenant_id, code=code, name=code))
        perm_by_code[code] = perm_id
    # Link admin role to all admin permissions
    for code in DEFAULT_ROLE_PERMISSIONS.get("admin", ["admin:*"]):
        pid = perm_by_code.get(code)
        if pid:
            db.execute(insert(role_permissions).values(role_id=admin_role_id, permission_id=pid))

    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        tenant_id=tenant_id,
        email=body.admin_email,
        hashed_password=hash_password(body.admin_password),
        full_name=body.admin_full_name or "Admin",
        is_active=True,
        is_superuser=True,
    )
    db.add(user)

    user_role = UserRole(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        user_id=user_id,
        role_id=admin_role_id,
    )
    db.add(user_role)
    db.commit()
    db.refresh(tenant)
    db.refresh(user)
    return tenant, user


def login(db: Session, body: LoginRequest) -> tuple[User, str, str]:
    """Validate credentials, return user, access_token, refresh_token."""
    # Resolve tenant: by slug or first tenant for email
    tenant = None
    if body.tenant_slug:
        tenant = db.query(Tenant).filter(Tenant.slug == body.tenant_slug, Tenant.is_active == True).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not tenant:
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=403, detail="Tenant inactive")
    if user.tenant_id != tenant.id:
        raise HTTPException(status_code=403, detail="User does not belong to this tenant")
    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    roles, permissions = _get_roles_and_permissions(db, user)
    jti = str(uuid.uuid4())
    access = create_access_token(str(user.id), user.tenant_id, roles, permissions)
    refresh = create_refresh_token(str(user.id), user.tenant_id, jti)

    # Store refresh token
    rt = RefreshToken(
        id=str(uuid.uuid4()),
        tenant_id=user.tenant_id,
        jti=jti,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))),
    )
    db.add(rt)
    db.commit()
    return user, access, refresh


def refresh_tokens(db: Session, refresh_token: str) -> tuple[str, str]:
    """Validate refresh token, return new access_token, refresh_token."""
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    jti = payload.get("jti")
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    if not jti or not user_id or not tenant_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    rt = db.query(RefreshToken).filter(RefreshToken.jti == jti, RefreshToken.tenant_id == tenant_id).first()
    if not rt or rt.revoked or rt.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked")

    user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    roles, permissions = _get_roles_and_permissions(db, user)
    new_access = create_access_token(user_id, tenant_id, roles, permissions)
    new_jti = str(uuid.uuid4())
    new_refresh = create_refresh_token(user_id, tenant_id, new_jti)
    rt.revoked = True
    new_rt = RefreshToken(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        jti=new_jti,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(days=int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))),
    )
    db.add(new_rt)
    db.commit()
    return new_access, new_refresh


def _get_roles_and_permissions(db: Session, user: User) -> tuple[list[str], list[str]]:
    """Return list of role names and permission codes for user."""
    role_names = []
    permission_codes = set()
    user_roles = db.query(UserRole).filter(UserRole.tenant_id == user.tenant_id, UserRole.user_id == user.id).all()
    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            role_names.append(role.name)
            # Permissions for this role
            from sqlalchemy import select
            from ..models.role import role_permissions
            stmt = select(role_permissions.c.permission_id).where(role_permissions.c.role_id == role.id)
            perm_ids = db.execute(stmt).fetchall()
            for (pid,) in perm_ids:
                perm = db.query(Permission).filter(Permission.id == pid).first()
                if perm:
                    permission_codes.add(perm.code)
    if user.is_superuser:
        permission_codes.add("admin:*")
    return role_names, list(permission_codes)


def get_me(db: Session, user_id: str, tenant_id: str) -> dict:
    """Return current user info for /me."""
    user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    roles, permissions = _get_roles_and_permissions(db, user)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "tenant_id": user.tenant_id,
        "tenant_name": tenant.name if tenant else None,
        "roles": roles,
        "permissions": permissions,
        "is_active": user.is_active,
    }
