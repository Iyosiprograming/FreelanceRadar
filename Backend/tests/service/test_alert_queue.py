import json
import uuid
from unittest.mock import AsyncMock
import pytest

from app.service.alert_queue import AlertQueue, QUEUE_KEY
from app.service.matching_service import MatchResult


def run_sync(coro):
    """Executes a coroutine with AsyncMocks synchronously without spawning an event loop."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.rpush = AsyncMock(return_value=1)
    mock.lpop = AsyncMock(return_value=None)
    mock.blpop = AsyncMock(return_value=None)
    mock.llen = AsyncMock(return_value=0)
    return mock


@pytest.fixture
def sample_match():
    return MatchResult(
        user_id=uuid.uuid4(),
        telegram_id=123456789,
        job_id=uuid.uuid4(),
        title="Build Python Webhook",
        url="https://freelancer.com/projects/123",
        project_type="fixed",
        budget_text="$500 - $1000 USD",
        description_snippet="Looking for a Python dev...",
        match_score=75,
        matched_skills=["python", "fastapi"]
    )


def test_push_alert(mock_redis, sample_match):
    queue = AlertQueue(redis=mock_redis)
    res = run_sync(queue.push_alert(sample_match))
    assert res == 1
    mock_redis.rpush.assert_called_once()
    call_args = mock_redis.rpush.call_args[0]
    assert call_args[0] == QUEUE_KEY
    payload = json.loads(call_args[1])
    assert payload["telegram_id"] == 123456789
    assert payload["match_score"] == 75


def test_push_alerts_multiple(mock_redis, sample_match):
    queue = AlertQueue(redis=mock_redis)
    run_sync(queue.push_alerts([sample_match, sample_match]))
    mock_redis.rpush.assert_called_once()
    assert len(mock_redis.rpush.call_args[0]) == 3  # key, item1, item2


def test_push_alerts_empty_list(mock_redis):
    queue = AlertQueue(redis=mock_redis)
    res = run_sync(queue.push_alerts([]))
    assert res == 0
    mock_redis.rpush.assert_not_called()


def test_pop_alert_empty_queue(mock_redis):
    queue = AlertQueue(redis=mock_redis)
    mock_redis.lpop.return_value = None
    res = run_sync(queue.pop_alert(timeout=0))
    assert res is None


def test_pop_alert_success(mock_redis, sample_match):
    queue = AlertQueue(redis=mock_redis)
    data = {
        "user_id": str(sample_match.user_id),
        "telegram_id": sample_match.telegram_id,
        "job_id": str(sample_match.job_id),
        "title": sample_match.title,
        "match_score": 75
    }
    mock_redis.lpop.return_value = json.dumps(data)

    res = run_sync(queue.pop_alert(timeout=0))
    assert res["telegram_id"] == 123456789
    assert res["match_score"] == 75


def test_pop_alert_blpop(mock_redis):
    queue = AlertQueue(redis=mock_redis)
    data = {"telegram_id": 999}
    mock_redis.blpop.return_value = (QUEUE_KEY, json.dumps(data).encode("utf-8"))

    res = run_sync(queue.pop_alert(timeout=2))
    assert res["telegram_id"] == 999


def test_get_queue_length(mock_redis):
    queue = AlertQueue(redis=mock_redis)
    mock_redis.llen.return_value = 5
    res = run_sync(queue.get_queue_length())
    assert res == 5

