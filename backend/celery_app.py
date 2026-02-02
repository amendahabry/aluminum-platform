"""Shared Celery app (Redis broker). Used by notification_service and ai_service workers."""
from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "aluminum",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "services.notification_service.tasks",
        "services.ai_service.tasks",
    ],
)
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.timezone = "UTC"
app.conf.enable_utc = True
