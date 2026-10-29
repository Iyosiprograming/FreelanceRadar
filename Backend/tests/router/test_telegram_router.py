import uuid
from unittest.mock import AsyncMock, patch
import pytest
from fastapi import HTTPException, Request

from app.core.config import settings
from app.model.user_model import User
from app.router.telegram_router import telegram_webhook


def run_sync(coro):
    """Executes a coroutine with AsyncMocks synchronously without spawning an event loop."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


@pytest.fixture
def test_user(db_session):
    user = User(
        clerk_id="clerk_tg_test",
        email="tguser@example.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def make_request(body: dict, headers: dict | None = None):
    mock = AsyncMock(spec=Request)
    default_headers = {}
    if settings.TELEGRAM_WEBHOOK_SECRET:
        default_headers["X-Telegram-Bot-Api-Secret-Token"] = settings.TELEGRAM_WEBHOOK_SECRET
    if headers:
        default_headers.update(headers)
    mock.headers = default_headers
    mock.json = AsyncMock(return_value=body)
    return mock


def test_webhook_secret_token_unauthorized(db_session):
    with patch.object(settings, "TELEGRAM_WEBHOOK_SECRET", "super_secret"):
        req = make_request({}, headers={"X-Telegram-Bot-Api-Secret-Token": "wrong_token"})
        with pytest.raises(HTTPException) as exc_info:
            run_sync(telegram_webhook(req, db_session))
        assert exc_info.value.status_code == 401


def test_webhook_secret_token_authorized(db_session):
    with patch.object(settings, "TELEGRAM_WEBHOOK_SECRET", "super_secret"):
        req = make_request({}, headers={"X-Telegram-Bot-Api-Secret-Token": "super_secret"})
        res = run_sync(telegram_webhook(req, db_session))
        assert res == {"ok": True}


def test_webhook_ignores_non_message_updates(db_session):
    req = make_request({"update_id": 999, "edited_message": {}})
    res = run_sync(telegram_webhook(req, db_session))
    assert res == {"ok": True}


def test_webhook_links_account_successfully(db_session, test_user):
    chat_id = 987654321
    payload = {
        "message": {
            "chat": {"id": chat_id},
            "text": f"/start {test_user.id}"
        }
    }
    req = make_request(payload)

    with patch("app.router.telegram_router.send_telegram_message", new_callable=AsyncMock) as mock_send:
        res = run_sync(telegram_webhook(req, db_session))

    assert res["status"] == "linked"
    assert res["user_id"] == str(test_user.id)

    # Verify user telegram_id in database
    db_session.refresh(test_user)
    assert test_user.telegram_id == chat_id

    # Verify confirmation message was sent
    mock_send.assert_called_once_with(
        chat_id=chat_id,
        text="Account linked successfully! You will now receive job alerts here."
    )


def test_webhook_start_with_invalid_uuid(db_session):
    payload = {
        "message": {
            "chat": {"id": 12345},
            "text": "/start not-a-uuid"
        }
    }
    req = make_request(payload)

    with patch("app.router.telegram_router.send_telegram_message", new_callable=AsyncMock) as mock_send:
        res = run_sync(telegram_webhook(req, db_session))

    assert res == {"ok": True}
    mock_send.assert_not_called()


def test_webhook_start_with_nonexistent_user(db_session):
    payload = {
        "message": {
            "chat": {"id": 12345},
            "text": f"/start {uuid.uuid4()}"
        }
    }
    req = make_request(payload)

    with patch("app.router.telegram_router.send_telegram_message", new_callable=AsyncMock) as mock_send:
        res = run_sync(telegram_webhook(req, db_session))

    assert res == {"ok": True}
    mock_send.assert_not_called()
