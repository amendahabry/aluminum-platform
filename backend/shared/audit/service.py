"""Audit log helper: structured log for audit; services with AuditLog table write to DB themselves."""
from typing import Any

from shared.logging_utils import get_logger

logger = get_logger(__name__)


def audit_log(
    tenant_id: str,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Emit structured audit log. Services that persist audit use their own AuditLog model + this."""
    logger.info(
        "audit",
        extra={
            "audit": True,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
        },
    )
