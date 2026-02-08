"""Invoice PDF export stub."""
import io
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from shared.auth.deps import require_permission
from ..deps import DbSession, TenantUser
from ..models import Invoice

router = APIRouter()


@router.get("/{invoice_id}/pdf")
def export_invoice_pdf(
    invoice_id: str,
    db: DbSession,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("orders:invoices:read"))],
):
    tid = tenant_user["tenant_id"]
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.tenant_id == tid).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    content = f"Invoice {invoice.reference or invoice.id}\nTotal: {invoice.total_amount}\nStatus: {invoice.status}\n".encode("utf-8")
    return StreamingResponse(io.BytesIO(content), media_type="application/pdf")
