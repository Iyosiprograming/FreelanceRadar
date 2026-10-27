import pytest
from sqlalchemy.exc import IntegrityError

from app.model.job_model import Job


def test_create_job_success(db_session):
    """Verify Job model saves to DB and populates default values."""
    job = Job(
        external_id="fl_123456",
        title="Python Data Scraper",
        description="Scrape data from real estate site",
        url="https://www.freelancer.com/projects/python/fl-123456",
        project_type="fixed",
        budget_min=100.0,
        budget_max=300.0,
        currency="USD",
        skills=["Python", "Scrapy"],
    )

    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    assert job.id is not None
    assert job.external_id == "fl_123456"
    assert job.title == "Python Data Scraper"
    assert job.skills == ["Python", "Scrapy"]
    assert job.created_at is not None


def test_create_job_duplicate_external_id_fails(db_session):
    """Verify unique constraint on external_id prevents duplicate job ingestion."""
    job1 = Job(
        external_id="duplicate_fl_id",
        title="Job 1",
        url="https://www.freelancer.com/projects/1",
        project_type="fixed",
    )
    job2 = Job(
        external_id="duplicate_fl_id",
        title="Job 2",
        url="https://www.freelancer.com/projects/2",
        project_type="fixed",
    )

    db_session.add(job1)
    db_session.commit()

    db_session.add(job2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_create_job_missing_required_fields_fails(db_session):
    """Verify NOT NULL constraints on title and external_id."""
    incomplete_job = Job(description="Missing required fields")
    db_session.add(incomplete_job)
    with pytest.raises(IntegrityError):
        db_session.commit()

