from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.core.config import settings
from app.service.telegram_service import send_telegram_message


def run_sync(coro):
    """Executes a coroutine with AsyncMocks synchronously without spawning an event loop."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


def test_send_telegram_message_without_token_returns_false():
    with patch.object(settings, "TELEGRAM_BOT_TOKEN", ""):
        result = run_sync(send_telegram_message(chat_id=12345, text="Hello"))
        assert result is False


def test_send_telegram_message_success_200():
    mock_response = MagicMock(status_code=200)

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post.return_value = mock_response

    with patch.object(settings, "TELEGRAM_BOT_TOKEN", "mock_bot_token"):
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = run_sync(send_telegram_message(chat_id=12345, text="Test message"))

    assert result is True
    mock_client.post.assert_called_once()
    call_args, call_kwargs = mock_client.post.call_args
    assert "https://api.telegram.org/botmock_bot_token/sendMessage" == call_args[0]
    assert call_kwargs["json"]["chat_id"] == 12345
    assert call_kwargs["json"]["text"] == "Test message"


def test_send_telegram_message_api_error_returns_false():
    mock_response = MagicMock(status_code=400, text="Bad Request: chat not found")

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post.return_value = mock_response

    with patch.object(settings, "TELEGRAM_BOT_TOKEN", "mock_bot_token"):
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = run_sync(send_telegram_message(chat_id=12345, text="Test message"))

    assert result is False


def test_send_telegram_message_exception_returns_false():
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post.side_effect = Exception("Connection timed out")

    with patch.object(settings, "TELEGRAM_BOT_TOKEN", "mock_bot_token"):
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = run_sync(send_telegram_message(chat_id=12345, text="Test message"))

    assert result is False

