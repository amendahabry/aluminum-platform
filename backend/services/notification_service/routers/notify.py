"""Notify: email + WhatsApp (queue), delivery logs."""
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from shared.auth.deps import require_permission
from ..deps import TenantUser

router = APIRouter()

# Stub: delivery logs (in production use DB/Redis)
_delivery_logs: list[dict] = []


class EmailRequest(BaseModel):
    to: str | list[str]
    subject: str
    body: str
    template_id: str | None = None
    template_data: dict | None = None


class WhatsAppRequest(BaseModel):
    to: str
    message: str
    template_id: str | None = None
    template_data: dict | None = None


class QueueResponse(BaseModel):
    job_id: str
    channel: str
    status: str
    message: str


class DeliveryLogEntry(BaseModel):
    id: str
    tenant_id: str
    channel: str
    recipient: str
    status: str
    created_at: str


@router.post("/email", response_model=QueueResponse)
def queue_email(
    body: EmailRequest,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("notifications:write"))],
):
    """Queue email (stub: enqueue and return job_id)."""
    import uuid
    job_id = str(uuid.uuid4())
    to_list = body.to if isinstance(body.to, list) else [body.to]
    for to in to_list:
        _delivery_logs.append({
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_user["tenant_id"],
            "channel": "email",
            "recipient": to,
            "status": "queued",
            "created_at": __import__("datetime").datetime.utcnow().isoformat(),
        })
    return QueueResponse(job_id=job_id, channel="email", status="queued", message="Email queued.")


@router.post("/whatsapp", response_model=QueueResponse)
def queue_whatsapp(
    body: WhatsAppRequest,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("notifications:write"))],
):
    """Queue WhatsApp message (stub)."""
    import uuid
    job_id = str(uuid.uuid4())
    _delivery_logs.append({
        "id": str(uuid.uuid4()),
        "tenant_id": tenant_user["tenant_id"],
        "channel": "whatsapp",
        "recipient": body.to,
        "status": "queued",
        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
    })
    return QueueResponse(job_id=job_id, channel="whatsapp", status="queued", message="WhatsApp message queued.")


@router.get("/logs", response_model=list[DeliveryLogEntry])
def get_logs(
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("notifications:read"))],
    limit: int = 50,
):
    """Return delivery logs for current tenant."""
    tid = tenant_user["tenant_id"]
    tenant_logs = [l for l in _delivery_logs if l.get("tenant_id") == tid][-limit:]
    return [DeliveryLogEntry(**l) for l in reversed(tenant_logs)]
