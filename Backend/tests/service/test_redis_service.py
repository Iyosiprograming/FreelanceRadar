import uuid
from unittest.mock import AsyncMock
import pytest

from app.model.user_model import User
from app.model.filter_model import Filter
from app.service.redis_service import RedisService


def run_sync(coro):
    """Executes a coroutine with AsyncMocks synchronously without spawning an event loop."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.sadd = AsyncMock()
    mock.srem = AsyncMock()
    mock.sunion = AsyncMock(return_value={"user_1", "user_2"})
    mock.flushdb = AsyncMock()
    return mock


@pytest.fixture
def redis_service(mock_redis):
    return RedisService(redis=mock_redis)


# ===========================================================================
# RedisService Unit Tests (Synchronously driven without socket event loops)
# ===========================================================================

def test_save_user_keywords(redis_service, mock_redis):
    """Verify that user_id is added to lowercase skill keys via sadd."""
    user_id = str(uuid.uuid4())
    keywords = ["Python", "FastAPI"]

    run_sync(redis_service.save_user_keywords(user_id, keywords))

    assert mock_redis.sadd.call_count == 2
    mock_redis.sadd.assert_any_call("skill:python", user_id)
    mock_redis.sadd.assert_any_call("skill:fastapi", user_id)


def test_delete_user_keywords(redis_service, mock_redis):
    """Verify that user_id is removed from skill keys via srem."""
    user_id = str(uuid.uuid4())
    keywords = ["Docker"]

    run_sync(redis_service.delete_user_keywords(user_id, keywords))

    mock_redis.srem.assert_called_once_with("skill:docker", user_id)


def test_update_user_keywords(redis_service, mock_redis):
    """Verify update removes old keywords and adds new ones."""
    user_id = str(uuid.uuid4())
    old_keywords = ["Python"]
    new_keywords = ["React"]

    run_sync(redis_service.update_user_keywords(user_id, old_keywords, new_keywords))

    mock_redis.srem.assert_called_once_with("skill:python", user_id)
    mock_redis.sadd.assert_called_once_with("skill:react", user_id)


def test_get_users_by_keywords(redis_service, mock_redis):
    """Verify sunion is called with formatted keys."""
    result = run_sync(redis_service.get_users_by_keywords(["Python", "FastAPI"]))

    assert result == {"user_1", "user_2"}
    mock_redis.sunion.assert_called_once_with("skill:python", "skill:fastapi")


def test_get_users_by_keywords_empty(redis_service, mock_redis):
    """Verify empty input returns empty set without calling Redis."""
    result = run_sync(redis_service.get_users_by_keywords([]))
    assert result == set()
    mock_redis.sunion.assert_not_called()


def test_rebuild_cache_from_db(redis_service, mock_redis, db_session):
    """Verify that rebuild wipes Redis and re-adds all filters from the database."""
    user = User(clerk_id="clerk_redis_test", email="redis@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_filter = Filter(user_id=user.id, name="Dev", skills=["Python", "Postgres"])
    db_session.add(user_filter)
    db_session.commit()

    run_sync(redis_service.rebuild_cache_from_db(db_session))

    # 1. Must flushdb first
    mock_redis.flushdb.assert_called_once()

    # 2. Must re-add both skills for this user
    assert mock_redis.sadd.call_count == 2
    mock_redis.sadd.assert_any_call("skill:python", str(user.id))
    mock_redis.sadd.assert_any_call("skill:postgres", str(user.id))
