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
    url = alert.get("url", "https://www.freelancer.com")

    return (
        f"🎯 <b>New Job Match ({score}% fit)</b>\n\n"
        f"📌 <b>{title}</b>\n"
        f"💰 <b>Budget:</b> {budget}\n"
        f"🛠 <b>Matched Skills:</b> {skills}\n\n"
        f"📝 {snippet}\n\n"
        f'👉 <a href="{url}">View Job on Freelancer</a>'
    )


async def send_job_alert(alert: dict) -> bool:
    """Formats and sends a single job alert to the user's Telegram."""
    telegram_id = alert.get("telegram_id")
    if not telegram_id:
        logger.warning(f"Alert missing telegram_id: {alert}")
        return False

    message = format_job_alert(alert)
    return await send_telegram_message(telegram_id, message)


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

