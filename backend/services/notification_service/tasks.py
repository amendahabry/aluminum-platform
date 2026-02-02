"""Celery tasks: async notification send (stub), delivery log."""
from celery import shared_task


@shared_task(bind=True)
def send_email_async(self, to: str, subject: str, body: str, tenant_id: str):
    """Stub: enqueue email send; in production send via SMTP/SES."""
    return {"status": "sent", "to": to, "tenant_id": tenant_id}


@shared_task(bind=True)
def send_whatsapp_async(self, to: str, message: str, tenant_id: str):
    """Stub: enqueue WhatsApp; in production use WhatsApp Business API."""
    return {"status": "queued", "to": to, "tenant_id": tenant_id}
