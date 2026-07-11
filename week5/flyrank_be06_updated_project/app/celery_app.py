from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "pdf_report_generator",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)

if settings.enable_scheduled_reports:
    celery_app.conf.beat_schedule = {
        "generate-daily-sales-report": {
            "task": "app.tasks.enqueue_scheduled_report",
            "schedule": crontab(
                hour=settings.schedule_hour_utc,
                minute=settings.schedule_minute_utc,
            ),
        }
    }
