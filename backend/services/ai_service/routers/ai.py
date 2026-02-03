"""AI endpoints: cut-optimize, quote-assistant, OCR invoice, NLQ (stubs)."""
from typing import Annotated, Any

from pydantic import BaseModel
from fastapi import APIRouter, Depends, UploadFile, File

from shared.auth.deps import require_permission
from ..deps import TenantUser

router = APIRouter()


# --- Cut optimize (stub) ---
class CutOptimizeRequest(BaseModel):
    bom_id: str
    stock_length_mm: float = 6000.0
    kerf_mm: float = 3.0


class CutOptimizeResponse(BaseModel):
    job_id: str
    status: str
    utilization_pct: float
    total_cuts: int
    message: str


@router.post("/cut-optimize", response_model=CutOptimizeResponse)
def cut_optimize(
    body: CutOptimizeRequest,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("ai:use"))],
):
    return CutOptimizeResponse(
        job_id=str(__import__("uuid").uuid4()),
        status="completed",
        utilization_pct=93.2,
        total_cuts=12,
        message="Stub: cut optimization completed.",
    )


# --- Quote assistant (stub) ---
class QuoteAssistantRequest(BaseModel):
    rfq_text: str
    context: dict[str, Any] | None = None


class QuoteAssistantResponse(BaseModel):
    suggestion: str
    estimated_lines: list[dict[str, Any]]
    confidence: float


@router.post("/quote-assistant", response_model=QuoteAssistantResponse)
def quote_assistant(
    body: QuoteAssistantRequest,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("ai:use"))],
):
    return QuoteAssistantResponse(
        suggestion="Stub: Add 3 lines for profiles 2400mm, 1800mm, 1200mm.",
        estimated_lines=[
            {"description": "Profile 2400mm", "quantity": 10, "unit": "pcs"},
            {"description": "Profile 1800mm", "quantity": 5, "unit": "pcs"},
        ],
        confidence=0.85,
    )


# --- OCR invoice (stub + file upload) ---
class OcrInvoiceResponse(BaseModel):
    job_id: str
    status: str
    extracted: dict[str, Any]
    message: str


@router.post("/ocr/invoice", response_model=OcrInvoiceResponse)
async def ocr_invoice(
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("ai:use"))],
    file: UploadFile = File(...),
):
    # Stub: accept file but return mock extracted data
    content = await file.read()
    return OcrInvoiceResponse(
        job_id=str(__import__("uuid").uuid4()),
        status="completed",
        extracted={
            "vendor": "Stub Vendor Ltd",
            "invoice_number": "INV-001",
            "total": 1500.00,
            "line_items": [],
        },
        message="Stub: OCR processing completed.",
    )


# --- NLQ (natural language query) (stub) ---
class NLQRequest(BaseModel):
    query: str
    limit: int = 10


class NLQResponse(BaseModel):
    answer: str
    results: list[dict[str, Any]]
    sql_generated: str | None = None


@router.post("/nlq", response_model=NLQResponse)
def nlq(
    body: NLQRequest,
    tenant_user: TenantUser,
    user: Annotated[dict, Depends(require_permission("ai:use"))],
):
    return NLQResponse(
        answer="Stub: No data source connected.",
        results=[],
        sql_generated="SELECT * FROM materials LIMIT 10",
    )
