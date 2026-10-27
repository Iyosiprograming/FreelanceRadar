import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.schema.filter_schema import FilterSchema, AddFilterSchema, UpdateFilterSchema


def test_filter_schema_valid_data():
    """Verify FilterSchema parses full filter data correctly."""
    user_id = uuid.uuid4()
    filter_id = uuid.uuid4()

    schema = FilterSchema(
        id=filter_id,
        user_id=user_id,
        name="Backend Engineer",
        skills=["Python", "FastAPI"],
        project_type="any",
        min_budget=100.0,
        min_hourly_rate=25.0,
        created_at=datetime.now(timezone.utc),
    )

    assert schema.id == filter_id
    assert schema.user_id == user_id
    assert schema.name == "Backend Engineer"
    assert schema.skills == ["Python", "FastAPI"]
    assert schema.project_type == "any"
    assert schema.min_budget == 100.0
    assert schema.min_hourly_rate == 25.0


def test_add_filter_schema_defaults():
    """Verify AddFilterSchema has appropriate defaults."""
    schema = AddFilterSchema(name="Simple Filter")

    assert schema.name == "Simple Filter"
    assert schema.skills == []
    assert schema.project_type == "any"
    assert schema.min_budget is None
    assert schema.min_hourly_rate is None


def test_add_filter_schema_negative_budget_fails():
    """Verify AddFilterSchema rejects negative min_budget."""
    with pytest.raises(ValidationError):
        AddFilterSchema(name="Invalid Filter", min_budget=-10.0)


def test_add_filter_schema_negative_hourly_rate_fails():
    """Verify AddFilterSchema rejects negative min_hourly_rate."""
    with pytest.raises(ValidationError):
        AddFilterSchema(name="Invalid Filter", min_hourly_rate=-5.0)


def test_add_filter_schema_invalid_project_type_fails():
    """Verify AddFilterSchema rejects unsupported project types."""
    with pytest.raises(ValidationError):
        AddFilterSchema(name="Invalid Filter", project_type="invalid_type")


def test_update_filter_schema_all_optional():
    """Verify UpdateFilterSchema allows omitting all fields."""
    schema = UpdateFilterSchema()
    dumped = schema.model_dump(exclude_unset=True)
    assert dumped == {}


def test_update_filter_schema_single_property():
    """Verify UpdateFilterSchema allows setting only a single property."""
    schema = UpdateFilterSchema(min_budget=350.0)
    dumped = schema.model_dump(exclude_unset=True)
    assert dumped == {"min_budget": 350.0}


def test_update_filter_schema_validation_still_applies():
    """Verify UpdateFilterSchema still validates constraints on provided fields."""
    with pytest.raises(ValidationError):
        UpdateFilterSchema(min_budget=-50.0)

    with pytest.raises(ValidationError):
        UpdateFilterSchema(project_type="unsupported")
