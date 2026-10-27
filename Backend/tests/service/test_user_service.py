import pytest
from fastapi import HTTPException

from app.schema.user_schema import AddUserSchema
from app.service.user_service import UserService


# ---------------------------------------------------------------------------
# Fixture: Creates a UserService instance wired to the test database
# ---------------------------------------------------------------------------
@pytest.fixture
def user_service(db_session):
    return UserService(db_session)


# ===========================================================================
# 1. User Creation Tests (create_user)
# ===========================================================================

def test_create_user_success(user_service):
    """Verify that a user is successfully created in the database."""
    user_input = AddUserSchema(
        clerk_id="clerk_abc123",
        email="alex@example.com",
        telegram_id=987654
    )

    created_user = user_service.create_user(user_input)

    assert created_user.id is not None
    assert created_user.clerk_id == "clerk_abc123"
    assert created_user.email == "alex@example.com"
    assert created_user.telegram_id == 987654
    assert created_user.is_active is True
    assert created_user.created_at is not None


def test_create_user_duplicate_clerk_id_raises_conflict(user_service):
    """Verify that creating a user with an existing clerk_id raises a 409 Conflict."""
    first_user = AddUserSchema(clerk_id="clerk_same_id", email="user1@example.com")
    second_user = AddUserSchema(clerk_id="clerk_same_id", email="user2@example.com")

    user_service.create_user(first_user)

    with pytest.raises(HTTPException) as exc_info:
        user_service.create_user(second_user)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "User with this clerk_id already exists."


def test_create_user_duplicate_email_raises_conflict(user_service):
    """Verify that creating a user with an existing email raises a 409 Conflict."""
    first_user = AddUserSchema(clerk_id="clerk_001", email="duplicate@example.com")
    second_user = AddUserSchema(clerk_id="clerk_002", email="duplicate@example.com")

    user_service.create_user(first_user)

    with pytest.raises(HTTPException) as exc_info:
        user_service.create_user(second_user)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "User with this email already exists."


# ===========================================================================
# 2. Querying Tests (get_user_by_email & get_user_by_clerk_id)
# ===========================================================================

def test_get_user_by_email_success(user_service):
    """Verify finding an existing user by their email."""
    user_input = AddUserSchema(clerk_id="clerk_query_email", email="findme@example.com")
    user_service.create_user(user_input)

    found_user = user_service.get_user_by_email("findme@example.com")

    assert found_user is not None
    assert found_user.email == "findme@example.com"
    assert found_user.clerk_id == "clerk_query_email"


def test_get_user_by_email_not_found_returns_none(user_service):
    """Verify get_user_by_email returns None if the user does not exist."""
    found_user = user_service.get_user_by_email("nonexistent@example.com")
    assert found_user is None


def test_get_user_by_clerk_id_success(user_service):
    """Verify finding an existing user by their Clerk ID."""
    user_input = AddUserSchema(clerk_id="clerk_target_id", email="clerkuser@example.com")
    user_service.create_user(user_input)

    found_user = user_service.get_user_by_clerk_id("clerk_target_id")

    assert found_user is not None
    assert found_user.clerk_id == "clerk_target_id"


def test_get_user_by_clerk_id_not_found_returns_none(user_service):
    """Verify get_user_by_clerk_id returns None if the Clerk ID does not exist."""
    found_user = user_service.get_user_by_clerk_id("clerk_does_not_exist")
    assert found_user is None
