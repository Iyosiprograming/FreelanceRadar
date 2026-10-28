import uuid
from unittest.mock import AsyncMock
import pytest
from fastapi import HTTPException

from app.model.user_model import User
from app.schema.filter_schema import AddFilterSchema, UpdateFilterSchema
from app.service.filter_service import FilterService


def run_sync(coro):
    """Executes a coroutine with AsyncMocks synchronously without spawning a background loop."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.save_user_keywords = AsyncMock()
    mock.delete_user_keywords = AsyncMock()
    mock.update_user_keywords = AsyncMock()
    return mock


@pytest.fixture
def filter_service(db_session, mock_redis):
    return FilterService(db_session, redis=mock_redis)


@pytest.fixture
def test_user(db_session):
    user = User(clerk_id="clerk_test_filter_user", email="test_filter@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_add_filter_success(filter_service, test_user, mock_redis):
    """Verify successfully creating a filter for a user and syncing to Redis."""
    filter_data = AddFilterSchema(
        name="Python Backend",
        skills=["Python", "FastAPI"],
        project_type="fixed",
        min_budget=200.0,
        min_hourly_rate=40.0
    )

    created = run_sync(filter_service.add_filter(filter_data, test_user.id))

    assert created.id is not None
    assert created.user_id == test_user.id
    assert created.name == "Python Backend"
    assert created.skills == ["Python", "FastAPI"]
    assert created.project_type == "fixed"
    assert created.min_budget == 200.0
    assert created.min_hourly_rate == 40.0

    # Redis save check
    mock_redis.save_user_keywords.assert_called_once_with(test_user.id, ["Python", "FastAPI"])


def test_add_filter_duplicate_raises_conflict(filter_service, test_user):
    """Verify that adding a second filter for the same user raises 409 Conflict."""
    filter1 = AddFilterSchema(name="Filter 1", skills=["Python"])
    filter2 = AddFilterSchema(name="Filter 2", skills=["JavaScript"])

    run_sync(filter_service.add_filter(filter1, test_user.id))

    with pytest.raises(HTTPException) as exc_info:
        run_sync(filter_service.add_filter(filter2, test_user.id))

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Filter already exists for this user."


def test_get_filter_by_user_id_success(filter_service, test_user):
    """Verify retrieving existing filter by user_id."""
    filter_data = AddFilterSchema(name="My Filter", skills=["Docker"])
    run_sync(filter_service.add_filter(filter_data, test_user.id))

    found = filter_service.get_filter_by_user_id(test_user.id)

    assert found is not None
    assert found.name == "My Filter"
    assert found.skills == ["Docker"]


def test_get_filter_by_user_id_not_found_returns_none(filter_service):
    """Verify get_filter_by_user_id returns None when user has no filter."""
    random_user_id = uuid.uuid4()
    found = filter_service.get_filter_by_user_id(random_user_id)
    assert found is None


def test_update_filter_single_property(filter_service, test_user, mock_redis):
    """Verify updating only a single property leaves all other properties intact."""
    initial = AddFilterSchema(
        name="Initial Filter",
        skills=["Python", "FastAPI"],
        project_type="fixed",
        min_budget=100.0,
        min_hourly_rate=20.0
    )
    run_sync(filter_service.add_filter(initial, test_user.id))

    # Only update min_budget (skills untouched)
    updated = run_sync(filter_service.update_filter(
        UpdateFilterSchema(min_budget=500.0),
        test_user.id
    ))

    assert updated.min_budget == 500.0
    assert updated.name == "Initial Filter"
    assert updated.skills == ["Python", "FastAPI"]
    assert updated.project_type == "fixed"
    assert updated.min_hourly_rate == 20.0

    # Redis should not update keywords since skills weren't modified
    mock_redis.update_user_keywords.assert_not_called()


def test_update_filter_two_properties_with_skills(filter_service, test_user, mock_redis):
    """Verify updating skills syncs old vs new skills in Redis."""
    initial = AddFilterSchema(
        name="My Stack",
        skills=["Python"],
        project_type="fixed",
        min_budget=100.0
    )
    run_sync(filter_service.add_filter(initial, test_user.id))

    # Update skills and project_type
    updated = run_sync(filter_service.update_filter(
        UpdateFilterSchema(skills=["Python", "Django", "Postgres"], project_type="hourly"),
        test_user.id
    ))

    assert updated.skills == ["Python", "Django", "Postgres"]
    assert updated.project_type == "hourly"
    assert updated.name == "My Stack"
    assert updated.min_budget == 100.0

    # Redis should sync old vs new skills
    mock_redis.update_user_keywords.assert_called_once_with(
        test_user.id,
        ["Python"],
        ["Python", "Django", "Postgres"]
    )


def test_update_filter_all_properties(filter_service, test_user, mock_redis):
    """Verify updating all properties."""
    initial = AddFilterSchema(name="Old Name", skills=["Python"])
    run_sync(filter_service.add_filter(initial, test_user.id))

    update_data = UpdateFilterSchema(
        name="New Name",
        skills=["Rust", "Go"],
        project_type="any",
        min_budget=1000.0,
        min_hourly_rate=75.0
    )
    updated = run_sync(filter_service.update_filter(update_data, test_user.id))

    assert updated.name == "New Name"
    assert updated.skills == ["Rust", "Go"]
    assert updated.project_type == "any"
    assert updated.min_budget == 1000.0
    assert updated.min_hourly_rate == 75.0

    mock_redis.update_user_keywords.assert_called_once_with(
        test_user.id,
        ["Python"],
        ["Rust", "Go"]
    )


def test_update_filter_empty_payload_leaves_everything_intact(filter_service, test_user):
    """Verify passing an empty UpdateFilterSchema leaves the filter unchanged."""
    initial = AddFilterSchema(name="Untouched", skills=["Python"])
    run_sync(filter_service.add_filter(initial, test_user.id))

    updated = run_sync(filter_service.update_filter(UpdateFilterSchema(), test_user.id))
    assert updated.name == "Untouched"
    assert updated.skills == ["Python"]


def test_update_filter_not_found_raises_404(filter_service):
    """Verify updating a non-existent filter raises 404."""
    random_user_id = uuid.uuid4()
    update_data = UpdateFilterSchema(name="New Name")

    with pytest.raises(HTTPException) as exc_info:
        run_sync(filter_service.update_filter(update_data, random_user_id))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No filter found for this user."


def test_delete_filter_success(filter_service, test_user, mock_redis):
    """Verify deleting an existing filter and cleaning up Redis."""
    filter_data = AddFilterSchema(name="To Delete", skills=["Python", "FastAPI"])
    run_sync(filter_service.add_filter(filter_data, test_user.id))

    run_sync(filter_service.delete_filter(test_user.id))

    assert filter_service.get_filter_by_user_id(test_user.id) is None
    mock_redis.delete_user_keywords.assert_called_once_with(test_user.id, ["Python", "FastAPI"])


def test_delete_filter_not_found_raises_404(filter_service):
    """Verify deleting a non-existent filter raises 404."""
    random_user_id = uuid.uuid4()

    with pytest.raises(HTTPException) as exc_info:
        run_sync(filter_service.delete_filter(random_user_id))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No filter found for this user."
