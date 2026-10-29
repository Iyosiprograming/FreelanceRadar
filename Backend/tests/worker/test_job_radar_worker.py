import asyncio
import uuid
from unittest.mock import AsyncMock, patch
import pytest

from app.model.user_model import User
from app.model.filter_model import Filter
from app.schema.job_schema import AddJobSchema
from app.service.alert_queue import AlertQueue
from app.worker.job_radar_worker import run_radar_cycle


def run_sync(coro):
    """Executes a coroutine with AsyncMocks synchronously without spawning an event loop."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


@pytest.fixture
def sample_add_job():
    return AddJobSchema(
        external_id="ext_radar_999",
        title="Python Webhook Developer",
        description="Looking for an experienced Python developer...",
        url="https://www.freelancer.com/projects/ext_radar_999",
        project_type="fixed",
        budget_min=100.0,
        budget_max=500.0,
        currency="USD",
        skills=["python", "fastapi"]
    )


def test_run_radar_cycle_no_jobs_fetched(db_session):
    with patch("app.worker.job_radar_worker.fetch_freelancer_jobs", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = []
        result = run_sync(run_radar_cycle(db=db_session))

    assert result["fetched"] == 0
    assert result["new_jobs"] == 0
    assert result["matches_found"] == 0
    assert result["alerts_sent"] == 0


def test_run_radar_cycle_no_new_jobs(db_session, sample_add_job):
    # Pre-save the job so it is considered a duplicate
    with patch("app.worker.job_radar_worker.fetch_freelancer_jobs", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [sample_add_job]

        with patch("app.service.job_service.JobService.save_bulk_jobs", return_value=[]):
            result = run_sync(run_radar_cycle(db=db_session))

    assert result["fetched"] == 1
    assert result["new_jobs"] == 0
    assert result["matches_found"] == 0
    assert result["alerts_sent"] == 0


def test_run_radar_cycle_full_success(db_session, sample_add_job):
    # 1. Create a user and matching filter in DB
    user = User(clerk_id="clerk_radar_user", email="radar@example.com", telegram_id=888777)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_filter = Filter(
        user_id=user.id,
        name="Backend Filter",
        project_type="any",
        min_budget=50.0,
        skills=["python", "fastapi"]
    )
    db_session.add(user_filter)
    db_session.commit()

    mock_queue = AsyncMock(spec=AlertQueue)
    mock_queue.push_alerts = AsyncMock(return_value=1)

    with patch("app.worker.job_radar_worker.fetch_freelancer_jobs", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [sample_add_job]

        with patch("app.service.matching_service.RedisService.get_users_by_keywords", new_callable=AsyncMock) as mock_redis:
            mock_redis.return_value = {str(user.id)}

            with patch("app.worker.job_radar_worker.process_next_alert", side_effect=[True, False]):
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    result = run_sync(run_radar_cycle(db=db_session, alert_queue=mock_queue))

    assert result["fetched"] == 1
    assert result["new_jobs"] == 1
    assert result["matches_found"] == 1
    assert result["alerts_sent"] == 1
    mock_queue.push_alerts.assert_called_once()
