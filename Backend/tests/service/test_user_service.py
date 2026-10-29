import uuid
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


# ===========================================================================
# 3. Telegram Account Linking Tests
# ===========================================================================

def test_get_user_by_id_success(user_service):
    user = user_service.create_user(AddUserSchema(clerk_id="clerk_id_test", email="idtest@example.com"))
    found = user_service.get_user_by_id(user.id)
    assert found is not None
    assert found.id == user.id


def test_link_telegram_success(user_service):
    user = user_service.create_user(AddUserSchema(clerk_id="clerk_link_test", email="linktest@example.com"))
    assert user.telegram_id is None

    linked_user = user_service.link_telegram(user.id, 123456789)
    assert linked_user is not None
    assert linked_user.telegram_id == 123456789

    # Verify persisted in database
    refreshed = user_service.get_user_by_id(user.id)
    assert refreshed.telegram_id == 123456789


def test_link_telegram_rejects_transfer_if_telegram_id_already_used(user_service):
    """Verify that a telegram_id already owned by another user cannot be transferred."""
    user1 = user_service.create_user(AddUserSchema(clerk_id="clerk_u1", email="u1@example.com", telegram_id=999888))
    user2 = user_service.create_user(AddUserSchema(clerk_id="clerk_u2", email="u2@example.com"))

    # Attempt to transfer 999888 to user2 is rejected
    result = user_service.link_telegram(user2.id, 999888)
    assert result is None

    # Verify user1 retains telegram_id and user2 remains unlinked
    assert user_service.get_user_by_id(user1.id).telegram_id == 999888
    assert user_service.get_user_by_id(user2.id).telegram_id is None


def test_link_telegram_locked_when_already_linked(user_service):
    """Verify that an account already linked cannot be overwritten by another Telegram account."""
    user = user_service.create_user(AddUserSchema(clerk_id="clerk_locked", email="locked@example.com", telegram_id=111222))

    # An attacker from a different telegram_id tries to link
    result = user_service.link_telegram(user.id, 999999)
    assert result is None

    # Verify original telegram_id remains unchanged
    refreshed = user_service.get_user_by_id(user.id)
    assert refreshed.telegram_id == 111222
