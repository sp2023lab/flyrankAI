from __future__ import annotations

import asyncio, logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.core.config import get_settings
from app.db.models import NotificationJob
from app.db.session import SessionFactory

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("notification-worker")
settings = get_settings()


async def deliver(submission_id):
    if settings.notification_force_fail:
        raise RuntimeError("forced notification failure")
    log.info("confirmation_notification submission_id=%s", submission_id)


async def process_one() -> bool:
    async with SessionFactory() as session:
        async with session.begin():
            job = await session.scalar(
                select(NotificationJob)
                .where(NotificationJob.status == "pending", NotificationJob.next_attempt_at <= datetime.now(timezone.utc))
                .order_by(NotificationJob.created_at)
                .with_for_update(skip_locked=True)
                .limit(1)
            )
            if not job: return False
            job.status = "processing"
            job.attempts += 1
        try:
            await deliver(job.submission_id)
        except Exception as exc:
            async with session.begin():
                job.status = "failed" if job.attempts >= settings.notification_max_attempts else "pending"
                job.last_error = type(exc).__name__
                job.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=min(60, 2 ** job.attempts))
            log.warning("notification_failed job=%s attempts=%s", job.id, job.attempts)
        else:
            async with session.begin():
                job.status = "sent"; job.last_error = None
        return True


async def main():
    while True:
        worked = await process_one()
        if not worked: await asyncio.sleep(settings.notification_poll_interval_seconds)


if __name__ == "__main__": asyncio.run(main())
