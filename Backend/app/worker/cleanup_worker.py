import asyncio
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logger import logger
from app.service.job_service import JobService


def run_cleanup_cycle(db: Session, older_than_hours: int = 24) -> int:
    """
    Executes one cleanup pass, deleting jobs older than `older_than_hours`.
    Returns the count of deleted jobs.
    """
    job_service = JobService(db)
    return job_service.delete_old_jobs(hours=older_than_hours)


async def start_cleanup_worker(interval_seconds: int = 86400, older_than_hours: int = 24):
    """
    Continuous background loop that runs the cleanup cycle every `interval_seconds` (default: 24 hours).
    """
    logger.info(
        f"Starting daily job cleanup worker (interval: {interval_seconds}s, retention: {older_than_hours}h)..."
    )
    while True:
        try:
            with SessionLocal() as db:
                deleted = run_cleanup_cycle(db, older_than_hours=older_than_hours)
                if deleted > 0:
                    logger.info(f"Daily cleanup: removed {deleted} old jobs from database.")
        except asyncio.CancelledError:
            logger.info("Daily job cleanup worker stopped.")
            break
        except Exception as e:
            logger.error(f"Error during daily job cleanup: {e}")

        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Daily job cleanup worker stopped.")
            break
