from datetime import datetime, timezone
import pytest

from app.job.freelancer import normalize_freelancer_project


# ===========================================================================
# Normalization Tests for Freelancer.com Projects
# ===========================================================================

def test_normalize_valid_fixed_project():
    """Verify that a standard Freelancer.com fixed-price project is normalized properly."""
    raw = {
        "id": 38912345,
        "title": "Build a Fast Python Scraper",
        "preview_description": "We need a scraper to extract product data.",
        "seo_url": "python/build-fast-python-scraper",
        "type": "fixed",
        "budget": {"minimum": 200.0, "maximum": 500.0},
        "currency": {"code": "USD"},
        "jobs": [{"name": "Python"}, {"name": "Scrapy"}, {"name": "FastAPI"}],
        "submitdate": 1700000000,
    }

    job = normalize_freelancer_project(raw)

    assert job is not None
    assert job.external_id == "38912345"
    assert job.title == "Build a Fast Python Scraper"
    assert job.description == "We need a scraper to extract product data."
    assert job.url == "https://www.freelancer.com/projects/python/build-fast-python-scraper"
    assert job.project_type == "fixed"
    assert job.budget_min == 200.0
    assert job.budget_max == 500.0
    assert job.currency == "USD"
    assert job.skills == ["Python", "Scrapy", "FastAPI"]
    assert job.published_at == datetime.fromtimestamp(1700000000, tz=timezone.utc)


def test_normalize_valid_hourly_project():
    """Verify that an hourly project is mapped to project_type='hourly'."""
    raw = {
        "id": 998877,
        "title": "Hourly DevOps Support",
        "type": "hourly",
        "budget": {"minimum": 30.0, "maximum": 60.0},
        "currency": {"code": "EUR"},
        "jobs": [{"name": "Docker"}, {"name": "Linux"}],
    }

    job = normalize_freelancer_project(raw)

    assert job is not None
    assert job.external_id == "998877"
    assert job.project_type == "hourly"
    assert job.budget_min == 30.0
    assert job.budget_max == 60.0
    assert job.currency == "EUR"
    assert job.skills == ["Docker", "Linux"]
    assert job.url == "https://www.freelancer.com/projects/998877"


def test_normalize_handles_string_budgets_and_timestamps():
    """Verify that string numbers and string timestamps from the API are parsed without crashing."""
    raw = {
        "id": "778899",
        "title": "String Numbers Job",
        "budget": {"minimum": "150.5", "maximum": "350"},
        "submitdate": "1700000000",
    }
    job = normalize_freelancer_project(raw)
    assert job is not None
    assert job.external_id == "778899"
    assert job.budget_min == 150.5
    assert job.budget_max == 350.0
    assert job.published_at == datetime.fromtimestamp(1700000000, tz=timezone.utc)


def test_normalize_missing_title_or_id_returns_none():
    """Verify that malformed records missing an ID or title are safely skipped."""
    assert normalize_freelancer_project({"title": "No ID"}) is None
    assert normalize_freelancer_project({"id": 12345}) is None
    assert normalize_freelancer_project({}) is None


def test_normalize_missing_optional_fields():
    """Verify that missing optional fields (budget, description, skills) default cleanly."""
    raw = {
        "id": 112233,
        "title": "Minimal Job",
    }

    job = normalize_freelancer_project(raw)

    assert job is not None
    assert job.external_id == "112233"
    assert job.title == "Minimal Job"
    assert job.description is None
    assert job.budget_min is None
    assert job.budget_max is None
    assert job.currency == "USD"
    assert job.skills == []
    assert job.published_at is None


def test_normalize_strips_whitespace_from_title():
    """Verify that leading and trailing whitespace are trimmed from the title."""
    raw = {
        "id": 445566,
        "title": "   Python Web Scraping Project   ",
    }
    job = normalize_freelancer_project(raw)
    assert job is not None
    assert job.title == "Python Web Scraping Project"


def test_normalize_ignores_negative_budgets():
    """Verify that invalid negative budget numbers are sanitized to None."""
    raw = {
        "id": 556677,
        "title": "Negative Budget Job",
        "budget": {"minimum": -50.0, "maximum": -10.0},
    }
    job = normalize_freelancer_project(raw)
    assert job is not None
    assert job.budget_min is None
    assert job.budget_max is None

