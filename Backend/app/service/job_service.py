from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.logger import logger
from app.model.job_model import Job
from app.schema.job_schema import AddJobSchema


class JobService:
    def __init__(self, db: Session):
        self.db = db

    def get_job_by_external_id(self, external_id: str) -> Job | None:
        """Fetch a job by its Freelancer.com project ID."""
        return self.db.scalars(
            select(Job).where(Job.external_id == external_id)
        ).first()

    def save_bulk_jobs(self, jobs_data: list[AddJobSchema]) -> list[Job]:
        """
        Saves any batch from 1 to 50+ jobs:
        - 1 query to check for existing jobs.
        - Automatically skips all duplicates.
        - 1 commit to insert all new jobs.
        - Returns only newly added jobs for radar alerts.
        """
        if not jobs_data:
            return []

        external_ids = [job.external_id for job in jobs_data]

        existing_ids = set(
            self.db.scalars(
                select(Job.external_id).where(Job.external_id.in_(external_ids))
            ).all()
        )

        seen_in_batch = set()
        new_jobs: list[Job] = []
        for job_item in jobs_data:
            if job_item.external_id not in existing_ids and job_item.external_id not in seen_in_batch:
                seen_in_batch.add(job_item.external_id)
                new_jobs.append(Job(**job_item.model_dump()))

        if not new_jobs:
            logger.info("No new jobs to save (all were duplicates).")
            return []

        try:
            self.db.add_all(new_jobs)
            self.db.commit()
            for job in new_jobs:
                self.db.refresh(job)

            logger.info(f"Successfully saved {len(new_jobs)} new jobs.")
            return new_jobs

        except IntegrityError:
            self.db.rollback()
            logger.warning("Concurrency conflict during bulk save. Rolled back cleanly.")
            return []
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk saving jobs: {e}")
            raise