import uuid
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.service.user_service import UserService
from app.service.telegram_service import send_telegram_message

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", summary="Telegram Bot Webhook")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    # Verify secret token if configured
    if settings.TELEGRAM_WEBHOOK_SECRET:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != settings.TELEGRAM_WEBHOOK_SECRET:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram webhook secret token"
            )

    try:
        body = await request.json()
    except Exception:
        return {"ok": True}

    message = body.get("message")
    if not message:
        return {"ok": True}

    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return {"ok": True}

    # Handle /start <user_id>
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1:
            token = parts[1]
            try:
                user_id = uuid.UUID(token)
                user = UserService(db).link_telegram(user_id, chat_id)
                if user:
                    await send_telegram_message(
                        chat_id=chat_id,
                        text="Account linked successfully! You will now receive job alerts here."
                    )
                    return {"ok": True, "status": "linked", "user_id": str(user.id)}
            except ValueError:
                pass

    return {"ok": True}

