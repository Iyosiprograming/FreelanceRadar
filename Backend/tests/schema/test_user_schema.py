import pytest
from uuid import UUID
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schema.user_schema import UserSchema, AddUserSchema


# ===========================================================================
# Tests for UserSchema (Full User Data Representation)
# ===========================================================================

def test_user_schema_valid_data():
    """Verify that UserSchema correctly parses valid user data and converts types."""
    user = UserSchema(
        id="123e4567-e89b-12d3-a456-426655440000",
        clerk_id="clerk_abc123",
        email="alex@example.com",
        telegram_id=987654,
        created_at="2023-05-01T12:34:56Z",
        is_active=True
    )

    # Pydantic parses string into UUID and datetime objects
    assert user.id == UUID("123e4567-e89b-12d3-a456-426655440000")
    assert str(user.id) == "123e4567-e89b-12d3-a456-426655440000"
    assert user.clerk_id == "clerk_abc123"
    assert user.email == "alex@example.com"
    assert user.telegram_id == 987654
    assert user.created_at == datetime(2023, 5, 1, 12, 34, 56, tzinfo=timezone.utc)
    assert user.is_active is True


def test_user_schema_invalid_email_format_fails():
    """Verify that an invalid email address raises a ValidationError."""
    with pytest.raises(ValidationError):
        UserSchema(
            id="123e4567-e89b-12d3-a456-426655440000",
            clerk_id="clerk_abc123",
            email="not_a_valid_email",
            telegram_id=987654,
            created_at="2023-05-01T12:34:56Z",
            is_active=True
        )


def test_user_schema_empty_email_fails():
    """Verify that an empty string for email raises a ValidationError."""
    with pytest.raises(ValidationError):
        UserSchema(
            id="123e4567-e89b-12d3-a456-426655440000",
            clerk_id="clerk_abc123",
            email="",
            telegram_id=987654,
            created_at="2023-05-01T12:34:56Z",
            is_active=True
        )


# ===========================================================================
# Tests for AddUserSchema (Input Data for Creating a User)
# ===========================================================================

def test_add_user_schema_valid_with_telegram():
    """Verify AddUserSchema accepts valid data with a telegram_id."""
    data = AddUserSchema(
        clerk_id="clerk_xyz789",
        email="developer@example.com",
        telegram_id=123456
    )

    assert data.clerk_id == "clerk_xyz789"
    assert data.email == "developer@example.com"
    assert data.telegram_id == 123456


def test_add_user_schema_defaults_telegram_to_none():
    """Verify AddUserSchema allows omitting telegram_id and defaults it to None."""
    data = AddUserSchema(
        clerk_id="clerk_xyz789",
        email="developer@example.com"
    )

    assert data.clerk_id == "clerk_xyz789"
    assert data.email == "developer@example.com"
    assert data.telegram_id is None


def test_add_user_schema_invalid_email_fails():
    """Verify AddUserSchema rejects malformed emails upon registration."""
    with pytest.raises(ValidationError):
        AddUserSchema(
            clerk_id="clerk_xyz789",
            email="invalid_email_address"
        )

