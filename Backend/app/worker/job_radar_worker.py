import asyncio
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logger import logger
from app.job.freelancer import fetch_freelancer_jobs
from app.service.job_service import JobService
from app.service.matching_service import MatchingService
from app.service.alert_queue import AlertQueue
from app.service.telegram_sender import process_next_alert


async def run_radar_cycle(db: Session, alert_queue: AlertQueue | None = None) -> dict:
    """
    Executes one complete FreelancerRadar cycle:
    1. Fetches latest active projects from Freelancer.com API
    2. Saves new projects in database (skipping duplicates)
    3. Finds all matching users for each new job (>= 50% match score)
    4. Pushes matches to the Redis alert queue
    5. Delivers queued alerts to users via Telegram
    """
    queue = alert_queue or AlertQueue()

    # 1. Fetch latest projects from Freelancer.com
    fetched_jobs = await fetch_freelancer_jobs(limit=50)
    if not fetched_jobs:
        logger.info("Radar cycle: No jobs fetched from Freelancer.com")
        return {"fetched": 0, "new_jobs": 0, "matches_found": 0, "alerts_sent": 0}

    # 2. Save only newly discovered jobs
    job_service = JobService(db)
    new_jobs = job_service.save_bulk_jobs(fetched_jobs)
    if not new_jobs:
        logger.info("Radar cycle: All fetched jobs are already in database.")
        return {"fetched": len(fetched_jobs), "new_jobs": 0, "matches_found": 0, "alerts_sent": 0}

    # 3. Match new jobs against active user filters
    matching_service = MatchingService(db)
    total_matches = 0
    for job in new_jobs:
        matches = await matching_service.find_matches_for_job(job)
        if matches:
            total_matches += len(matches)
            await queue.push_alerts(matches)

    # 4. Drain the alert queue and send Telegram messages
    alerts_sent = 0
    while await process_next_alert(queue, timeout=0):
        alerts_sent += 1
        # Small pause between sends to be gentle with Telegram rate limits
        await asyncio.sleep(0.05)

    logger.info(
        f"Radar cycle complete: {len(fetched_jobs)} fetched, {len(new_jobs)} new, "
        f"{total_matches} matched, {alerts_sent} alerts sent."
    )
    return {
        "fetched": len(fetched_jobs),
        "new_jobs": len(new_jobs),
        "matches_found": total_matches,
        "alerts_sent": alerts_sent,
    }


async def start_radar_worker(interval_seconds: int = 180):
    """
    Continuous background loop that runs the radar cycle every `interval_seconds` (default: 3 minutes).
    """
    logger.info(f"Starting FreelancerRadar background worker (interval: {interval_seconds}s)...")
    while True:
        try:
            with SessionLocal() as db:
                await run_radar_cycle(db)
        except asyncio.CancelledError:
            logger.info("FreelancerRadar background worker stopped.")
            break
        except Exception as e:
            logger.error(f"Error during radar worker cycle: {e}")

        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("FreelancerRadar background worker stopped.")
            break


if __name__ == "__main__":
    asyncio.run(start_radar_worker(interval_seconds=180))

