from unittest.mock import AsyncMock, patch
import pytest

from app.service.alert_queue import AlertQueue
from app.service.telegram_sender import format_job_alert, process_next_alert, send_job_alert


def run_sync(coro):
    """Executes a coroutine with AsyncMocks synchronously without spawning an event loop."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


def test_format_job_alert():
    alert = {
        "title": "Need a <Python & FastAPI> Expert",
        "budget_text": "$500 - $1,000 USD",
        "description_snippet": "Build a fast & scalable API...",
        "matched_skills": ["python", "fastapi"],
        "match_score": 85,
        "url": "https://www.freelancer.com/projects/123"
    }

    formatted = format_job_alert(alert)

    # Check match percentage
    assert "🎯 <b>New Job Match (85% fit)</b>" in formatted
    # Check HTML escaping
    assert "&lt;Python &amp; FastAPI&gt;" in formatted
    assert "fast &amp; scalable" in formatted
    # Check details
    assert "$500 - $1,000 USD" in formatted
    assert "python, fastapi" in formatted
    assert 'href="https://www.freelancer.com/projects/123"' in formatted


def test_format_job_alert_defaults():
    alert = {}
    formatted = format_job_alert(alert)
    assert "Untitled Job" in formatted
    assert "Not specified" in formatted
    assert "None specified" in formatted


def test_send_job_alert_missing_telegram_id():
    res = run_sync(send_job_alert({"title": "Test Job"}))
    assert res is False


def test_send_job_alert_success():
    alert = {
        "telegram_id": 987654,
        "title": "Test Title",
        "match_score": 90
    }

    with patch("app.service.telegram_sender.send_telegram_message", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        res = run_sync(send_job_alert(alert))

    assert res is True
    mock_send.assert_called_once()
    assert mock_send.call_args[0][0] == 987654
    assert "Test Title" in mock_send.call_args[0][1]


def test_process_next_alert_empty_queue():
    mock_queue = AsyncMock(spec=AlertQueue)
    mock_queue.pop_alert.return_value = None

    res = run_sync(process_next_alert(alert_queue=mock_queue))
    assert res is False


def test_process_next_alert_success():
    mock_queue = AsyncMock(spec=AlertQueue)
    mock_queue.pop_alert.return_value = {
        "telegram_id": 112233,
        "title": "Queue Job",
        "match_score": 60
    }

    with patch("app.service.telegram_sender.send_job_alert", new_callable=AsyncMock) as mock_send_job:
        mock_send_job.return_value = True
        res = run_sync(process_next_alert(alert_queue=mock_queue))

    assert res is True
    mock_send_job.assert_called_once()

