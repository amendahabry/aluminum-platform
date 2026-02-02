from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from shared.db.session import get_db
from shared.auth.deps import get_current_user
from shared.tenants.middleware import set_tenant_context


def get_db_session():
    return next(get_db())


def require_tenant_and_db(user: Annotated[dict, Depends(get_current_user)]):
    tid = user.get("tenant_id")
    if not tid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenant")
    set_tenant_context(tid)
    return user


DbSession = Annotated[Session, Depends(get_db_session)]
TenantUser = Annotated[dict, Depends(require_tenant_and_db)]
