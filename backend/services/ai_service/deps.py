from typing import Annotated
from fastapi import Depends, HTTPException, status
from shared.auth.deps import get_current_user
from shared.tenants.middleware import set_tenant_context

def require_tenant(user: Annotated[dict, Depends(get_current_user)]):
    tid = user.get("tenant_id")
    if not tid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenant")
    set_tenant_context(tid)
    return user

TenantUser = Annotated[dict, Depends(require_tenant)]
