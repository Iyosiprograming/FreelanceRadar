from typing import Any
import httpx
from app.core.config import settings
from app.core.logger import logger


async def send_telegram_message(
    chat_id: int,
    text: str,
    parse_mode: str | None = "HTML",
    reply_markup: dict[str, Any] | None = None
) -> bool:
    """Sends a Telegram message to a user using the Telegram Bot API."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not configured. Skipping message sending.")
        return False

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                return True
            logger.error(f"Telegram API error ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False

