"""User CRUD with tenant isolation and RBAC."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser, get_db_session
from ..models import User, UserRole
from ..schemas.users import UserCreate, UserUpdate, UserResponse, UserListResponse
from ..services.password import hash_password
from ..services.auth_service import _get_roles_and_permissions

router = APIRouter()


def _user_to_response(db: Session, user: User) -> UserResponse:
    roles, _ = _get_roles_and_permissions(db, user)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        tenant_id=user.tenant_id,
        roles=roles,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.get("", response_model=UserListResponse)
def list_users(
    db: DbSession,
    user: Annotated[dict, Depends(require_permission("auth:users:read"))],
    tenant_user: TenantUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    tid = tenant_user["tenant_id"]
    q = db.query(User).filter(User.tenant_id == tid)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return UserListResponse(
        items=[_user_to_response(db, u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: DbSession,
    user: Annotated[dict, Depends(require_permission("auth:users:read"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    u = db.query(User).filter(User.id == user_id, User.tenant_id == tid).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_response(db, u)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    db: DbSession,
    body: UserCreate,
    user: Annotated[dict, Depends(require_permission("auth:users:write"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    if db.query(User).filter(User.tenant_id == tid, User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already exists in tenant")
    uid = str(uuid.uuid4())
    u = User(
        id=uid,
        tenant_id=tid,
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return _user_to_response(db, u)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    db: DbSession,
    body: UserUpdate,
    user: Annotated[dict, Depends(require_permission("auth:users:write"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    u = db.query(User).filter(User.id == user_id, User.tenant_id == tid).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if body.full_name is not None:
        u.full_name = body.full_name
    if body.is_active is not None:
        u.is_active = body.is_active
    if body.password is not None:
        u.hashed_password = hash_password(body.password)
    db.commit()
    db.refresh(u)
    return _user_to_response(db, u)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: DbSession,
    user: Annotated[dict, Depends(require_permission("auth:users:write"))],
    tenant_user: TenantUser,
):
    tid = tenant_user["tenant_id"]
    u = db.query(User).filter(User.id == user_id, User.tenant_id == tid).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.tenant_id == tid).delete()
    db.delete(u)
    db.commit()
