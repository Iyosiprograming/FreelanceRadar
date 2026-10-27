import uuid
import pytest
from sqlalchemy.exc import IntegrityError

from app.model.user_model import User
from app.model.filter_model import Filter


def test_create_filter_success(db_session):
    """Verify that a filter can be created and defaults are set properly."""
    user = User(clerk_id="clerk_filter_user", email="filter_user@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    filter_obj = Filter(
        user_id=user.id,
        name="Python Developer",
        skills=["Python", "FastAPI", "SQLAlchemy"],
        project_type="fixed",
        min_budget=150.0,
        min_hourly_rate=35.0,
    )
    db_session.add(filter_obj)
    db_session.commit()
    db_session.refresh(filter_obj)

    assert filter_obj.id is not None
    assert filter_obj.user_id == user.id
    assert filter_obj.name == "Python Developer"
    assert filter_obj.skills == ["Python", "FastAPI", "SQLAlchemy"]
    assert filter_obj.project_type == "fixed"
    assert filter_obj.min_budget == 150.0
    assert filter_obj.min_hourly_rate == 35.0
    assert filter_obj.created_at is not None


def test_create_filter_duplicate_user_id_fails(db_session):
    """Verify 1-to-1 relationship: user can only have ONE filter."""
    user = User(clerk_id="clerk_multi_filter", email="multi@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    filter1 = Filter(user_id=user.id, name="Filter 1", skills=["Python"])
    filter2 = Filter(user_id=user.id, name="Filter 2", skills=["React"])

    db_session.add(filter1)
    db_session.commit()

    db_session.add(filter2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_create_filter_missing_user_id_fails(db_session):
    """Verify that user_id cannot be null."""
    incomplete_filter = Filter(name="Orphan Filter", skills=["Python"])
    db_session.add(incomplete_filter)
    with pytest.raises(IntegrityError):
        db_session.commit()

