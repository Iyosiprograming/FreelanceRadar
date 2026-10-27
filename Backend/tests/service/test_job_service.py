import pytest

from app.schema.job_schema import AddJobSchema
from app.service.job_service import JobService


@pytest.fixture
def job_service(db_session):
    return JobService(db_session)


def make_sample_job(external_id: str = "fl_1001", title: str = "Python Scraper") -> AddJobSchema:
    """Helper factory to create valid AddJobSchema objects for testing."""
    return AddJobSchema(
        external_id=external_id,
        title=title,
        description="Scrape product data from target website",
        url=f"https://www.freelancer.com/projects/{external_id}",
        project_type="fixed",
        budget_min=150.0,
        budget_max=300.0,
        currency="USD",
        skills=["Python", "Scrapy", "FastAPI"],
    )


# ===========================================================================
# 1. Single Job Batch (List with 1 item)
# ===========================================================================

def test_save_bulk_jobs_single_job_success(job_service):
    """Verify that a batch with a single job saves correctly and populates all fields."""
    job_input = make_sample_job(external_id="fl_single_001", title="FastAPI Developer")

    saved_jobs = job_service.save_bulk_jobs([job_input])

    assert len(saved_jobs) == 1
    job = saved_jobs[0]
    assert job.id is not None
    assert job.external_id == "fl_single_001"
    assert job.title == "FastAPI Developer"
    assert job.project_type == "fixed"
    assert job.skills == ["Python", "Scrapy", "FastAPI"]
    assert job.budget_min == 150.0
    assert job.budget_max == 300.0
    assert job.created_at is not None


def test_save_bulk_jobs_single_job_duplicate_returns_empty(job_service):
    """Verify that ingesting an existing single job returns an empty list without re-inserting."""
    job_input = make_sample_job(external_id="fl_single_dup")

    # Initial save
    first_run = job_service.save_bulk_jobs([job_input])
    assert len(first_run) == 1

    # Ingesting the same job again must return empty list
    second_run = job_service.save_bulk_jobs([job_input])
    assert second_run == []


# ===========================================================================
# 2. Multi-Job Batch Ingestion (1 to 50+ items)
# ===========================================================================

def test_save_bulk_jobs_empty_list_returns_empty(job_service):
    """Verify that passing an empty list returns an empty list without database operations."""
    assert job_service.save_bulk_jobs([]) == []


def test_save_bulk_jobs_multiple_new_jobs_success(job_service):
    """Verify that a batch with multiple new jobs commits all of them in one transaction."""
    batch = [
        make_sample_job(external_id="fl_batch_01", title="Job 1"),
        make_sample_job(external_id="fl_batch_02", title="Job 2"),
        make_sample_job(external_id="fl_batch_03", title="Job 3"),
    ]

    saved_jobs = job_service.save_bulk_jobs(batch)

    assert len(saved_jobs) == 3
    saved_ids = {j.external_id for j in saved_jobs}
    assert saved_ids == {"fl_batch_01", "fl_batch_02", "fl_batch_03"}


def test_save_bulk_jobs_filters_out_existing_jobs(job_service):
    """Verify that only brand-new jobs are saved and returned when partial duplicates exist in DB."""
    # Pre-populate DB with fl_existing
    job_service.save_bulk_jobs([make_sample_job(external_id="fl_existing", title="Old Job")])

    # Incoming batch has fl_existing (duplicate) + fl_new_01, fl_new_02 (new)
    incoming_batch = [
        make_sample_job(external_id="fl_existing", title="Old Job Duplicate"),
        make_sample_job(external_id="fl_new_01", title="New Job 1"),
        make_sample_job(external_id="fl_new_02", title="New Job 2"),
    ]

    saved_jobs = job_service.save_bulk_jobs(incoming_batch)

    # Only the 2 new jobs should be saved and returned
    assert len(saved_jobs) == 2
    saved_ids = {j.external_id for j in saved_jobs}
    assert saved_ids == {"fl_new_01", "fl_new_02"}


def test_save_bulk_jobs_all_existing_returns_empty(job_service):
    """Verify that when all incoming jobs already exist in DB, zero writes occur and [] is returned."""
    batch = [
        make_sample_job(external_id="fl_dup_01"),
        make_sample_job(external_id="fl_dup_02"),
    ]
    job_service.save_bulk_jobs(batch)

    # Ingest identical batch
    subsequent_run = job_service.save_bulk_jobs(batch)
    assert subsequent_run == []


def test_save_bulk_jobs_deduplicates_within_same_batch(job_service):
    """Verify that if the incoming batch contains duplicate external_ids, only unique jobs are saved."""
    # Batch with internal duplicates: fl_unique_01 appears twice
    batch = [
        make_sample_job(external_id="fl_unique_01", title="Original"),
        make_sample_job(external_id="fl_unique_01", title="Duplicate In Same Batch"),
        make_sample_job(external_id="fl_unique_02", title="Second Job"),
    ]

    saved_jobs = job_service.save_bulk_jobs(batch)

    assert len(saved_jobs) == 2
    saved_ids = {j.external_id for j in saved_jobs}
    assert saved_ids == {"fl_unique_01", "fl_unique_02"}


# ===========================================================================
# 3. Job Lookup (get_job_by_external_id)
# ===========================================================================

def test_get_job_by_external_id_returns_job_when_exists(job_service):
    """Verify finding an existing job by its Freelancer.com external_id."""
    job_service.save_bulk_jobs([make_sample_job(external_id="fl_lookup_target", title="Target Job")])

    found_job = job_service.get_job_by_external_id("fl_lookup_target")

    assert found_job is not None
    assert found_job.external_id == "fl_lookup_target"
    assert found_job.title == "Target Job"


def test_get_job_by_external_id_returns_none_when_missing(job_service):
    """Verify that querying a non-existent external_id returns None."""
    found_job = job_service.get_job_by_external_id("non_existent_external_id")
    assert found_job is None
