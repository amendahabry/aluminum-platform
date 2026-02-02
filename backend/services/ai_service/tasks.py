"""Celery tasks: OCR parsing stub, nightly forecasting stub."""
from celery import shared_task


@shared_task(bind=True)
def ocr_parse_invoice_async(self, file_path: str, tenant_id: str):
    """Stub: OCR parse invoice file; in production run OCR pipeline."""
    return {"status": "completed", "job_id": self.request.id, "extracted": {}}


@shared_task(bind=True)
def nightly_forecasting_async(self, tenant_id: str):
    """Stub: nightly demand/material forecasting; in production run ML pipeline."""
    return {"status": "completed", "tenant_id": tenant_id}
