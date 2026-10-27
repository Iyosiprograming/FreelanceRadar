import pytest
from sqlalchemy.exc import IntegrityError
from app.model.user_model import User


# ---------------------------------------------------------------------------
# Happy Path Test: Verify a user can be created and defaults are populated
# ---------------------------------------------------------------------------
def test_create_user_success(db_session):
    # 1. Arrange: Create user object
    user = User(
        clerk_id="clerk_abc123",
        email="alex@example.com",
        telegram_id=987654
    )

    # 2. Act: Save to database
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 3. Assert: Check all saved and default fields
    assert user.id is not None                      # UUID generated automatically
    assert user.clerk_id == "clerk_abc123"
    assert user.email == "alex@example.com"
    assert user.telegram_id == 987654
    assert user.is_active is True                   # Defaulted to True
    assert user.created_at is not None              # Timestamp generated automatically


# ---------------------------------------------------------------------------
# Error Case: Verify saving without required fields fails (NOT NULL constraint)
# ---------------------------------------------------------------------------
def test_create_user_missing_required_fields_fails(db_session):
    # Missing required 'clerk_id' and 'email'
    incomplete_user = User()

    db_session.add(incomplete_user)

    # Committing incomplete data must raise IntegrityError
    with pytest.raises(IntegrityError):
        db_session.commit()


# ---------------------------------------------------------------------------
# Error Case: Verify duplicate emails are rejected (UNIQUE constraint)
# ---------------------------------------------------------------------------
def test_create_user_duplicate_email_fails(db_session):
    user1 = User(clerk_id="clerk_001", email="duplicate@example.com")
    user2 = User(clerk_id="clerk_002", email="duplicate@example.com")

    db_session.add(user1)
    db_session.commit()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()



