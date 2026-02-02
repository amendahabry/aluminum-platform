"""Structured logging with request ID support."""
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def bind_request_id(request_id: str | None = None) -> str:
    """Set or generate request ID; return it."""
    rid = request_id or str(uuid.uuid4())
    request_id_ctx.set(rid)
    return rid


def get_request_id() -> str:
    return request_id_ctx.get() or ""


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def setup_logging(service_name: str, level: str = "INFO") -> None:
    """Configure structured JSON-like logs and request_id."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    fmt = (
        '{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"'
        + service_name
        + '","request_id":"%(request_id)s","message":"%(message)s"}'
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(request_id)s] %(message)s"))
    root = logging.getLogger()
    root.setLevel(log_level)
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    for handler in root.handlers:
        handler.addFilter(RequestIdFilter())
    # Ensure our logger has request_id attribute
    logging.Logger.manager.loggerDict.get(service_name)
    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not any(isinstance(f, RequestIdFilter) for f in logger.filters):
        logger.addFilter(RequestIdFilter())
    return logger
