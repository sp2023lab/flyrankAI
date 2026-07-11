import logging

import httpx

from app.config import get_settings
from app.models import AIJob

logger = logging.getLogger(__name__)


def alert_permanent_ai_failure(job: AIJob, error: BaseException) -> None:
    settings = get_settings()
    logger.critical(
        "alert=ai_job_permanently_failed job_id=%s feature=%s attempts=%d "
        "max_attempts=%d error_type=%s",
        job.id,
        job.feature,
        job.attempts,
        job.max_attempts,
        type(error).__name__,
    )

    if not settings.ai_failure_webhook_url:
        return

    try:
        httpx.post(
            settings.ai_failure_webhook_url,
            json={
                "event": "ai_job_permanently_failed",
                "job_id": job.id,
                "feature": job.feature,
                "attempts": job.attempts,
                "max_attempts": job.max_attempts,
                "error_type": type(error).__name__,
            },
            timeout=settings.ai_failure_alert_timeout_seconds,
        ).raise_for_status()
    except httpx.HTTPError:
        logger.exception("ai_failure_alert_delivery_failed job_id=%s", job.id)
