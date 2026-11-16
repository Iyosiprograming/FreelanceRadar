import html
from app.core.logger import logger
from app.service.alert_queue import AlertQueue
from app.service.telegram_service import send_telegram_message


def format_job_alert(alert: dict) -> str:
    """Formats a job match into a sleek, clean Telegram HTML message."""
    title = html.escape(alert.get("title", "Untitled Job"))
    budget = html.escape(alert.get("budget_text", "Not specified"))
    snippet = html.escape(alert.get("description_snippet", ""))
    skills_list = alert.get("matched_skills", [])
    skills = html.escape(", ".join(skills_list)) if skills_list else "None specified"
    score = alert.get("match_score", 0)

    lines = [
        f"🎯 <b>New Job Match ({score}% fit)</b>",
        "",
        f"📌 <b>{title}</b>",
        "",
        f"💰 <b>Budget:</b> {budget}",
        f"🛠 <b>Matched Skills:</b> {skills}",
    ]
    if snippet:
        lines.extend(["", f"📝 <i>{snippet}</i>"])

    return "\n".join(lines)


async def send_job_alert(alert: dict) -> bool:
    """Formats and sends a single job alert to the user's Telegram with an inline button."""
    telegram_id = alert.get("telegram_id")
    if not telegram_id:
        logger.warning(f"Alert missing telegram_id: {alert}")
        return False

    message = format_job_alert(alert)
    url = alert.get("url") or "https://www.freelancer.com"
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "👉 View Job on Freelancer", "url": url}
            ]
        ]
    }
    return await send_telegram_message(
        chat_id=telegram_id,
        text=message,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


async def process_next_alert(alert_queue: AlertQueue | None = None, timeout: int = 1) -> bool:
    """
    Pops the next alert from the queue and delivers it to the user.
    Returns True if an alert was successfully delivered, False if queue was empty or send failed.
    """
    queue = alert_queue or AlertQueue()
    alert = await queue.pop_alert(timeout=timeout)
    if not alert:
        return False

    success = await send_job_alert(alert)
    if success:
        logger.info(f"Delivered job alert to Telegram ID {alert.get('telegram_id')}")
    else:
        logger.error(f"Failed to deliver alert to Telegram ID {alert.get('telegram_id')}")
    return success

