import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.schema.job_schema import JobSchema, AddJobSchema


def test_job_schema_valid_data():
    """Verify JobSchema correctly parses valid job data."""
    job_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    schema = JobSchema(
        id=job_id,
        external_id="proj_12345",
        title="Build Python Web Scraper",
        description="Need a scraper to gather product pricing.",
        url="https://www.freelancer.com/projects/python/build-scraper",
        project_type="fixed",
        budget_min=250.0,
        budget_max=500.0,
        currency="USD",
        skills=["Python", "Scrapy", "BeautifulSoup"],
        published_at=now,
        created_at=now,
    )

    assert schema.id == job_id
    assert schema.external_id == "proj_12345"
    assert schema.title == "Build Python Web Scraper"
    assert schema.description == "Need a scraper to gather product pricing."
    assert schema.url == "https://www.freelancer.com/projects/python/build-scraper"
    assert schema.project_type == "fixed"
    assert schema.budget_min == 250.0
    assert schema.budget_max == 500.0
    assert schema.currency == "USD"
    assert schema.skills == ["Python", "Scrapy", "BeautifulSoup"]
    assert schema.published_at == now
    assert schema.created_at == now


def test_add_job_schema_defaults():
    """Verify AddJobSchema applies appropriate default values."""
    schema = AddJobSchema(
        external_id="proj_67890",
        title="React Frontend Developer",
        url="https://www.freelancer.com/projects/react/frontend",
    )

    assert schema.external_id == "proj_67890"
    assert schema.title == "React Frontend Developer"
    assert schema.url == "https://www.freelancer.com/projects/react/frontend"
    assert schema.project_type == "fixed"
    assert schema.budget_min is None
    assert schema.budget_max is None
    assert schema.currency == "USD"
    assert schema.skills == []
    assert schema.description is None
    assert schema.published_at is None


def test_add_job_schema_hourly_type():
    """Verify AddJobSchema accepts 'hourly' project_type."""
    schema = AddJobSchema(
        external_id="proj_hourly_1",
        title="Hourly DevOps Consultant",
        url="https://www.freelancer.com/projects/devops",
        project_type="hourly",
        budget_min=30.0,
        budget_max=60.0,
    )

    assert schema.project_type == "hourly"
    assert schema.budget_min == 30.0
    assert schema.budget_max == 60.0


def test_add_job_schema_negative_budget_fails():
    """Verify AddJobSchema rejects negative budgets."""
    with pytest.raises(ValidationError):
        AddJobSchema(
            external_id="proj_neg",
            title="Invalid Budget",
            url="https://example.com",
            budget_min=-100.0,
        )


def test_add_job_schema_invalid_project_type_fails():
    """Verify AddJobSchema rejects unsupported project types."""
    with pytest.raises(ValidationError):
        AddJobSchema(
            external_id="proj_inv",
            title="Invalid Type",
            url="https://example.com",
            project_type="contract",
        )

